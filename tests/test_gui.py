from pathlib import Path

import pytest

from memory_export_converter.gui import (
    RunRequest,
    conflicting_outputs,
    open_directory,
    validate_selections,
)


def test_validate_raw_media_only(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    request = validate_selections(str(source), "", str(tmp_path / "output"), "")
    assert request.media_input == source
    assert request.zip_input is None


def test_validate_archives_only(tmp_path: Path) -> None:
    source = tmp_path / "archives"
    source.mkdir()
    request = validate_selections("", str(source), "", str(tmp_path / "merged"))
    assert request.zip_input == source
    assert request.media_input is None


@pytest.mark.parametrize(
    ("values", "message"),
    [
        (("", "", "", ""), "at least one input"),
        (("missing", "", "output", ""), "does not exist"),
    ],
)
def test_validate_rejects_incomplete_selections(
    values: tuple[str, str, str, str], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        validate_selections(*values)


def test_conflicting_outputs_detects_raw_and_archive_results(tmp_path: Path) -> None:
    media = tmp_path / "media"
    archives = tmp_path / "archives"
    photos = tmp_path / "photos"
    merged = tmp_path / "merged"
    for directory in (media, archives, photos, merged):
        directory.mkdir()
    (media / "memory").touch()
    (archives / "snap.zip").touch()
    existing_photo = photos / "memory.jpg"
    existing_video = merged / "snap.mp4"
    existing_photo.touch()
    existing_video.touch()

    request = RunRequest(media, archives, photos, merged)
    assert conflicting_outputs(request) == (existing_photo, existing_video)


@pytest.mark.parametrize(
    ("platform", "command"),
    [
        ("darwin", ["/usr/bin/open", "output"]),
        ("linux", ["xdg-open", "output"]),
    ],
)
def test_open_directory_uses_platform_file_manager(
    monkeypatch: pytest.MonkeyPatch, platform: str, command: list[str]
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr("memory_export_converter.gui.sys.platform", platform)
    monkeypatch.setattr("memory_export_converter.gui.subprocess.Popen", calls.append)

    open_directory(Path("output"))

    assert calls == [command]


def test_open_directory_uses_startfile_on_windows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[Path] = []
    monkeypatch.setattr("memory_export_converter.gui.sys.platform", "win32")
    monkeypatch.setattr(
        "memory_export_converter.gui.os.startfile", calls.append, raising=False
    )

    open_directory(Path("output"))

    assert calls == [Path("output")]
