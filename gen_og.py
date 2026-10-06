#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成微信/社交平台分享卡片的封面图 og-cover.jpg（1200x630 标准 OG 尺寸）"""

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1200, 630          # 标准 OG 尺寸
S = 3                     # 超采样倍数，保证边缘平滑
w, h = W * S, H * S


def heart_polygon(cx, cy, size, n=200):
    """心形参数方程，返回顶点列表（数学意义上最标准的心）"""
    pts = []
    for i in range(n):
        t = i * 2.0 * math.pi / n
        x = 16.0 * math.sin(t) ** 3
        y = 13.0 * math.cos(t) - 5.0 * math.cos(2 * t) - 2.0 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * size / 32.0, cy - y * size / 32.0))
    return pts


# ---------------------------------------------------------------- 背景：径向渐变
yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
cx, cy = w * 0.5, h * 0.50
r = np.sqrt(((xx - cx) / (w * 0.60)) ** 2 + ((yy - cy) / (h * 0.78)) ** 2)
r = np.clip(r, 0.0, 1.0)

inner = np.array([176, 52, 104], dtype=np.float32)    # 中心的玫瑰
outer = np.array([20, 6, 18], dtype=np.float32)       # 边缘的深紫黑
mix = (1.0 - r) ** 1.7
bg = outer + (inner - outer) * mix[..., None]

# 再叠一层偏紫的暗角，增加层次
violet = np.array([46, 14, 52], dtype=np.float32)
bg = bg * 0.82 + violet * (1.0 - mix)[..., None] * 0.30

img = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), "RGB")

# ---------------------------------------------------------------- 发光层
glow = Image.new("L", (w, h), 0)
gd = ImageDraw.Draw(glow)
main_size = h * 0.60
gd.polygon(heart_polygon(cx, cy * 1.02, main_size), fill=255)
glow = glow.filter(ImageFilter.GaussianBlur(radius=w * 0.028))

halo = Image.new("RGB", (w, h), (255, 118, 168))
img = Image.composite(halo, img, glow.point(lambda v: int(v * 0.85)))

# 更大范围的一层柔光
glow2 = Image.new("L", (w, h), 0)
ImageDraw.Draw(glow2).polygon(heart_polygon(cx, cy * 1.02, main_size * 1.06), fill=140)
glow2 = glow2.filter(ImageFilter.GaussianBlur(radius=w * 0.075))
img = Image.composite(Image.new("RGB", (w, h), (255, 150, 190)), img,
                      glow2.point(lambda v: int(v * 0.5)))

# ---------------------------------------------------------------- 主心：实心亮粉
d = ImageDraw.Draw(img)
d.polygon(heart_polygon(cx, cy * 1.02, main_size), fill=(255, 143, 176))

# 小心脏，散在四周，透明度各不相同
rng = np.random.default_rng(7)
layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
ld = ImageDraw.Draw(layer)
for _ in range(46):
    ang = rng.uniform(0, 2 * math.pi)
    rad = rng.uniform(0.42, 1.05)
    px = cx + math.cos(ang) * w * 0.5 * rad
    py = cy + math.sin(ang) * h * 0.62 * rad
    if abs(px - cx) < w * 0.16 and abs(py - cy) < h * 0.30:
        continue                                    # 别压在主心上
    sz = rng.uniform(h * 0.028, h * 0.075)
    a = int(rng.uniform(60, 200))
    ld.polygon(heart_polygon(px, py, sz),
               fill=(255, int(rng.uniform(150, 205)), int(rng.uniform(185, 225)), a))
img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

# ---------------------------------------------------------------- 缩回目标尺寸
out = img.resize((W, H), Image.LANCZOS)
out.save("og-cover.jpg", "JPEG", quality=92, optimize=True, progressive=True)
print("✓ 已生成 og-cover.jpg  %dx%d" % out.size)

import os
print("  文件大小: %.1f KB" % (os.path.getsize("og-cover.jpg") / 1024))
