from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from snapchat_export_conversion.convert import convert_files


def test_convert_files_builds_ffmpeg_command(tmp_path: Path) -> None:
    source = tmp_path / "source"
    output = tmp_path / "output"
    source.mkdir()
    (source / "memory").write_bytes(b"media")

    with (
        patch(
            "snapchat_export_conversion.convert.get_ffmpeg_executable",
            return_value="ffmpeg",
        ),
        patch(
            "snapchat_export_conversion.convert.subprocess.run",
            return_value=Mock(returncode=0),
        ) as run,
    ):
        summary = convert_files(source, output)

    assert summary.successful == 1
    assert summary.failed == ()
    assert run.call_args.args[0][-1] == str(output / "memory.jpg")


def test_convert_files_rejects_missing_source(tmp_path: Path) -> None:
    with pytest.raises(NotADirectoryError):
        convert_files(tmp_path / "missing", tmp_path / "output")
