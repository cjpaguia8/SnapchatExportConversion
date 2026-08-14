# Memory Export Converter

A friendly desktop application for recovering exported Snapchat memories and
converting otherwise awkward media files into standard JPEGs. No terminal commands
or separate FFmpeg installation are required when using a desktop release.

## Easiest way to run it on Windows

1. Open the repository's **Releases** page on GitHub.
2. Download `MemoryExportConverter.exe` from the newest release.
3. Double-click the downloaded application.
4. Select either a raw-media folder, a Snapchat ZIP folder, or both.
5. Select where the converted photos and merged Snapchat media should be saved.
6. Click **Run Conversion**.

Use **Browse** to select a location; you can create a new output folder from the
folder selection window. When processing finishes, the application reports the
result and provides buttons that open the output folders.

Windows may show a SmartScreen warning for an unsigned community application. If
you downloaded it from this repository's official Releases page, choose **More
info**, verify the application name, and select **Run anyway**.

## Easiest way to run it on macOS

The packaged macOS application supports macOS 15 or newer. Download the file that
matches your Mac:

- Apple Silicon (M1, M2, M3, M4, or newer):
  `MemoryExportConverter-macOS-arm64.zip`
- Intel processor: `MemoryExportConverter-macOS-x86_64.zip`

Extract the ZIP, then drag **Memory Export Converter.app** into **Applications**.
Because the initial macOS releases use free ad-hoc signing rather than a paid
Apple Developer ID, Gatekeeper may block the first launch. Control-click the app,
choose **Open**, and confirm **Open**. If that option is unavailable, try opening
the app once and then use **System Settings > Privacy & Security > Open Anyway**.

The macOS release supplies FFmpeg and does not require Python or a separate FFmpeg
installation.

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
cd MemoryExportConverter
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
memory-export-converter-gui
```

After installation, `RunMemoryExportConverter.pyw` can also be double-clicked
on Windows.
On macOS or Linux, activate the environment with `source .venv/bin/activate`.

## Verify a release download

Each packaged download has a matching SHA-256 file. On macOS, verify the ZIP with:

```bash
shasum -a 256 MemoryExportConverter-macOS-arm64.zip
cat MemoryExportConverter-macOS-arm64.sha256
```

The two hashes must match. Replace `arm64` with `x86_64` when verifying the Intel
download. With GitHub CLI installed, you can also verify that GitHub Actions built
the archive from this repository:

```bash
gh attestation verify MemoryExportConverter-macOS-arm64.zip \
  --repo cjpaguia8/MemoryExportConverter
```

## Command-line usage

The original commands remain available for scripting and advanced users.

Convert a directory to JPEG:

```powershell
memory-convert --source-dir "C:\path\to\input" --output-dir "C:\path\to\output"
```

Extract Snapchat exports and merge their overlays:

```powershell
memory-unzip --source-dir "C:\path\to\zips" --extract-dir "C:\path\to\extracted" --merged-img-dir "C:\path\to\results"
```

`python MemoryExportConverter.py` and `python BatchUnzipper.py` are also
available as launchers. Run either command with `--help` for all options.

## Development and packaging

```powershell
python -m pip install -e ".[dev,gui-build]"
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m build
pyinstaller --clean --noconfirm MemoryExportConverter.spec
```

The Windows executable is written to `dist/MemoryExportConverter.exe`. On macOS,
build the application bundle with:

```bash
pyinstaller --clean --noconfirm MemoryExportConverter-macOS.spec
```

Pushing a version tag such as `v1.2.0` runs the Windows and macOS GitHub Actions
workflows. The corresponding release receives the Windows executable plus native
macOS ZIPs for Apple Silicon and Intel, together with checksums and build
attestations.

## Project layout

```text
MemoryExportConverter/
|-- src/memory_export_converter/ # Conversion engine, CLI, and desktop GUI
|-- tests/                  # Automated tests
|-- RunMemoryExportConverter.pyw # Double-click source launcher
|-- MemoryExportConverter.spec   # Standalone Windows build configuration
|-- MemoryExportConverter-macOS.spec # macOS application bundle configuration
|-- pyproject.toml          # Dependencies, commands, and tool configuration
`-- README.md
```

Keep personal exports and generated media outside the repository. Common local
input/output directories, virtual environments, caches, IDE files, and builds are
ignored by Git.

## License and trademark notice

This project is open-source software licensed under the [MIT License](LICENSE).

This is an independent, unofficial project. It is not affiliated with, endorsed
by, sponsored by, or otherwise associated with Snap Inc. or Snapchat. Snapchat is
a trademark of Snap Inc. This project's use of the name is solely an informational
reference to describe compatibility with user-provided Snapchat export files.
