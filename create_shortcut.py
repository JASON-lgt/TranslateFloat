# -*- coding: utf-8 -*-
"""在桌面创建无黑窗、带图标的快捷方式（优先用短路径，避免中文路径问题）。"""
from __future__ import annotations

import sys
from pathlib import Path


def short_path(path: Path) -> str:
    try:
        import ctypes
        from ctypes import wintypes

        GetShortPathNameW = ctypes.windll.kernel32.GetShortPathNameW
        GetShortPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
        GetShortPathNameW.restype = wintypes.DWORD
        buf = ctypes.create_unicode_buffer(260)
        if GetShortPathNameW(str(path), buf, 260):
            return buf.value
    except Exception:
        pass
    return str(path)


def main() -> int:
    app_dir = Path(__file__).resolve().parent
    pyw = app_dir / ".venv" / "Scripts" / "pythonw.exe"
    main_py = app_dir / "main.py"
    ico = app_dir / "assets" / "app.ico"
    if not pyw.exists():
        print("missing", pyw)
        return 1

    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        desktop = Path.home() / "桌面"

    import win32com.client  # type: ignore

    names = ["TranslateFloat.lnk", "翻译飘窗.lnk"]
    for name in names:
        lnk = desktop / name
        shell = win32com.client.Dispatch("WScript.Shell")
        sc = shell.CreateShortCut(str(lnk))
        sc.Targetpath = short_path(pyw)
        sc.Arguments = f'-s "{short_path(main_py)}"'
        sc.WorkingDirectory = short_path(app_dir)
        sc.WindowStyle = 1
        sc.Description = "翻译飘窗"
        if ico.exists():
            sc.IconLocation = f"{short_path(ico)},0"
        sc.save()
        print("OK", lnk)

    # ASCII fallback bat
    bat = desktop / "TranslateFloat.bat"
    bat.write_text(
        f'@echo off\r\nstart "" "{short_path(pyw)}" -s "{short_path(main_py)}"\r\n',
        encoding="ascii",
        errors="ignore",
    )
    print("OK", bat)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ImportError:
        # no pywin32: fall back to WScript via cscript
        app_dir = Path(__file__).resolve().parent
        pyw = short_path(app_dir / ".venv" / "Scripts" / "pythonw.exe")
        main_py = short_path(app_dir / "main.py")
        ico = short_path(app_dir / "assets" / "app.ico")
        desktop = Path.home() / "Desktop"
        lnk = desktop / "TranslateFloat.lnk"
        vbs = app_dir / "_mk_shortcut.vbs"
        vbs.write_text(
            "\r\n".join(
                [
                    'Set sh = CreateObject("WScript.Shell")',
                    f'Set sc = sh.CreateShortcut("{lnk}")',
                    f'sc.TargetPath = "{pyw}"',
                    f'sc.Arguments = "-s {main_py}"',
                    f'sc.WorkingDirectory = "{short_path(app_dir)}"',
                    f'sc.IconLocation = "{ico},0"',
                    "sc.Save",
                ]
            )
            + "\r\n",
            encoding="utf-8",
        )
        import subprocess

        subprocess.run(["cscript", "//nologo", str(vbs)], check=False)
        vbs.unlink(missing_ok=True)
        print("OK", lnk)
