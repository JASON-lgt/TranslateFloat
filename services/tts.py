# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
import time
from pathlib import Path

import numpy as np
from edge_tts import Communicate

from services.branding import app_root
from services.langs import LANGS

OUT_DIR = app_root() / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)


async def _save(text: str, lang: str, path: Path) -> None:
    await Communicate(text, LANGS[lang]["voice"]).save(str(path))


def synthesize(text: str, lang: str) -> Path | None:
    text = (text or "").strip()
    if not text:
        return None
    path = OUT_DIR / f"tts-{int(time.time() * 1000)}.mp3"
    asyncio.run(_save(text, lang, path))
    return path


def play_mp3(path: str | Path) -> None:
    """Decode mp3 and play without stealing focus."""
    try:
        import av
        import sounddevice as sd

        container = av.open(str(path))
        chunks: list[np.ndarray] = []
        rate = 24000
        for frame in container.decode(audio=0):
            arr = frame.to_ndarray()
            if arr.ndim > 1:
                arr = np.mean(arr, axis=0)
            arr = arr.astype(np.float32, copy=False)
            if np.max(np.abs(arr)) > 1.5:
                arr = arr / 32768.0
            chunks.append(arr)
            rate = frame.sample_rate or rate
        if chunks:
            sd.play(np.concatenate(chunks), rate, blocking=False)
    except Exception:
        pass
