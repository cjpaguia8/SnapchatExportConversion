"""Locate the FFmpeg executable supplied by the package or the host system."""

from __future__ import annotations

import shutil
from pathlib import Path


def get_ffmpeg_executable() -> str:
    """Return a usable FFmpeg executable, preferring the packaged binary."""
    try:
        import imageio_ffmpeg

        executable = imageio_ffmpeg.get_ffmpeg_exe()
        if executable and Path(executable).is_file():
            return executable
    except (ImportError, RuntimeError):
        pass

    executable = shutil.which("ffmpeg")
    if executable is None:
        raise RuntimeError(
            "FFmpeg is unavailable. Reinstall the application or install FFmpeg."
        )
    return executable
