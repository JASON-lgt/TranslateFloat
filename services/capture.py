# -*- coding: utf-8 -*-
from __future__ import annotations

from PIL import Image


def grab_bbox(left: int, top: int, width: int, height: int) -> Image.Image:
    """Screenshot a screen rectangle. Hollow transparent UI need not be hidden."""
    if width < 8 or height < 8:
        raise RuntimeError("识别区域太小")
    import mss

    with mss.mss() as sct:
        shot = sct.grab({"left": int(left), "top": int(top), "width": int(width), "height": int(height)})
    return Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
