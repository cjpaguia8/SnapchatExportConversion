import argparse
import subprocess
from datetime import datetime
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert a folder of media files to JPEG images with ffmpeg."
    )
    parser.add_argument(
        "--source-dir",
        required=True,
        type=Path,
        help="Directory containing files to convert.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory where converted JPEG files will be written.",
    )
    parser.add_argument(
        "--quality",
        default=2,
        type=int,
        help="ffmpeg JPEG quality value. Lower is better; valid range is usually 2-31.",
    )
    return parser.parse_args()


def convert_files(source_dir, output_dir, quality):
    source_dir = Path(source_dir)
    output_dir = Path(output_dir)

    if not source_dir.is_dir():
        raise NotADirectoryError(f"Source directory does not exist: {source_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(path for path in source_dir.iterdir() if path.is_file())
    print(f"Found {len(files)} files to convert")
    print(f"Output folder: {output_dir}\n")

    success_count = 0
    failed_files = []

    for input_path in files:
        output_path = output_dir / f"{input_path.name}.jpg"

        try:
            result = subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    str(input_path),
                    "-q:v",
                    str(quality),
                    "-y",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print(f"[OK] Converted: {input_path.name}")
                success_count += 1
            else:
                print(f"[FAILED] {input_path.name}")
                failed_files.append(input_path.name)

        except Exception as exc:
            print(f"[ERROR] {input_path.name}: {exc}")
            failed_files.append(input_path.name)

    if failed_files:
        write_failure_log(output_dir, failed_files)
    else:
        print("\nAll files converted successfully - no log file needed.")

    print_summary(success_count, len(failed_files), len(files))


def write_failure_log(output_dir, failed_files):
    log_path = output_dir / "failed_conversions_log.txt"
    with log_path.open("w", encoding="utf-8") as log_file:
        log_file.write("Failed File Conversions\n")
        log_file.write("=" * 50 + "\n")
        log_file.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"Total failed: {len(failed_files)}\n\n")
        log_file.write("Failed files:\n")
        for failed_file in failed_files:
            log_file.write(f"  - {failed_file}\n")

    print(f"\nLog file created: {log_path}")


def print_summary(success_count, error_count, total_count):
    print(f"\n{'=' * 50}")
    print("Conversion complete!")
    print(f"Successful: {success_count}")
    print(f"Failed: {error_count}")
    print(f"Total: {total_count}")
    print(f"{'=' * 50}")


def main():
    args = parse_args()
    convert_files(args.source_dir, args.output_dir, args.quality)


if __name__ == "__main__":
    main()
