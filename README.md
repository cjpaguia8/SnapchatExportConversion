# Photo Conversion Tools

A friendly desktop application for recovering exported Snapchat memories and
converting otherwise awkward media files into standard JPEGs. No terminal commands
or separate FFmpeg installation are required when using the Windows release.

## Easiest way to run it on Windows

1. Open the repository's **Releases** page on GitHub.
2. Download `PhotoConversion.exe` from the newest release.
3. Double-click the downloaded application.
4. Select either a raw-media folder, a Snapchat ZIP folder, or both.
5. Select where the converted photos and merged Snapchat media should be saved.
6. Click **Run Conversion**.

Use **Browse** to select an existing location or **New Folder** to create an output
folder. When processing finishes, the application reports the result and provides
buttons that open the output folders.

Windows may show a SmartScreen warning for an unsigned community application. If
you downloaded it from this repository's official Releases page, choose **More
info**, verify the application name, and select **Run anyway**.

## What it does

- Converts every media file in a selected folder to JPEG.
- Extracts batches of Snapchat ZIP exports.
- Composites transparent overlays onto exported images.
- Applies overlays to exported videos.
- Supplies its own FFmpeg binary through `imageio-ffmpeg`.
- Rejects unsafe ZIP paths and reports failures clearly.

The two workflows are independent: users can select either input type or run both
at once. Temporary ZIP extraction files are removed automatically.

## Run the desktop app from source

Python 3.9 or newer is required:

```powershell
git clone <repository-url>
cd PhotoConversion
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
photo-conversion-gui
```

After installation, `RunPhotoConversion.pyw` can also be double-clicked on Windows.
On macOS or Linux, activate the environment with `source .venv/bin/activate`.

## Command-line usage

The original commands remain available for scripting and advanced users.

Convert a directory to JPEG:

```powershell
photo-convert --source-dir "C:\path\to\input" --output-dir "C:\path\to\output"
```

Extract Snapchat exports and merge their overlays:

```powershell
snapchat-unzip --source-dir "C:\path\to\zips" --extract-dir "C:\path\to\extracted" --merged-img-dir "C:\path\to\results"
```

`python PhotoConversion.py` and `python BatchUnzipper.py` remain as compatibility
launchers. Run either command with `--help` for all options.

## Development and packaging

```powershell
python -m pip install -e ".[dev,gui-build]"
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m build
pyinstaller --clean --noconfirm PhotoConversion.spec
```

The Windows executable is written to `dist/PhotoConversion.exe`. Pushing a version
tag such as `v1.1.0` runs the included GitHub Actions workflow and attaches the
executable to the corresponding release.

## Project layout

```text
PhotoConversion/
|-- src/photo_conversion/   # Conversion engine, CLI, and desktop GUI
|-- tests/                  # Automated tests
|-- RunPhotoConversion.pyw  # Double-click source launcher
|-- PhotoConversion.spec    # Standalone Windows build configuration
|-- pyproject.toml          # Dependencies, commands, and tool configuration
`-- README.md
```

Keep personal exports and generated media outside the repository. Common local
input/output directories, virtual environments, caches, IDE files, and builds are
ignored by Git.
