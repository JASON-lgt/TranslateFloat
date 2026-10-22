# -*- coding: utf-8 -*-
from __future__ import annotations

from functools import lru_cache

import numpy as np


@lru_cache(maxsize=1)
def _engine():
    from rapidocr_onnxruntime import RapidOCR

    return RapidOCR()


def warmup() -> None:
    _engine()


def ocr_pil(image) -> str:
    import cv2

    rgb = np.array(image.convert("RGB"))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    result, _ = _engine()(bgr)
    if not result:
        return ""
    lines = []
    for item in result:
        if len(item) >= 2 and item[1]:
            lines.append(str(item[1]).strip())
    return "\n".join(x for x in lines if x)
