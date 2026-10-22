# -*- coding: utf-8 -*-
"""Language metadata shared by translate / OCR / TTS / STT."""

LANGS = {
    "中文": {"code": "zh", "whisper": "zh", "voice": "zh-CN-XiaoxiaoNeural"},
    "英语": {"code": "en", "whisper": "en", "voice": "en-US-JennyNeural"},
    "日语": {"code": "ja", "whisper": "ja", "voice": "ja-JP-NanamiNeural"},
    "韩语": {"code": "ko", "whisper": "ko", "voice": "ko-KR-SunHiNeural"},
    "法语": {"code": "fr", "whisper": "fr", "voice": "fr-FR-DeniseNeural"},
    "德语": {"code": "de", "whisper": "de", "voice": "de-DE-KatjaNeural"},
    "西班牙语": {"code": "es", "whisper": "es", "voice": "es-ES-ElviraNeural"},
    "俄语": {"code": "ru", "whisper": "ru", "voice": "ru-RU-SvetlanaNeural"},
}

LANG_NAMES = list(LANGS.keys())
