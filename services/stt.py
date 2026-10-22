# -*- coding: utf-8 -*-
from __future__ import annotations

import os

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

from services.langs import LANGS

_whisper = None


def get_whisper():
    global _whisper
    if _whisper is None:
        from faster_whisper import WhisperModel

        _whisper = WhisperModel("tiny", device="cpu", compute_type="int8")
    return _whisper


def recognize_file(audio_path: str, src_lang: str) -> str:
    if not audio_path:
        raise RuntimeError("没有音频。")
    model = get_whisper()
    lang = LANGS[src_lang]["whisper"]
    segments, _ = model.transcribe(audio_path, language=lang, vad_filter=True)
    text = "".join(seg.text for seg in segments).strip()
    if not text:
        raise RuntimeError("没听清，请再说一次。")
    return text
