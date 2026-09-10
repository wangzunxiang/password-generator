# -*- coding: utf-8 -*-
"""
等保三级合规密码生成器 —— 核心逻辑层

依据 GB/T 22239-2019《信息安全技术 网络安全等级保护基本要求》
三级等保口令策略：
  - 口令长度不少于 8 位（本工具按更严格标准：不低于 10 位）
  - 包含大写字母、小写字母、数字、特殊字符中至少 3 类
  - 不得为简单/连续/重复口令

本模块仅依赖 Python 标准库（secrets 密码学安全随机源），
无任何 GUI 依赖，可独立导入进行单元测试。
"""
import math
import re
import secrets
import string

SPECIALS = "!@#$%^&*-_+=?"
MIN_LEN = 10
MAX_LEN = 32
MIN_TYPES = 3

# 字符类型（展示顺序）
TYPE_ORDER = ("upper", "lower", "digit", "special")
TYPE_NAMES = {
    "upper": "大写字母 (A-Z)",
    "lower": "小写字母 (a-z)",
    "digit": "数字 (0-9)",
    "special": "特殊字符 (!@#$%^&*-_+=?)",
}
TYPE_RANGES = {
    "upper": string.ascii_uppercase,
    "lower": string.ascii_lowercase,
    "digit": string.digits,
    "special": SPECIALS,
}

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


def selected_types(options):
    """按固定顺序返回被勾选的类型 key 列表。"""
    return [k for k in TYPE_ORDER if options.get(k)]


def pool_size(options):
    """当前勾选组合的有效字符池大小。"""
    return sum(len(TYPE_RANGES[k]) for k in selected_types(options))


def generate_password(length, options):
    """
    生成密码。
    length:  期望长度（不足类型数时自动补齐）
    options: dict，如 {"upper": True, "lower": True, "digit": True, "special": True}
    每类勾选字符至少出现 1 个，secrets 安全洗牌。
    """
    keys = selected_types(options)
    if not keys:
        raise ValueError("请至少勾选一种字符类型")
    length = max(length, len(keys))
    pools = [TYPE_RANGES[k] for k in keys]
    all_chars = "".join(pools)
    # 每类至少取一个，保证类型覆盖
    chars = [secrets.choice(p) for p in pools]
    chars += [secrets.choice(all_chars) for _ in range(length - len(chars))]
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
    """合规自检，返回 (是否合规, 问题列表)。"""
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


def password_entropy(pwd, options):
    """按当前勾选字符池估算口令熵（bits）。"""
    n = pool_size(options)
    return len(pwd) * math.log2(n) if n else 0.0
