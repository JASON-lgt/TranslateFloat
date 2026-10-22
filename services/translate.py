# -*- coding: utf-8 -*-
from __future__ import annotations

import translators as ts

from services.config import load_config
from services.langs import LANGS

# DeepL 语言码
_DEEPL = {
    "zh": "ZH",
    "en": "EN",
    "ja": "JA",
    "ko": "KO",
    "fr": "FR",
    "de": "DE",
    "es": "ES",
    "ru": "RU",
}


def _deepl_translate(text: str, src: str, tgt: str, api_key: str, api_url: str) -> str:
    import requests

    headers = {"Authorization": f"DeepL-Auth-Key {api_key}"}
    data = {
        "text": text,
        "target_lang": _DEEPL.get(tgt, tgt.upper()),
    }
    if src in _DEEPL:
        data["source_lang"] = _DEEPL[src]
    r = requests.post(api_url, data=data, headers=headers, timeout=20)
    r.raise_for_status()
    payload = r.json()
    return payload["translations"][0]["text"]


def translate_text(text: str, src_lang: str, tgt_lang: str, engine: str | None = None) -> str:
    text = (text or "").strip()
    if not text:
        raise RuntimeError("没有可翻译的内容。")
    if src_lang == tgt_lang:
        return text

    cfg = load_config()
    engine = (engine or cfg.get("translate_engine") or "auto").lower()
    src = LANGS[src_lang]["code"]
    tgt = LANGS[tgt_lang]["code"]

    if engine == "deepl" or (engine == "auto" and (cfg.get("deepl_api_key") or "").strip()):
        key = (cfg.get("deepl_api_key") or "").strip()
        if key:
            try:
                return _deepl_translate(
                    text,
                    src,
                    tgt,
                    key,
                    cfg.get("deepl_api_url") or "https://api-free.deepl.com/v2/translate",
                )
            except Exception as e:
                if engine == "deepl":
                    raise RuntimeError(f"DeepL 失败：{e}") from e
                # auto 模式 DeepL 失败则继续回落

    order = {
        "auto": ("bing", "baidu", "youdao"),
        "bing": ("bing",),
        "baidu": ("baidu",),
        "youdao": ("youdao",),
        "deepl": ("bing", "baidu", "youdao"),  # deepl 已失败时的兜底
    }.get(engine, ("bing", "baidu", "youdao"))

    errors: list[str] = []
    for name in order:
        try:
            return ts.translate_text(
                text,
                translator=name,
                from_language=src,
                to_language=tgt,
            )
        except Exception as e:  # noqa: BLE001
            errors.append(f"{name}: {e}")
    raise RuntimeError("翻译失败：" + " | ".join(errors[:2]))
