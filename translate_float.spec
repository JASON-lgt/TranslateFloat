# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller onedir 规格：翻译飘窗。"""
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_data_files

ROOT = Path(SPECPATH)

datas = [
    (str(ROOT / "assets" / "donate.png"), "assets"),
    (str(ROOT / "assets" / "app.ico"), "assets"),
    (str(ROOT / "assets" / "app.png"), "assets"),
    (str(ROOT / "使用说明.txt"), "."),
    (str(ROOT / "SUPPORT.md"), "."),
]

hiddenimports = [
    "PIL._tkinter_finder",
    "services",
    "services.branding",
    "services.config",
    "services.translate",
    "services.ocr",
    "services.capture",
    "services.stt",
    "services.tts",
    "services.langs",
    "ui",
    "ui.main_window",
    "ui.settings_dialog",
]

binaries = []

for pkg in ("rapidocr_onnxruntime", "onnxruntime", "faster_whisper", "ctranslate2", "av"):
    try:
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception:
        pass

try:
    datas += collect_data_files("certifi")
except Exception:
    pass

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "gradio",
        "torch",
        "torchaudio",
        "torchvision",
        "tensorflow",
        "matplotlib",
        "IPython",
        "notebook",
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="TranslateFloat",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    icon=str(ROOT / "assets" / "app.ico"),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="TranslateFloat",
)
