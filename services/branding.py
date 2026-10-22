# -*- coding: utf-8 -*-
"""产品与支持信息（写死，不进可编辑配置）。"""
from __future__ import annotations

import sys
from pathlib import Path

APP_NAME = "翻译飘窗"
APP_VERSION = "1.0.0"
AUTHOR_NAME = "空白"
SUPPORT_NOTE = (
    "本软件免费开源。若愿意支持作者，请使用支付宝扫下方收款码。\n"
    "自愿支持 · 不解锁任何功能。\n"
    "官方收款以本程序内置二维码及仓库 SUPPORT.md 为准。"
)


def app_root() -> Path:
    """源码运行=项目根；打包后=exe 所在目录。"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def resource_root() -> Path:
    """打包资源目录（PyInstaller onedir 的 _MEIPASS 或 _internal）。"""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return app_root()


ROOT = app_root()
DONATE_IMAGE = resource_root() / "assets" / "donate.png"
# 若资源在 _MEIPASS，桌面图标仍可用 exe 旁副本
_ico_res = resource_root() / "assets" / "app.ico"
_png_res = resource_root() / "assets" / "app.png"
_ico_side = app_root() / "assets" / "app.ico"
_png_side = app_root() / "assets" / "app.png"
APP_ICON_ICO = _ico_side if _ico_side.exists() else _ico_res
APP_ICON_PNG = _png_side if _png_side.exists() else _png_res
