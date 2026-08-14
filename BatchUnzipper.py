"""Backward-compatible launcher for the Snapchat archive command."""

from memory_export_converter.snapchat import main

if __name__ == "__main__":
    raise SystemExit(main())
