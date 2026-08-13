import argparse
import shutil
import subprocess
import zipfile
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Batch unzip and merge Snapchat memory overlays."
    )
    parser.add_argument(
        "--source-dir",
        required=True,
        type=Path,
        help="Directory containing zip files.",
    )
    parser.add_argument(
        "--extract-dir",
        required=True,
        type=Path,
        help="Directory where zip contents will be extracted.",
    )
    parser.add_argument(
        "--merged-img-dir",
        "--merged_img_dir",
        required=True,
        dest="merged_img_dir",
        type=Path,
        help="Directory for merged image and video output files.",
    )
    return parser.parse_args()


def overlay_images(jpg_path, png_path, output_path):
    from PIL import Image

    try:
        base = Image.open(jpg_path).convert("RGBA")
        overlay = Image.open(png_path).convert("RGBA")

        if overlay.size != base.size:
            overlay = overlay.resize(base.size, Image.Resampling.LANCZOS)

        merged = Image.alpha_composite(base, overlay)
        merged.convert("RGB").save(output_path.with_suffix(".jpg"), "JPEG", quality=95)
        print(f"[OK] Merged image saved: {output_path.with_suffix('.jpg').name}")

    except Exception as exc:
        print(f"[ERROR] Error merging images: {exc}")


def overlay_video(vid_path, png_path, output_path):
    output_file = output_path.with_suffix(".mp4")
    cmd = [
        "ffmpeg",
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
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"[OK] Merged video saved: {output_file.name}")
        else:
            print(f"[FAILED] FFmpeg error for {vid_path.name}: {result.stderr}")

    except Exception as exc:
        print(f"[ERROR] Error merging video: {exc}")


def copy_to_dest(source_path, dest_path):
    output_file = dest_path.with_suffix(".jpg")
    try:
        shutil.copy(source_path, output_file)
        print(f"[OK] File copied to {output_file}")
    except FileNotFoundError:
        print(f"[ERROR] File not found: {source_path}")
    except Exception as exc:
        print(f"[ERROR] An error occurred in copy_to_dest: {exc}")


def search_for_images(dir_path):
    main = None
    overlay = None
    main_video = None

    for file_path in Path(dir_path).iterdir():
        if not file_path.is_file():
            continue

        suffix = file_path.suffix.lower()
        if suffix in {".jpg", ".jpeg"}:
            main = file_path
        elif suffix == ".png":
            overlay = file_path
        elif suffix in {".mp4", ".mov"}:
            main_video = file_path

    return main, overlay, main_video


def batch_unzip(input_dir, output_dir, target_img_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    target_img_path = Path(target_img_dir)

    if not input_path.is_dir():
        raise NotADirectoryError(f"Source directory does not exist: {input_path}")

    output_path.mkdir(parents=True, exist_ok=True)
    target_img_path.mkdir(parents=True, exist_ok=True)

    zip_files = sorted(input_path.glob("*.zip"))
    print(f"Found {len(zip_files)} zip files")

    for zip_file in zip_files:
        try:
            extract_folder = output_path / zip_file.stem
            extract_folder.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(zip_file, "r") as zip_ref:
                zip_ref.extractall(extract_folder)

            print(f"[OK] Extracted {zip_file.name} to: {extract_folder}")
            img_path, overlay_path, vid_path = search_for_images(extract_folder)
            output_file_path = target_img_path / zip_file.stem

            if overlay_path is None:
                print(f"[FAILED] No overlay found in {extract_folder}")
                if img_path is not None:
                    copy_to_dest(img_path, output_file_path)
            elif vid_path is not None:
                overlay_video(vid_path, overlay_path, output_file_path)
            elif img_path is not None:
                overlay_images(img_path, overlay_path, output_file_path)
            else:
                print(f"[FAILED] No base image or video found in {extract_folder}")

        except zipfile.BadZipFile:
            print(f"[ERROR] {zip_file.name} is not a valid ZIP file")


def main():
    args = parse_args()
    batch_unzip(args.source_dir, args.extract_dir, args.merged_img_dir)


if __name__ == "__main__":
    main()