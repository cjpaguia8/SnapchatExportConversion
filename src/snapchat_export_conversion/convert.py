"""Convert every file in a directory to JPEG with FFmpeg."""

from __future__ import annotations

import argparse
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from snapchat_export_conversion.ffmpeg import get_ffmpeg_executable

ProgressCallback = Callable[[str], None]


@dataclass(frozen=True)
class ConversionSummary:
    """Result counts and failed filenames from a conversion run."""

    total: int
    successful: int
    failed: tuple[str, ...]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert a folder of media files to JPEG images with FFmpeg."
    )
    parser.add_argument("--source-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument(
        "--quality",
        default=2,
        type=int,
        choices=range(2, 32),
        metavar="2-31",
        help="FFmpeg JPEG quality (lower is better; default: 2).",
    )
    return parser


def convert_files(
    source_dir: Path | str,
    output_dir: Path | str,
    quality: int = 2,
    *,
    progress: ProgressCallback | None = None,
    overwrite: bool = True,
) -> ConversionSummary:
    source_path = Path(source_dir)
    destination = Path(output_dir)
    if not source_path.is_dir():
        raise NotADirectoryError(f"Source directory does not exist: {source_path}")
    if not 2 <= quality <= 31:
        raise ValueError("quality must be between 2 and 31")
    ffmpeg = get_ffmpeg_executable()

    destination.mkdir(parents=True, exist_ok=True)
    files = sorted(path for path in source_path.iterdir() if path.is_file())
    report = progress or print
    report(f"Found {len(files)} files to convert")
    report(f"Output folder: {destination}")
    failed: list[str] = []

    for index, input_path in enumerate(files, start=1):
        output_path = destination / f"{input_path.stem}.jpg"
        if output_path.exists() and not overwrite:
            report(f"[SKIPPED {index}/{len(files)}] Already exists: {output_path.name}")
            failed.append(input_path.name)
            continue
        result = subprocess.run(
            [
                ffmpeg,
                "-loglevel",
                "error",
                "-i",
                str(input_path),
                "-q:v",
                str(quality),
                "-y",
                str(output_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            report(f"[OK {index}/{len(files)}] Converted: {input_path.name}")
        else:
            report(
                f"[FAILED {index}/{len(files)}] {input_path.name}: "
                f"{result.stderr.strip()}"
            )
            failed.append(input_path.name)

    if failed:
        write_failure_log(destination, failed)
    summary = ConversionSummary(len(files), len(files) - len(failed), tuple(failed))
    if progress is None:
        print_summary(summary)
    return summary


def write_failure_log(output_dir: Path, failed_files: Sequence[str]) -> Path:
    log_path = output_dir / "failed_conversions_log.txt"
    with log_path.open("w", encoding="utf-8") as log_file:
        log_file.write("Failed File Conversions\n")
        log_file.write("=" * 50 + "\n")
        log_file.write(f"Date: {datetime.now():%Y-%m-%d %H:%M:%S}\n")
        log_file.write(f"Total failed: {len(failed_files)}\n\nFailed files:\n")
        for filename in failed_files:
            log_file.write(f"  - {filename}\n")
    print(f"\nLog file created: {log_path}")
    return log_path


def print_summary(summary: ConversionSummary) -> None:
    print(f"\n{'=' * 50}\nConversion complete!")
    print(f"Successful: {summary.successful}")
    print(f"Failed: {len(summary.failed)}")
    print(f"Total: {summary.total}\n{'=' * 50}")


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        summary = convert_files(args.source_dir, args.output_dir, args.quality)
    except (NotADirectoryError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}")
        return 2
    return 1 if summary.failed else 0
