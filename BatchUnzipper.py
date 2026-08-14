"""Backward-compatible launcher for the Snapchat archive command."""

from snapchat_export_conversion.snapchat import main

if __name__ == "__main__":
    raise SystemExit(main())
