# -*- coding: utf-8 -*-
"""
等保三级合规密码生成器 —— 图形界面层 (tkinter)

卡片式浅色主题，纯标准库实现（不依赖 ttk 主题差异），
在 Windows 7 / 10 / 11 上呈现一致外观。
"""
import os
import sys
import tkinter as tk
from tkinter import messagebox

import password_core as core

APP_TITLE = "等保三级合规密码生成器"
APP_VERSION = "1.1.1"

# ── 配色（浅色专业主题）─────────────────────────────
C_BG = "#f5f7fa"        # 窗口背景
C_CARD = "#ffffff"      # 卡片背景
C_BORDER = "#e3e8ef"    # 卡片/输入边框
C_PRIMARY = "#2f6fed"   # 主色（蓝）
C_PRIMARY_HOVER = "#1e5cd6"
C_PRIMARY_SOFT = "#eef3fe"   # 主色浅底
C_TEXT = "#2c3e50"
C_MUTED = "#8a94a6"
C_OK = "#1e8e5a"
C_WARN = "#c98a00"
C_DANGER = "#d64545"
C_TROUGH = "#dbe2ec"
C_DISABLED_BG = "#eef1f5"
C_DISABLED_FG = "#b3bcc9"

FAM = "Microsoft YaHei UI"
MONO = "Consolas"


def resource_path(rel):
    """兼容 PyInstaller --onefile 运行时资源定位。"""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


class Card:
    """带标题的圆角风格卡片（白色 + 细边框 + 标题强调条）。"""

    def __init__(self, parent, title):
        self.outer = tk.Frame(parent, bg=C_BG)
        self.inner = tk.Frame(self.outer, bg=C_CARD,
                              highlightbackground=C_BORDER, highlightthickness=1)
        self.inner.pack(fill="both", expand=True)

        head = tk.Frame(self.inner, bg=C_CARD)
        head.pack(fill="x", padx=14, pady=(10, 2))
        tk.Label(head, bg=C_PRIMARY, width=2).pack(side="left", pady=(1, 1))
        tk.Label(head, text=title, bg=C_CARD, fg=C_TEXT,
                 font=(FAM, 10, "bold")).pack(side="left", padx=(6, 0))

        self.body = tk.Frame(self.inner, bg=C_CARD)
        self.body.pack(fill="both", expand=True, padx=14, pady=(4, 12))


class App:
    def __init__(self, root):
        self.root = root
        root.title(f"{APP_TITLE}  {APP_VERSION}")
        root.configure(bg=C_BG)
        root.minsize(520, 470)
        root.resizable(True, True)
        try:
            root.iconbitmap(resource_path("app.ico"))
        except tk.TclError:
            pass

        self.length_var = tk.IntVar(value=12)
        self._vars = {k: tk.BooleanVar(value=True) for k in core.TYPE_ORDER}
        self.current_pwd = ""

        self._build_header()
        self._build_param_card()
        self._build_buttons()
        self._build_result_card()
        self._build_footer()

        root.columnconfigure(0, weight=1)
        root.bind("<Return>", lambda e: self.on_generate())

    # ── 布局 ─────────────────────────────────────────

    def _build_header(self):
        frm = tk.Frame(self.root, bg=C_BG)
        frm.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))
        frm.columnconfigure(0, weight=1)
        tk.Label(frm, bg=C_BG, fg=C_TEXT, font=(FAM, 13, "bold"),
                 text=APP_TITLE).grid(row=0, column=0, sticky="w")
        tk.Label(frm, bg=C_BG, fg=C_MUTED, font=(FAM, 8),
                 text="GB/T 22239-2019 · 三级等保口令策略").grid(
            row=0, column=1, sticky="e")

    def _build_param_card(self):
        card = Card(self.root, "生成参数")
        card.outer.grid(row=1, column=0, sticky="ew", padx=16, pady=4)
        body = card.body
        body.columnconfigure(1, weight=1)

        # 长度行
        tk.Label(body, bg=C_CARD, fg=C_TEXT, font=(FAM, 9),
                 text=f"长度（{core.MIN_LEN}–{core.MAX_LEN} 位）").grid(
            row=0, column=0, sticky="e", pady=(6, 4))
        self.scale = tk.Scale(body, from_=core.MIN_LEN, to=core.MAX_LEN,
                              orient="horizontal", length=210, showvalue=False,
                              bg=C_CARD, troughcolor=C_TROUGH,
                              activebackground=C_PRIMARY,
                              highlightthickness=0, sliderlength=20, width=10,
                              command=self._on_scale)
        self.scale.set(12)
        self.scale.grid(row=0, column=1, sticky="w", padx=10, pady=(6, 4))
        self.len_label = tk.Label(body, text="12", width=4,
                                  bg=C_PRIMARY_SOFT, fg=C_PRIMARY,
                                  font=(MONO, 11, "bold"), relief="flat",
                                  highlightthickness=1,
                                  highlightbackground=C_BORDER)
        self.len_label.grid(row=0, column=2, padx=(10, 0), pady=(6, 4))

        # 字符类型（单列，避免长标签在窄窗口被裁切）
        grid = tk.Frame(body, bg=C_CARD)
        grid.grid(row=1, column=0, columnspan=3, sticky="w", pady=(2, 0))
        grid.columnconfigure(0, weight=1)
        for idx, key in enumerate(core.TYPE_ORDER):
            cb = tk.Checkbutton(grid, text=core.TYPE_NAMES[key],
                                variable=self._vars[key],
                                font=(FAM, 9), bg=C_CARD, fg=C_TEXT,
                                activebackground=C_CARD,
                                activeforeground=C_TEXT,
                                selectcolor=C_PRIMARY_SOFT,
                                anchor="w",
                                highlightthickness=0)
            cb.grid(row=idx, column=0, sticky="w", pady=1)

        tk.Label(body, bg=C_CARD, fg=C_MUTED, font=(FAM, 8),
                 text=f"等保三级要求：长度≥{core.MIN_LEN} 位，至少 "
                      f"{core.MIN_TYPES} 类字符，禁止连续/重复弱口令").grid(
            row=2, column=0, columnspan=3, sticky="w", pady=(6, 0))

    def _build_buttons(self):
        frm = tk.Frame(self.root, bg=C_BG)
        frm.grid(row=2, column=0, pady=(6, 2))

        self.btn_gen = tk.Button(frm, text="生 成 密 码",
                                 command=self.on_generate,
                                 bg=C_PRIMARY, fg="white",
                                 activebackground=C_PRIMARY_HOVER,
                                 activeforeground="white",
                                 font=(FAM, 10, "bold"), bd=0,
                                 padx=10, pady=9, width=13,
                                 cursor="hand2", highlightthickness=0)
        self.btn_gen.pack(side="left", padx=(16, 8))

        self.btn_copy = tk.Button(frm, text="复制到剪贴板",
                                  command=self.on_copy,
                                  bg=C_CARD, fg=C_PRIMARY,
                                  activebackground=C_PRIMARY_SOFT,
                                  activeforeground=C_PRIMARY,
                                  font=(FAM, 10), bd=0,
                                  padx=10, pady=9, width=13,
                                  highlightthickness=1,
                                  highlightbackground=C_PRIMARY,
                                  cursor="hand2")
        self.btn_copy.pack(side="left", padx=(8, 16))
        self._set_copy_state(False)

    def _build_result_card(self):
        card = Card(self.root, "生成结果")
        card.outer.grid(row=3, column=0, sticky="ew", padx=16, pady=4)
        body = card.body
        body.columnconfigure(0, weight=1)

        self.pwd_var = tk.StringVar(value="点击「生成密码」开始")
        self.lbl_pwd = tk.Label(body, textvariable=self.pwd_var,
                                font=(MONO, 15, "bold"), fg=C_TEXT,
                                bg="#fbfcfe", relief="flat", anchor="w",
                                padx=14, pady=14,
                                highlightthickness=1,
                                highlightbackground=C_BORDER)
        self.lbl_pwd.grid(row=0, column=0, sticky="ew", pady=(4, 6))

        self.status_var = tk.StringVar(value="")
        self.lbl_status = tk.Label(body, textvariable=self.status_var,
                                   bg=C_CARD, fg=C_MUTED, anchor="w",
                                   justify="left", font=(FAM, 9))
        self.lbl_status.grid(row=1, column=0, sticky="ew", pady=(0, 2))

        self.meta_var = tk.StringVar(value="")
        self.lbl_meta = tk.Label(body, textvariable=self.meta_var,
                                 bg=C_CARD, fg=C_MUTED, anchor="w",
                                 font=(FAM, 8))
        self.lbl_meta.grid(row=2, column=0, sticky="ew")

    def _build_footer(self):
        tk.Label(self.root, bg=C_BG, fg=C_MUTED, font=(FAM, 8),
                 text="纯本地运行 · 不联网 · 不落盘 · 不记录任何密码").grid(
            row=4, column=0, pady=(4, 10))

    # ── 交互 ─────────────────────────────────────────

    def _on_scale(self, value):
        n = int(float(value))
        self.length_var.set(n)
        self.len_label.config(text=str(n))

    def _set_copy_state(self, enabled):
        if enabled:
            self.btn_copy.config(bg=C_CARD, fg=C_PRIMARY, cursor="hand2",
                                 highlightbackground=C_PRIMARY)
        else:
            self.btn_copy.config(bg=C_DISABLED_BG, fg=C_DISABLED_FG,
                                 cursor="arrow", highlightbackground=C_BORDER)

    def _set_status(self, text, color):
        self.status_var.set(text)
        self.lbl_status.config(fg=color)

    def on_generate(self):
        length = int(round(float(self.length_var.get())))
        length = max(core.MIN_LEN, min(core.MAX_LEN, length))
        opts = {k: self._vars[k].get() for k in core.TYPE_ORDER}
        if not any(opts.values()):
            messagebox.showwarning("提示", "请至少勾选一种字符类型",
                                   parent=self.root)
            return
        try:
            pwd = core.generate_password(length, opts)
        except ValueError as e:
            messagebox.showerror("错误", str(e), parent=self.root)
            return

        self.current_pwd = pwd
        self.pwd_var.set(pwd)
        self._set_copy_state(True)

        ent = core.password_entropy(pwd, opts)
        pool = core.pool_size(opts)
        sel = sum(opts.values())
        self.meta_var.set(
            f"熵 ≈ {ent:.0f} bit · 字符池 {pool} 种 · 已选 {sel}/4 类")

        if core.check_password(pwd)[0] and sel >= core.MIN_TYPES:
            self._set_status(
                "✔ 合规：满足等保三级口令策略要求（长度≥10 位，≥3 类字符，无弱特征）",
                C_OK)
        elif core.check_password(pwd)[0]:
            self._set_status(
                f"⚠ 长度与复杂度达标，但仅 {sel} 类字符（等保要求≥{core.MIN_TYPES} 类），建议勾选更多类型",
                C_WARN)
        else:
            _, issues = core.check_password(pwd)
            self._set_status("✘ 存在风险：" + "；".join(issues), C_DANGER)

    def on_copy(self):
        if not self.current_pwd:
            messagebox.showinfo("提示", "请先生成密码", parent=self.root)
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.current_pwd)
        self._set_status("已复制到剪贴板（请妥善保存，本工具不在本地存储任何密码）",
                         C_PRIMARY)
        self.btn_copy.config(text="✓ 已复制")
        self.root.after(1500, lambda: self.btn_copy.config(text="复制到剪贴板"))


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
