# -*- coding: utf-8 -*-
"""一体化置顶窗：镂空视口 + 译文条。配置进设置页。"""
from __future__ import annotations

import ctypes
import os
import tempfile
import threading
import tkinter as tk
from tkinter import ttk
from typing import Callable

import numpy as np
import soundfile as sf

from services.branding import APP_ICON_ICO, APP_ICON_PNG, APP_NAME
from services.capture import grab_bbox
from services.config import load_config, save_config
from services.langs import LANG_NAMES
from services.ocr import ocr_pil, warmup as ocr_warmup
from services.stt import recognize_file
from services.translate import translate_text
from services.tts import play_mp3, synthesize
from ui.settings_dialog import SettingsDialog

HOLE = "#010203"
BG = "#1e1f24"
BG2 = "#2a2b32"
PANEL = "#f4f5f7"
ACCENT = "#e85d4c"
FG = "#e8e8ea"
MUTED = "#9a9aaa"
CLIP_MS = 600
MAX_CHARS_DEFAULT = 2000


def _enable_dpi_aware() -> None:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def _norm(text: str) -> str:
    return " ".join((text or "").split())


class MainWindow:
    def __init__(self) -> None:
        _enable_dpi_aware()
        self.cfg = load_config()
        os.environ["HF_ENDPOINT"] = self.cfg.get("hf_endpoint") or "https://hf-mirror.com"

        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry(self.cfg.get("window_geometry") or "420x580+100+80")
        self.root.minsize(360, 440)
        self.root.configure(bg=BG)
        self.root.attributes("-topmost", bool(self.cfg.get("topmost", True)))
        self.root.attributes("-transparentcolor", HOLE)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._set_app_icon()

        self.src_var = tk.StringVar(value=self.cfg.get("src_lang", "英语"))
        self.tgt_var = tk.StringVar(value=self.cfg.get("tgt_lang", "中文"))
        self.mode_clip = tk.BooleanVar(value=bool(self.cfg.get("mode_clip", True)))
        self.mode_screen = tk.BooleanVar(value=bool(self.cfg.get("mode_screen", True)))
        self.mode_speak = tk.BooleanVar(value=bool(self.cfg.get("mode_speak", False)))
        self.topmost = tk.BooleanVar(value=bool(self.cfg.get("topmost", True)))
        self.status_var = tk.StringVar(value="透明区对准文字 · 详细选项在「设置」")

        self._region_ms = int(float(self.cfg.get("region_interval_sec", 4)) * 1000)
        self._max_chars = int(self.cfg.get("max_chars", MAX_CHARS_DEFAULT))
        self._last_clip = ""
        self._last_ocr = ""
        self._busy = False
        self._listen = False
        self._frames: list[np.ndarray] = []
        self._rec_stream = None
        self._sd = None
        self._ocr_ready = False
        self._settings_win = None

        self._style()
        self._build()
        self.root.after(CLIP_MS, self._poll_clipboard)
        self.root.after(self._region_ms, self._poll_region)
        self.root.after(600, self._warmup_ocr_async)

    def _set_app_icon(self) -> None:
        try:
            if APP_ICON_ICO.exists():
                self.root.iconbitmap(default=str(APP_ICON_ICO))
        except Exception:
            pass
        try:
            if APP_ICON_PNG.exists():
                from PIL import Image, ImageTk

                img = Image.open(APP_ICON_PNG).resize((64, 64))
                self._icon_photo = ImageTk.PhotoImage(img)
                self.root.iconphoto(True, self._icon_photo)
        except Exception:
            pass

    def _style(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TButton", padding=(8, 4))
        style.configure("Tool.TButton", padding=(6, 2))
        style.configure("TCombobox", padding=2)

    def _chk(self, parent, text, var) -> tk.Checkbutton:
        return tk.Checkbutton(
            parent,
            text=text,
            variable=var,
            bg=BG2,
            fg=FG,
            selectcolor=BG,
            activebackground=BG2,
            activeforeground="#fff",
            highlightthickness=0,
            bd=0,
            font=("Microsoft YaHei UI", 9),
        )

    def _build(self) -> None:
        # 顶栏
        bar = tk.Frame(self.root, bg=BG2, height=44)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        tk.Label(bar, text=APP_NAME, bg=BG2, fg=FG, font=("Microsoft YaHei UI", 11, "bold")).pack(
            side="left", padx=(12, 10), pady=10
        )
        ttk.Combobox(
            bar, textvariable=self.src_var, values=LANG_NAMES, width=6, state="readonly"
        ).pack(side="left")
        ttk.Button(bar, text="⇄", width=3, command=self._swap, style="Tool.TButton").pack(
            side="left", padx=4
        )
        ttk.Combobox(
            bar, textvariable=self.tgt_var, values=LANG_NAMES, width=6, state="readonly"
        ).pack(side="left")
        ttk.Button(bar, text="设置", command=self._open_settings, style="Tool.TButton").pack(
            side="right", padx=(4, 10)
        )
        ttk.Button(bar, text="支持", command=self._open_support, style="Tool.TButton").pack(
            side="right"
        )

        # 模式条（仅日常开关）
        modes = tk.Frame(self.root, bg=BG2)
        modes.pack(fill="x")
        self._chk(modes, "剪贴板", self.mode_clip).pack(side="left", padx=(12, 6), pady=4)
        self._chk(modes, "屏幕识别", self.mode_screen).pack(side="left", padx=6)
        self._chk(modes, "朗读", self.mode_speak).pack(side="left", padx=6)
        self._chk(modes, "置顶", self.topmost).pack(side="left", padx=6)
        self.topmost.trace_add("write", lambda *_: self._toggle_topmost())

        # 透明视口
        wrap = tk.Frame(self.root, bg=ACCENT, padx=2, pady=2)
        wrap.pack(fill="both", expand=True, padx=10, pady=8)
        tk.Label(
            wrap,
            text="透明识别区",
            bg=ACCENT,
            fg="white",
            font=("Microsoft YaHei UI", 8),
        ).pack(fill="x")
        self.viewport = tk.Frame(wrap, bg=HOLE)
        self.viewport.pack(fill="both", expand=True)

        # 底部面板
        panel = tk.Frame(self.root, bg=PANEL)
        panel.pack(fill="x", side="bottom")

        tools = tk.Frame(panel, bg=PANEL)
        tools.pack(fill="x", padx=10, pady=(8, 4))
        ttk.Button(tools, text="立即识别", command=self._ocr_once).pack(side="left")
        ttk.Button(tools, text="翻译", command=self._manual_translate).pack(side="left", padx=6)
        ttk.Button(tools, text="朗读", command=self._speak_out).pack(side="left")
        ttk.Button(tools, text="清空", command=self._clear).pack(side="left", padx=6)
        self.mic_btn = ttk.Button(tools, text="按住说话")
        self.mic_btn.pack(side="right")
        self.mic_btn.bind("<ButtonPress-1>", self._mic_down)
        self.mic_btn.bind("<ButtonRelease-1>", self._mic_up)

        tk.Label(panel, text="原文", bg=PANEL, fg="#444", font=("Microsoft YaHei UI", 9)).pack(
            anchor="w", padx=10
        )
        self.src_text = tk.Text(
            panel, height=3, wrap="word", font=("Microsoft YaHei UI", 10), relief="flat", bd=6
        )
        self.src_text.pack(fill="x", padx=10, pady=2)

        tk.Label(panel, text="译文", bg=PANEL, fg="#444", font=("Microsoft YaHei UI", 9)).pack(
            anchor="w", padx=10
        )
        self.out_text = tk.Text(
            panel, height=4, wrap="word", font=("Microsoft YaHei UI", 10), relief="flat", bd=6
        )
        self.out_text.pack(fill="x", padx=10, pady=2)

        tk.Label(
            panel,
            textvariable=self.status_var,
            bg=PANEL,
            fg="#777",
            anchor="w",
            font=("Microsoft YaHei UI", 8),
        ).pack(fill="x", padx=10, pady=(2, 10))

    def _open_settings(self) -> None:
        if self._settings_win is not None and self._settings_win.winfo_exists():
            self._settings_win.lift()
            return
        self._settings_win = SettingsDialog(self.root, on_saved=self._apply_config)

    def _open_support(self) -> None:
        """打开设置并切到「关于 / 支持」。"""
        self._open_settings()
        win = self._settings_win
        if win is None:
            return
        try:
            for child in win.winfo_children():
                if isinstance(child, ttk.Notebook):
                    child.select(3)  # 关于 / 支持
                    break
        except Exception:
            pass

    def _apply_config(self, data: dict) -> None:
        self.cfg = data
        os.environ["HF_ENDPOINT"] = data.get("hf_endpoint") or "https://hf-mirror.com"
        self.src_var.set(data.get("src_lang", self.src_var.get()))
        self.tgt_var.set(data.get("tgt_lang", self.tgt_var.get()))
        self.mode_clip.set(bool(data.get("mode_clip", True)))
        self.mode_screen.set(bool(data.get("mode_screen", True)))
        self.mode_speak.set(bool(data.get("mode_speak", False)))
        self.topmost.set(bool(data.get("topmost", True)))
        self._region_ms = int(float(data.get("region_interval_sec", 4)) * 1000)
        self._max_chars = int(data.get("max_chars", MAX_CHARS_DEFAULT))
        eng = data.get("translate_engine", "auto")
        self._set_status(f"设置已应用 · 引擎 {eng} · 识别间隔 {data.get('region_interval_sec')}s")

    def _on_close(self) -> None:
        try:
            data = load_config()
            data["window_geometry"] = self.root.geometry()
            data["src_lang"] = self.src_var.get()
            data["tgt_lang"] = self.tgt_var.get()
            data["mode_clip"] = bool(self.mode_clip.get())
            data["mode_screen"] = bool(self.mode_screen.get())
            data["mode_speak"] = bool(self.mode_speak.get())
            data["topmost"] = bool(self.topmost.get())
            save_config(data)
        except Exception:
            pass
        self.root.destroy()

    def _toggle_topmost(self) -> None:
        self.root.attributes("-topmost", bool(self.topmost.get()))

    def _swap(self) -> None:
        s, t = self.src_var.get(), self.tgt_var.get()
        self.src_var.set(t)
        self.tgt_var.set(s)

    def _clear(self) -> None:
        self.src_text.delete("1.0", "end")
        self.out_text.delete("1.0", "end")
        self._last_ocr = ""
        self.status_var.set("已清空")

    def _ui(self, fn: Callable[[], None]) -> None:
        self.root.after(0, fn)

    def _set_status(self, msg: str) -> None:
        self._ui(lambda: self.status_var.set(msg))

    def _set_src(self, text: str) -> None:
        def apply() -> None:
            self.src_text.delete("1.0", "end")
            self.src_text.insert("1.0", text)

        self._ui(apply)

    def _set_out(self, text: str) -> None:
        def apply() -> None:
            self.out_text.delete("1.0", "end")
            self.out_text.insert("1.0", text)

        self._ui(apply)

    def _submit(self, work: Callable[[], None]) -> None:
        if self._busy:
            self._set_status("正在处理…")
            return
        self._busy = True

        def runner() -> None:
            try:
                work()
            finally:
                self._busy = False

        threading.Thread(target=runner, daemon=True).start()

    def _translate_pipeline(self, text: str, source: str) -> None:
        text = (text or "").strip()
        if not text:
            return
        if len(text) > self._max_chars:
            text = text[: self._max_chars]

        def work() -> None:
            self._set_status(f"翻译中…（{source}）")
            self._set_src(text)
            result = translate_text(text, self.src_var.get(), self.tgt_var.get())
            self._set_out(result)
            self._set_status(f"完成（{source}）")
            if self.mode_speak.get():
                path = synthesize(result, self.tgt_var.get())
                if path:
                    play_mp3(path)

        self._submit(work)

    def _manual_translate(self) -> None:
        self._translate_pipeline(self.src_text.get("1.0", "end"), "手动")

    def _speak_out(self) -> None:
        text = self.out_text.get("1.0", "end").strip()
        if not text:
            self._set_status("没有译文")
            return

        def work() -> None:
            self._set_status("朗读中…")
            path = synthesize(text, self.tgt_var.get())
            if path:
                play_mp3(path)
            self._set_status("朗读完成")

        self._submit(work)

    def _poll_clipboard(self) -> None:
        if self.mode_clip.get() and not self._busy:
            try:
                clip = self.root.clipboard_get()
            except tk.TclError:
                clip = ""
            if isinstance(clip, str):
                clip = clip.strip()
                if (
                    clip
                    and clip != self._last_clip
                    and not clip.startswith("http://")
                    and not clip.startswith("https://")
                    and any(ch.isalpha() or "\u4e00" <= ch <= "\u9fff" for ch in clip)
                ):
                    self._last_clip = clip
                    self._translate_pipeline(clip, "剪贴板")
        self.root.after(CLIP_MS, self._poll_clipboard)

    def _viewport_bbox(self) -> tuple[int, int, int, int]:
        self.root.update_idletasks()
        return (
            int(self.viewport.winfo_rootx()),
            int(self.viewport.winfo_rooty()),
            int(self.viewport.winfo_width()),
            int(self.viewport.winfo_height()),
        )

    def _warmup_ocr_async(self) -> None:
        def work() -> None:
            try:
                ocr_warmup()
                self._ocr_ready = True
                self._set_status("就绪 · 透明区对准文字即可")
            except Exception as e:  # noqa: BLE001
                self._set_status(f"OCR 加载失败：{e}")

        threading.Thread(target=work, daemon=True).start()

    def _read_viewport_text(self) -> str:
        if not self._ocr_ready:
            ocr_warmup()
            self._ocr_ready = True
        x, y, w, h = self._viewport_bbox()
        return ocr_pil(grab_bbox(x, y, w, h)).strip()

    def _ocr_once(self) -> None:
        def work() -> None:
            self._set_status("正在识别…")
            text = self._read_viewport_text()
            if not text:
                self._set_status("未识别到文字")
                return
            self._last_ocr = text
            self._set_src(text)
            result = translate_text(text, self.src_var.get(), self.tgt_var.get())
            self._set_out(result)
            self._set_status("完成（屏幕）")
            if self.mode_speak.get():
                path = synthesize(result, self.tgt_var.get())
                if path:
                    play_mp3(path)

        self._submit(work)

    def _poll_region(self) -> None:
        if self.mode_screen.get() and not self._busy:
            self._busy = True

            def runner() -> None:
                try:
                    text = self._read_viewport_text()
                    if not text:
                        self._set_status("屏幕识别：未读到文字")
                        return
                    if _norm(text) == _norm(self._last_ocr):
                        return
                    self._last_ocr = text
                    self._set_src(text)
                    result = translate_text(text, self.src_var.get(), self.tgt_var.get())
                    self._set_out(result)
                    self._set_status("完成（屏幕）")
                    if self.mode_speak.get():
                        path = synthesize(result, self.tgt_var.get())
                        if path:
                            play_mp3(path)
                except Exception as e:  # noqa: BLE001
                    self._set_status(f"屏幕识别：{e}")
                finally:
                    self._busy = False

            threading.Thread(target=runner, daemon=True).start()

        self.root.after(max(2000, self._region_ms), self._poll_region)

    def _ensure_sd(self):
        if self._sd is None:
            import sounddevice as sd

            self._sd = sd
        return self._sd

    def _mic_down(self, _event=None) -> None:
        if self._listen or self._busy:
            return
        try:
            sd = self._ensure_sd()
        except Exception as e:  # noqa: BLE001
            self._set_status(f"麦克风不可用：{e}")
            return
        self._listen = True
        self._frames = []
        self.mic_btn.configure(text="松开结束…")
        self._set_status("正在听…")

        def callback(indata, frames, time_info, status):  # noqa: ARG001
            if self._listen:
                self._frames.append(indata.copy())

        try:
            self._rec_stream = sd.InputStream(
                samplerate=16000, channels=1, dtype="float32", callback=callback
            )
            self._rec_stream.start()
        except Exception as e:  # noqa: BLE001
            self._listen = False
            self.mic_btn.configure(text="按住说话")
            self._set_status(f"麦克风失败：{e}")

    def _mic_up(self, _event=None) -> None:
        if not self._listen:
            return
        self._listen = False
        self.mic_btn.configure(text="按住说话")
        try:
            if self._rec_stream is not None:
                self._rec_stream.stop()
                self._rec_stream.close()
        except Exception:
            pass
        self._rec_stream = None
        if not self._frames:
            self._set_status("没有录到声音")
            return
        audio = np.concatenate(self._frames, axis=0).reshape(-1)
        if len(audio) < 16000 * 0.3:
            self._set_status("说太短了")
            return
        tmp = tempfile.mktemp(suffix=".wav")
        sf.write(tmp, audio, 16000)

        def work() -> None:
            self._set_status("语音识别中…")
            heard = recognize_file(tmp, self.src_var.get())
            self._set_src(heard)
            result = translate_text(heard, self.src_var.get(), self.tgt_var.get())
            self._set_out(result)
            self._set_status("完成（语音）")
            if self.mode_speak.get():
                path = synthesize(result, self.tgt_var.get())
                if path:
                    play_mp3(path)

        self._submit(work)

    def run(self) -> None:
        self.root.mainloop()
