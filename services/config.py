# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from services.branding import app_root

CONFIG_PATH = app_root() / "config.json"

# 仅运行偏好；作者/收款等见 services.branding（写死）
DEFAULTS = {
    "src_lang": "英语",
    "tgt_lang": "中文",
    "translate_engine": "auto",
    "deepl_api_key": "",
    "deepl_api_url": "https://api-free.deepl.com/v2/translate",
    "mode_clip": True,
    "mode_screen": True,
    "mode_speak": False,
    "topmost": True,
    "region_interval_sec": 4.0,
    "hf_endpoint": "https://hf-mirror.com",
    "window_geometry": "420x580+100+80",
    "max_chars": 2000,
}


def load_config() -> dict:
    data = deepcopy(DEFAULTS)
    if CONFIG_PATH.exists():
        try:
            raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                data.update({k: raw[k] for k in DEFAULTS if k in raw})
        except Exception:
            pass
    return data


def save_config(data: dict) -> None:
    merged = deepcopy(DEFAULTS)
    merged.update({k: data[k] for k in DEFAULTS if k in data})
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
