"""Backward-compatible launcher for the photo conversion command."""

from photo_conversion.convert import main

if __name__ == "__main__":
    raise SystemExit(main())
