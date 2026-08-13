"""Extract Snapchat memory archives and merge their media overlays."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import zipfile
from collections.abc import Sequence
from pathlib import Path
from typing import Callable

from photo_conversion.ffmpeg import get_ffmpeg_executable

ProgressCallback = Callable[[str], None]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Batch unzip and merge Snapchat memory overlays."
    )
    parser.add_argument("--source-dir", required=True, type=Path)
    parser.add_argument("--extract-dir", required=True, type=Path)
    parser.add_argument(
        "--merged-img-dir",
        "--merged_img_dir",
        required=True,
        dest="merged_img_dir",
        type=Path,
    )
    return parser


def overlay_images(
    jpg_path: Path,
    png_path: Path,
    output_path: Path,
    progress: ProgressCallback | None = None,
) -> bool:
    from PIL import Image

    try:
        with Image.open(jpg_path) as image, Image.open(png_path) as overlay_image:
            base = image.convert("RGBA")
            overlay = overlay_image.convert("RGBA")
            if overlay.size != base.size:
                overlay = overlay.resize(base.size, Image.Resampling.LANCZOS)
            output_file = output_path.with_suffix(".jpg")
            Image.alpha_composite(base, overlay).convert("RGB").save(
                output_file, "JPEG", quality=95
            )
        (progress or print)(f"[OK] Merged image saved: {output_file.name}")
        return True
    except (OSError, ValueError) as exc:
        (progress or print)(f"[ERROR] Error merging images: {exc}")
        return False


def overlay_video(
    vid_path: Path,
    png_path: Path,
    output_path: Path,
    progress: ProgressCallback | None = None,
) -> bool:
    output_file = output_path.with_suffix(".mp4")
    result = subprocess.run(
        [
            get_ffmpeg_executable(),
            "-loglevel",
            "error",
            "-i",
            str(vid_path),
            "-i",
            str(png_path),
            "-filter_complex",
            "[1:v]scale=720:1280,format=rgba[ovr];[0:v][ovr]overlay=0:0",
            "-c:a",
            "copy",
            "-y",
            str(output_file),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        (progress or print)(f"[OK] Merged video saved: {output_file.name}")
        return True
    (progress or print)(
        f"[FAILED] FFmpeg error for {vid_path.name}: {result.stderr.strip()}"
    )
    return False


def copy_to_dest(
    source_path: Path,
    dest_path: Path,
    progress: ProgressCallback | None = None,
) -> bool:
    output_file = dest_path.with_suffix(".jpg")
    try:
        shutil.copy2(source_path, output_file)
        (progress or print)(f"[OK] File copied to {output_file}")
        return True
    except OSError as exc:
        (progress or print)(f"[ERROR] Could not copy {source_path}: {exc}")
        return False


def find_media(directory: Path) -> tuple[Path | None, Path | None, Path | None]:
    image = overlay = video = None
    for file_path in sorted(directory.iterdir()):
        if not file_path.is_file():
            continue
        suffix = file_path.suffix.lower()
        if suffix in {".jpg", ".jpeg"}:
            image = file_path
        elif suffix == ".png":
            overlay = file_path
        elif suffix in {".mp4", ".mov"}:
            video = file_path
    return image, overlay, video


def safe_extract(archive: zipfile.ZipFile, destination: Path) -> None:
    """Extract an archive after rejecting paths outside the destination."""
    root = destination.resolve()
    for member in archive.infolist():
        target = (destination / member.filename).resolve()
        if target != root and root not in target.parents:
            raise ValueError(f"Unsafe path in ZIP archive: {member.filename}")
    archive.extractall(destination)


def batch_unzip(
    input_dir: Path | str,
    output_dir: Path | str,
    target_dir: Path | str,
    *,
    progress: ProgressCallback | None = None,
) -> int:
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    target_path = Path(target_dir)
    if not input_path.is_dir():
        raise NotADirectoryError(f"Source directory does not exist: {input_path}")

    output_path.mkdir(parents=True, exist_ok=True)
    target_path.mkdir(parents=True, exist_ok=True)
    zip_files = sorted(input_path.glob("*.zip"))
    report = progress or print
    report(f"Found {len(zip_files)} zip files")
    failures = 0

    for index, zip_file in enumerate(zip_files, start=1):
        extract_folder = output_path / zip_file.stem
        extract_folder.mkdir(parents=True, exist_ok=True)
        try:
            with zipfile.ZipFile(zip_file) as archive:
                safe_extract(archive, extract_folder)
            report(f"[OK {index}/{len(zip_files)}] Extracted {zip_file.name}")
            image, overlay, video = find_media(extract_folder)
            destination = target_path / zip_file.stem
            if overlay is None and image is not None:
                succeeded = copy_to_dest(image, destination, report)
            elif overlay is not None and video is not None:
                succeeded = overlay_video(video, overlay, destination, report)
            elif overlay is not None and image is not None:
                succeeded = overlay_images(image, overlay, destination, report)
            else:
                report(f"[FAILED] No usable media found in {extract_folder}")
                succeeded = False
            failures += not succeeded
        except (zipfile.BadZipFile, ValueError, OSError) as exc:
            report(f"[ERROR] Could not process {zip_file.name}: {exc}")
            failures += 1
    return failures


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        failures = batch_unzip(args.source_dir, args.extract_dir, args.merged_img_dir)
    except NotADirectoryError as exc:
        print(f"Error: {exc}")
        return 2
    return 1 if failures else 0
