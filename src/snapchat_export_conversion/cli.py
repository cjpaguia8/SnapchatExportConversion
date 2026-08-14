"""Unified command-line interface."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from snapchat_export_conversion import convert, snapchat


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="photo-tools")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("convert", parents=[convert.build_parser()], add_help=False)
    subparsers.add_parser("snapchat", parents=[snapchat.build_parser()], add_help=False)
    args = parser.parse_args(argv)

    if args.command == "convert":
        summary = convert.convert_files(args.source_dir, args.output_dir, args.quality)
        return 1 if summary.failed else 0
    failures = snapchat.batch_unzip(
        args.source_dir, args.extract_dir, args.merged_img_dir
    )
    return 1 if failures else 0
