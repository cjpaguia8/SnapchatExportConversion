"""Backward-compatible launcher for the Snapchat archive command."""

from photo_conversion.snapchat import main

if __name__ == "__main__":
    raise SystemExit(main())
