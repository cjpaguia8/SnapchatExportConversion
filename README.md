# Photo Conversion Tools

Small Python scripts for recovering and processing exported Snapchat memory files.

## Scripts

- `PhotoConversion.py` converts files in a folder to JPEG images using `ffmpeg`.
- `BatchUnzipper.py` extracts Snapchat memory zip files, merges image/video overlays, and writes the merged output to a target folder.

## Requirements

- Python 3.9 or newer
- `ffmpeg` installed and available on your `PATH`
- Python dependencies from `requirements.txt`

Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

Check that `ffmpeg` is available:

```powershell
ffmpeg -version
```

## Convert Files to JPEG

```powershell
python PhotoConversion.py --source-dir "C:\path\to\NoExtension Files" --output-dir "C:\path\to\RecoveredJPEG Files"
```

Optional JPEG quality:

```powershell
python PhotoConversion.py --source-dir "C:\path\to\input" --output-dir "C:\path\to\output" --quality 2
```

Lower `--quality` values produce higher quality JPEGs. A value of `2` is the default.

## Unzip and Merge Overlays

```powershell
python BatchUnzipper.py --source-dir "C:\path\to\Compressed Files" --extract-dir "C:\path\to\Uncompressed Files" --merged-img-dir "C:\path\to\Composite Files"
```

The script also accepts the old `--merged_img_dir` argument name for compatibility.

## Notes

- Output folders are created automatically if they do not exist.
- Generated files, logs, virtual environments, Python caches, and PyCharm project files are ignored by git.
- Keep personal media exports outside the repository unless you intentionally want to publish them.
