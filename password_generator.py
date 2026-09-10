# -*- coding: utf-8 -*-
"""
等保三级合规密码生成器
依据 GB/T 22239-2019 三级等保口令策略要求：
  - 长度不少于 8 位（本工具按更严格标准：不低于 10 位）
  - 包含大小写字母、数字、特殊字符中至少 3 类
  - 不得为简单/连续/重复口令
采用 secrets 模块（密码学安全随机源）生成。
"""
import re
import string
import secrets
import tkinter as tk
from tkinter import ttk, messagebox

SPECIALS = "!@#$%^&*-_+=?"
MIN_LEN = 10
MAX_LEN = 32
MIN_TYPES = 3

COMMON_WORDS = [
    "123456", "123456789", "12345678", "1234567", "12345", "000000",
    "111111", "112233", "11223344", "666666", "888888", "qwerty",
    "qazwsx", "1qaz2wsx", "1q2w3e", "password", "passw0rd", "admin",
    "admin123", "root", "root123", "iloveyou", "abc123", "abcd1234",
    "welcome", "letmein", "monkey", "dragon", "sunshine", "princess",
    "shadow", "master", "hello", "charlie", "donald", "baseball",
    "qwerty123", "admin@123", "woaini", "p@ssw0rd", "wo5wo5",
    "password1", "password123", "pass123", "abc@123", "a123456",
]

TYPE_NAMES = {
    "upper": "大写字母 (A-Z)",
    "lower": "小写字母 (a-z)",
    "digit": "数字 (0-9)",
    "special": "特殊字符 (!@#$%^&*-_+=?)",
}


def generate_password(length, use_upper, use_lower, use_digit, use_special):
    pools = []
    if use_upper:
        pools.append(string.ascii_uppercase)
    if use_lower:
        pools.append(string.ascii_lowercase)
    if use_digit:
        pools.append(string.digits)
    if use_special:
        pools.append(SPECIALS)
    if not pools:
        raise ValueError("请至少勾选一种字符类型")
    if length < len(pools):
        length = len(pools)
    all_chars = "".join(pools)
    # 每类至少取一个，保证类型覆盖
    chars = [secrets.choice(p) for p in pools]
    chars += [secrets.choice(all_chars) for _ in range(length - len(pools))]
    # 密码学安全洗牌 (Fisher-Yates + secrets.randbelow)
    for i in range(len(chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        chars[i], chars[j] = chars[j], chars[i]
    return "".join(chars)


def _consecutive_issue(pwd):
    for i in range(len(pwd) - 2):
        a, b, c = pwd[i], pwd[i + 1], pwd[i + 2]
        same_class = (a.islower() and b.islower() and c.islower()) or \
                     (a.isupper() and b.isupper() and c.isupper()) or \
                     (a.isdigit() and b.isdigit() and c.isdigit())
        if same_class and ord(b) - ord(a) == 1 and ord(c) - ord(b) == 1:
            return True
        if same_class and ord(a) - ord(b) == 1 and ord(b) - ord(c) == 1:
            return True
    return False


def check_password(pwd):
    """返回 (是否合规, 问题列表)"""
    issues = []
    if len(pwd) < MIN_LEN:
        issues.append(f"长度 {len(pwd)} 位，低于 {MIN_LEN} 位要求")
    types = 0
    if re.search(r"[A-Z]", pwd):
        types += 1
    if re.search(r"[a-z]", pwd):
        types += 1
    if re.search(r"[0-9]", pwd):
        types += 1
    if re.search(r"[^A-Za-z0-9]", pwd):
        types += 1
    if types < MIN_TYPES:
        issues.append(f"仅含 {types} 类字符，等保三级要求至少 {MIN_TYPES} 类（大小写/数字/特殊字符）")
    if _consecutive_issue(pwd):
        issues.append("含连续递增/递减序列（如 abc、123、xyz）")
    if re.search(r"(.)\1{2,}", pwd):
        issues.append("同一字符连续出现 3 次及以上")
    low = pwd.lower()
    for w in COMMON_WORDS:
        if w in low:
            issues.append(f"含常见弱口令词根 '{w}'")
            break
    return (len(issues) == 0, issues)


class App:
    def __init__(self, root):
        self.root = root
        root.title("等保三级合规密码生成器")
        root.resizable(False, False)

        self.length_var = tk.IntVar(value=12)
        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.digit_var = tk.BooleanVar(value=True)
        self.special_var = tk.BooleanVar(value=True)
        self.current_pwd = ""

        # ── 参数区 ──
        frm_param = ttk.LabelFrame(root, text="生成参数")
        frm_param.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="ew")

        ttk.Label(frm_param, text=f"长度（{MIN_LEN}–{MAX_LEN} 位）:").grid(
            row=0, column=0, padx=(10, 8), pady=(8, 4), sticky="e")
        scale = ttk.Scale(frm_param, from_=MIN_LEN, to=MAX_LEN,
                          orient="horizontal", length=160,
                          command=self._on_scale)
        scale.set(12)
        scale.grid(row=0, column=1, padx=(0, 8), pady=(8, 4), sticky="w")
        self.len_label = ttk.Label(frm_param, text="12", width=4,
                                   font=("Consolas", 10, "bold"))
        self.len_label.grid(row=0, column=2, pady=(8, 4))

        checks = [
            (self.upper_var, "upper"),
            (self.lower_var, "lower"),
            (self.digit_var, "digit"),
            (self.special_var, "special"),
        ]
        for idx, (var, key) in enumerate(checks):
            cb = ttk.Checkbutton(frm_param, text=TYPE_NAMES[key], variable=var)
            cb.grid(row=1, column=idx // 2,
                    rowspan=1, columnspan=1,
                    padx=(10, 16), pady=(0, 10), sticky="w")

        ttk.Label(frm_param, foreground="#888888",
                  text=f"等保三级要求：长度≥{MIN_LEN}位（本工具上限{MAX_LEN}），"
                       f"至少 {MIN_TYPES} 类字符，禁止连续/重复弱口令").grid(
            row=2, column=0, columnspan=4, padx=10, pady=(0, 6), sticky="w")

        # ── 操作按钮 ──
        frm_btn = ttk.Frame(root)
        frm_btn.grid(row=1, column=0, pady=4)
        self.btn_gen = ttk.Button(frm_btn, text="生 成 密 码",
                                  command=self.on_generate, width=16)
        self.btn_gen.grid(row=0, column=0, padx=8)
        self.btn_copy = ttk.Button(frm_btn, text="复制到剪贴板",
                                   command=self.on_copy, width=16)
        self.btn_copy.grid(row=0, column=1, padx=8)

        # ── 结果区 ──
        frm_res = ttk.LabelFrame(root, text="生成结果")
        frm_res.grid(row=2, column=0, padx=12, pady=6, sticky="ew")
        self.pwd_var = tk.StringVar(value="点击『生成密码』开始")
        self.lbl_pwd = tk.Label(frm_res, textvariable=self.pwd_var,
                                font=("Consolas", 16, "bold"),
                                fg="#1a5276", anchor="w",
                                bg="#fdfefe", relief="solid", bd=1,
                                padx=10, pady=10)
        self.lbl_pwd.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 4),
                          sticky="ew")

        self.status_var = tk.StringVar(value="")
        self.lbl_status = tk.Label(frm_res, textvariable=self.status_var,
                                   anchor="w", justify="left",
                                   font=("Microsoft YaHei", 9))
        self.lbl_status.grid(row=1, column=0, columnspan=2,
                             padx=12, pady=(0, 10), sticky="ew")

        root.columnconfigure(0, weight=1)
        root.bind("<Return>", lambda e: self.on_generate())

    def _on_scale(self, value):
        n = int(float(value))
        self.len_label.config(text=str(n))

    def on_generate(self):
        length = int(round(float(self.length_var.get())))
        length = max(MIN_LEN, min(MAX_LEN, length))
        opts = (self.upper_var.get(), self.lower_var.get(),
                self.digit_var.get(), self.special_var.get())
        if not any(opts):
            messagebox.showwarning("提示", "请至少勾选一种字符类型")
            return
        sel_types = sum(1 for v in opts if v)
        try:
            pwd = generate_password(length, *opts)
        except ValueError as e:
            messagebox.showerror("错误", str(e))
            return
        self.current_pwd = pwd
        self.pwd_var.set(pwd)
        ok, issues = check_password(pwd)
        if ok and sel_types >= MIN_TYPES:
            self.lbl_status.config(
                text="✔ 合规：满足等保三级口令策略要求（长度≥10位，≥3类字符，无弱特征）",
                foreground="#1e8449")
        elif ok:
            self.lbl_status.config(
                text=f"⚠ 长度与复杂度达标，但仅 {sel_types} 类字符（等保要求≥{MIN_TYPES}类），建议勾选更多类型",
                foreground="#b9770e")
        else:
            self.lbl_status.config(
                text="✘ 存在风险：" + "；".join(issues),
                foreground="#c0392b")

    def on_copy(self):
        if not self.current_pwd:
            messagebox.showinfo("提示", "请先生成密码")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.current_pwd)
        self.lbl_status.config(
            text="已复制到剪贴板（请妥善保存，本工具不在本地存储任何密码）",
            foreground="#1a5276")


def main():
    root = tk.Tk()
    try:
        ttk.Style().theme_use("vista")
    except tk.TclError:
        pass
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
