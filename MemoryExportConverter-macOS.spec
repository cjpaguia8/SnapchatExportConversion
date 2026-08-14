# PyInstaller build specification for the native macOS GUI application.

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files("imageio_ffmpeg")

analysis = Analysis(
    ["RunMemoryExportConverter.pyw"],
    pathex=["src"],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(analysis.pure)

executable = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="MemoryExportConverter",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    codesign_identity=None,
    entitlements_file=None,
)

application = BUNDLE(
    executable,
    name="Memory Export Converter.app",
    bundle_identifier="io.github.cjpaguia8.memory-export-converter",
    info_plist={"NSHighResolutionCapable": True},
)
