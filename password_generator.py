# -*- coding: utf-8 -*-
"""
等保三级合规密码生成器 —— 程序入口

架构：
  password_core.py  核心逻辑（生成/合规检测/熵估算，纯标准库，可单测）
  ui.py             图形界面（tkinter 卡片式主题）

打包:  build.bat  ->  dist\\PasswordGenerator.exe
"""
from ui import main

if __name__ == "__main__":
    main()
