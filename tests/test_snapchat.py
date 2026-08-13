import zipfile
from pathlib import Path

import pytest
from PIL import Image

from photo_conversion.snapchat import find_media, overlay_images, safe_extract


def test_overlay_images(tmp_path: Path) -> None:
    base = tmp_path / "base.jpg"
    overlay = tmp_path / "overlay.png"
    Image.new("RGB", (4, 4), "blue").save(base)
    Image.new("RGBA", (4, 4), (255, 0, 0, 128)).save(overlay)

    assert overlay_images(base, overlay, tmp_path / "merged")
    assert (tmp_path / "merged.jpg").is_file()


def test_find_media_is_case_insensitive(tmp_path: Path) -> None:
    for name in ("photo.JPG", "overlay.PNG", "clip.MOV"):
        (tmp_path / name).touch()
    image, overlay, video = find_media(tmp_path)
    assert (image.name, overlay.name, video.name) == (
        "photo.JPG",
        "overlay.PNG",
        "clip.MOV",
    )


def test_safe_extract_rejects_path_traversal(tmp_path: Path) -> None:
    archive_path = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("../outside.txt", "unsafe")
    with zipfile.ZipFile(archive_path) as archive, pytest.raises(ValueError):
        safe_extract(archive, tmp_path / "output")
