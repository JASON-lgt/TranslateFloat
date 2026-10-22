# -*- coding: utf-8 -*-
"""设置对话框。支持作者信息写死，不可在此修改。"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from services.branding import AUTHOR_NAME, DONATE_IMAGE, SUPPORT_NOTE
from services.config import CONFIG_PATH, load_config, save_config
from services.langs import LANG_NAMES

ENGINES = [
    ("auto", "自动（有 DeepL Key 优先，否则必应→百度→有道）"),
    ("bing", "必应"),
    ("baidu", "百度"),
    ("youdao", "有道"),
    ("deepl", "DeepL（需 API Key）"),
]


class SettingsDialog(tk.Toplevel):
    def __init__(self, master: tk.Misc, on_saved=None) -> None:
        super().__init__(master)
        self.on_saved = on_saved
        self.title("设置")
        self.geometry("520x560")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.configure(bg="#f7f7f7")
        self._photo = None

        self.cfg = load_config()
        self.engine_var = tk.StringVar(value=self.cfg.get("translate_engine", "auto"))
        self.deepl_key = tk.StringVar(value=self.cfg.get("deepl_api_key", ""))
        self.deepl_url = tk.StringVar(
            value=self.cfg.get("deepl_api_url", "https://api-free.deepl.com/v2/translate")
        )
        self.src_var = tk.StringVar(value=self.cfg.get("src_lang", "英语"))
        self.tgt_var = tk.StringVar(value=self.cfg.get("tgt_lang", "中文"))
        self.interval_var = tk.DoubleVar(value=float(self.cfg.get("region_interval_sec", 4)))
        self.hf_var = tk.StringVar(value=self.cfg.get("hf_endpoint", "https://hf-mirror.com"))
        self.def_clip = tk.BooleanVar(value=bool(self.cfg.get("mode_clip", True)))
        self.def_screen = tk.BooleanVar(value=bool(self.cfg.get("mode_screen", True)))
        self.def_speak = tk.BooleanVar(value=bool(self.cfg.get("mode_speak", False)))
        self.def_top = tk.BooleanVar(value=bool(self.cfg.get("topmost", True)))

        self._build()
        self.bind("<Escape>", lambda _e: self.destroy())

    def _build(self) -> None:
        pad = {"padx": 14, "pady": 6}
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=12, pady=12)

        tab_tr = ttk.Frame(nb, padding=10)
        tab_ocr = ttk.Frame(nb, padding=10)
        tab_boot = ttk.Frame(nb, padding=10)
        tab_about = ttk.Frame(nb, padding=10)
        nb.add(tab_tr, text="翻译 / API")
        nb.add(tab_ocr, text="识别")
        nb.add(tab_boot, text="启动默认")
        nb.add(tab_about, text="关于 / 支持")

        ttk.Label(tab_tr, text="翻译引擎").grid(row=0, column=0, sticky="w", **pad)
        ttk.Combobox(
            tab_tr,
            textvariable=self.engine_var,
            values=[e[0] for e in ENGINES],
            state="readonly",
            width=16,
        ).grid(row=0, column=1, sticky="w", **pad)
        tip = "\n".join(f"• {k}：{v}" for k, v in ENGINES)
        ttk.Label(tab_tr, text=tip, foreground="#555", justify="left").grid(
            row=1, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 8)
        )
        ttk.Label(tab_tr, text="默认源语言").grid(row=2, column=0, sticky="w", **pad)
        ttk.Combobox(
            tab_tr, textvariable=self.src_var, values=LANG_NAMES, state="readonly", width=16
        ).grid(row=2, column=1, sticky="w", **pad)
        ttk.Label(tab_tr, text="默认目标语言").grid(row=3, column=0, sticky="w", **pad)
        ttk.Combobox(
            tab_tr, textvariable=self.tgt_var, values=LANG_NAMES, state="readonly", width=16
        ).grid(row=3, column=1, sticky="w", **pad)
        ttk.Separator(tab_tr).grid(row=4, column=0, columnspan=2, sticky="ew", pady=8)
        ttk.Label(tab_tr, text="DeepL API Key（可选）").grid(row=5, column=0, sticky="w", **pad)
        ttk.Entry(tab_tr, textvariable=self.deepl_key, width=42, show="*").grid(
            row=5, column=1, sticky="w", **pad
        )
        ttk.Label(tab_tr, text="DeepL API 地址").grid(row=6, column=0, sticky="w", **pad)
        ttk.Entry(tab_tr, textvariable=self.deepl_url, width=42).grid(
            row=6, column=1, sticky="w", **pad
        )
        ttk.Label(
            tab_tr,
            text="填写 Key 后，引擎选 deepl 或 auto 即可使用。",
            foreground="#666",
        ).grid(row=7, column=0, columnspan=2, sticky="w", padx=14)

        ttk.Label(tab_ocr, text="屏幕识别间隔（秒）").grid(row=0, column=0, sticky="w", **pad)
        ttk.Spinbox(
            tab_ocr, from_=2, to=30, increment=0.5, textvariable=self.interval_var, width=8
        ).grid(row=0, column=1, sticky="w", **pad)
        ttk.Label(tab_ocr, text="HuggingFace 镜像（语音模型）").grid(
            row=2, column=0, sticky="w", **pad
        )
        ttk.Entry(tab_ocr, textvariable=self.hf_var, width=42).grid(
            row=2, column=1, sticky="w", **pad
        )

        ttk.Checkbutton(tab_boot, text="启动时开启剪贴板自动译", variable=self.def_clip).pack(
            anchor="w", pady=4
        )
        ttk.Checkbutton(tab_boot, text="启动时开启屏幕识别", variable=self.def_screen).pack(
            anchor="w", pady=4
        )
        ttk.Checkbutton(tab_boot, text="启动时开启译后朗读", variable=self.def_speak).pack(
            anchor="w", pady=4
        )
        ttk.Checkbutton(tab_boot, text="启动时窗口置顶", variable=self.def_top).pack(
            anchor="w", pady=4
        )

        # 关于 / 支持：只读写死
        ttk.Label(
            tab_about,
            text=f"翻译飘窗  ·  作者 {AUTHOR_NAME}",
            font=("Microsoft YaHei UI", 11, "bold"),
        ).pack(anchor="w", padx=8, pady=(4, 8))
        ttk.Label(tab_about, text=SUPPORT_NOTE, foreground="#444", justify="left").pack(
            anchor="w", padx=8, pady=(0, 8)
        )
        self.qr_label = ttk.Label(tab_about)
        self.qr_label.pack(pady=8)
        self._load_qr()
        ttk.Label(
            tab_about,
            text="打开支付宝 → 扫一扫",
            foreground="#666",
        ).pack(pady=(0, 8))

        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=12, pady=(0, 12))
        ttk.Button(btns, text="取消", command=self.destroy).pack(side="right")
        ttk.Button(btns, text="保存", command=self._save).pack(side="right", padx=8)

    def _load_qr(self) -> None:
        path = DONATE_IMAGE
        if not path.exists():
            self.qr_label.configure(text="内置收款码缺失", image="")
            self._photo = None
            return
        try:
            from PIL import Image, ImageTk

            img = Image.open(path).convert("RGB")
            img.thumbnail((240, 240))
            self._photo = ImageTk.PhotoImage(img)
            self.qr_label.configure(image=self._photo, text="")
        except Exception as e:  # noqa: BLE001
            self.qr_label.configure(text=f"收款码加载失败：{e}", image="")
            self._photo = None

    def _save(self) -> None:
        eng = self.engine_var.get().strip().lower()
        if eng == "deepl" and not self.deepl_key.get().strip():
            messagebox.showwarning("设置", "选择 DeepL 时请填写 API Key。", parent=self)
            return
        try:
            interval = float(self.interval_var.get())
        except Exception:
            messagebox.showerror("设置", "识别间隔必须是数字。", parent=self)
            return
        if interval < 2:
            interval = 2.0

        data = load_config()
        data.update(
            {
                "translate_engine": eng,
                "deepl_api_key": self.deepl_key.get().strip(),
                "deepl_api_url": self.deepl_url.get().strip()
                or "https://api-free.deepl.com/v2/translate",
                "src_lang": self.src_var.get(),
                "tgt_lang": self.tgt_var.get(),
                "region_interval_sec": interval,
                "hf_endpoint": self.hf_var.get().strip() or "https://hf-mirror.com",
                "mode_clip": bool(self.def_clip.get()),
                "mode_screen": bool(self.def_screen.get()),
                "mode_speak": bool(self.def_speak.get()),
                "topmost": bool(self.def_top.get()),
            }
        )
        save_config(data)
        if self.on_saved:
            self.on_saved(data)
        messagebox.showinfo("设置", f"已保存到\n{CONFIG_PATH}", parent=self)
        self.destroy()
