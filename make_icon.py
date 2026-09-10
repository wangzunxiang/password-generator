# -*- coding: utf-8 -*-
"""生成 app.ico：蓝色圆角方块 + 白色盾牌 + 钥匙孔。"""
from PIL import Image, ImageDraw

SIZE = 256
BG = (47, 111, 237, 255)        # 与 UI 主色一致
WHITE = (255, 255, 255, 255)

img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# 圆角方块
d.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=56, fill=BG)

# 盾牌
scx = SIZE / 2
top = 40
bot = SIZE - 34
w = 132
pts = [
    (scx, top),
    (scx + w / 2, top + 26),
    (scx + w / 2, top + 120),
    (scx, SIZE - 40),
    (scx - w / 2, top + 120),
    (scx - w / 2, top + 26),
]
d.polygon(pts, fill=WHITE)

# 钥匙孔（镂空：与背景同色）
ky = top + 84
d.ellipse([scx - 28, ky - 32, scx + 28, ky + 24], fill=BG)
d.polygon([(scx - 18, ky + 2), (scx + 18, ky + 2), (scx + 24, ky + 62),
           (scx - 24, ky + 62)], fill=BG)

# 顶部高光
d.arc([8, 8, SIZE - 8, SIZE - 8], start=200, end=320, fill=(255, 255, 255, 90), width=14)

img.save(r"E:\workspace\password_generator\app.ico",
         sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("app.ico written")
