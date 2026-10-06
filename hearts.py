#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
满屏小爱心 ♥  ——  纯标准库实现，只用 Python 自带的 tkinter，不需要 pip install 任何东西

用法：
    python3 hearts.py                      全屏爱心，按 Esc 或点一下关闭
    python3 hearts.py --text "好想你哇"     屏幕中央再显示一句话
    python3 hearts.py --count 300          爱心数量（默认 160，卡就调小）
    python3 hearts.py --seconds 15         15 秒后自动关闭
    python3 hearts.py --selftest           自检模式：小窗口跑 30 帧就退出

在 Mac 上跑完，如果想让她的 Windows 也看：这个脚本可以直接发给她，或者
你自己跑，然后用屏幕共享 / 网页版（index.html 里那个「惊喜」按钮）给她看。
"""

import argparse
import colorsys
import math
import random
import sys
import time

try:
    import tkinter as tk
except ImportError:                                    # pragma: no cover
    sys.exit(
        "这个脚本需要 Python 自带的 tkinter。\n"
        "  macOS  : brew install python-tk\n"
        "  Ubuntu : sudo apt install python3-tk\n"
        "  Windows: 重新装 python.org 的安装包，勾选 tcl/tk"
    )

BG = "#0a0510"          # 背景：很深很深的紫黑
FPS = 33                # 每秒帧数


# ----------------------------------------------------------------------
# 心形参数方程：x = 16sin³t, y = 13cos t − 5cos2t − 2cos3t − cos4t
# 用它画出来的心是数学意义上最标准的那种，不依赖任何字体
# ----------------------------------------------------------------------
def heart_points(size, steps=24):
    pts = []
    for i in range(steps):
        t = i * 2.0 * math.pi / steps
        x = 16.0 * math.sin(t) ** 3
        y = (13.0 * math.cos(t) - 5.0 * math.cos(2 * t)
             - 2.0 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((x * size / 32.0, -y * size / 32.0))
    return pts


def hls_hex(h, l, s=0.92):
    r, g, b = colorsys.hls_to_rgb(h % 1.0, max(0.0, min(1.0, l)), s)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


class Heart:
    __slots__ = ("item", "pts", "x", "y", "vy", "amp", "phase", "hue", "top")

    def __init__(self, canvas, w, h, spawn_bottom=True):
        self.pts = heart_points(random.uniform(6.5, 26.0))
        self.top = min(p[1] for p in self.pts)          # 用来判断什么时候飘出屏幕
        self.x = random.uniform(0, w)
        self.y = h + random.uniform(0, h * 0.6) if spawn_bottom else random.uniform(0, h)
        self.vy = random.uniform(1.0, 3.2)              # 向上飘的速度
        self.amp = random.uniform(0.3, 1.5)             # 左右摇摆幅度
        self.phase = random.uniform(0, math.tau)
        # 大部分是粉红，少数偏正红
        self.hue = random.uniform(0.92, 0.99) if random.random() < 0.75 else random.uniform(0.0, 0.04)
        self.item = canvas.create_polygon(
            *self._flat(), fill=hls_hex(self.hue, 0.72), outline=""
        )
        canvas.itemconfig(self.item, tags="heart")

    def _flat(self):
        out = []
        for px, py in self.pts:
            out.append(self.x + px)
            out.append(self.y + py)
        return out

    def step(self, w, h):
        self.phase += 0.045
        self.x += math.sin(self.phase) * self.amp
        self.y -= self.vy
        if self.y + self.top < -30 or self.x < -70 or self.x > w + 70:
            self.x = random.uniform(0, w)
            self.y = h + random.uniform(10, 90)
        return self._flat()


class App:
    def __init__(self, root, count, text, seconds, selftest):
        self.root = root
        self.selftest = selftest
        self.frames = 0
        self.started = time.time()

        self.w, self.h = (430, 320) if selftest else (root.winfo_screenwidth(), root.winfo_screenheight())

        if not selftest:
            root.attributes("-fullscreen", True)
            try:
                root.attributes("-topmost", True)
            except tk.TclError:
                pass
        else:
            root.geometry("%dx%d" % (self.w, self.h))

        root.configure(bg=BG)
        root.title("♥")
        self.cv = tk.Canvas(root, bg=BG, highlightthickness=0, bd=0, width=self.w, height=self.h)
        self.cv.pack(fill="both", expand=True)

        self.hearts = [Heart(self.cv, self.w, self.h, spawn_bottom=False) for _ in range(count)]

        if text:
            self.cv.create_text(
                self.w / 2, self.h / 2, text=text, fill="#ffe3ee",
                font=("PingFang SC", max(18, int(self.h * 0.045)), "bold"),
            )

        root.bind("<Escape>", lambda e: self.quit())
        root.bind("<Button-1>", lambda e: self.quit())
        root.protocol("WM_DELETE_WINDOW", self.quit)

        if seconds:
            root.after(int(seconds * 1000), self.quit)

        self.tick()

    def tick(self):
        self.frames += 1
        for heart in self.hearts:
            flat = heart.step(self.w, self.h)
            self.cv.coords(heart.item, *flat)

        # 自检：跑满 30 帧就自己退出，不打扰任何人
        if self.selftest and self.frames >= 30:
            self.quit()
            return

        self.root.after(int(1000 / FPS), self.tick)

    def quit(self):
        try:
            self.root.destroy()
        except tk.TclError:
            pass


def main():
    ap = argparse.ArgumentParser(description="满屏小爱心 ♥")
    ap.add_argument("--count", type=int, default=160, help="爱心数量，默认 160")
    ap.add_argument("--text", default="", help="屏幕中央显示的文字")
    ap.add_argument("--seconds", type=float, default=0, help="多少秒后自动关闭，0 = 不自动关")
    ap.add_argument("--seed", type=int, default=0, help="随机种子（同一个种子每次长得一样）")
    ap.add_argument("--selftest", action="store_true", help="自检模式：小窗口跑 30 帧退出")
    args = ap.parse_args()

    if args.seed:
        random.seed(args.seed)

    root = tk.Tk()
    app = App(root, max(1, args.count), args.text, args.seconds, args.selftest)
    root.mainloop()

    if args.selftest:
        print("✓ 自检通过：%d 帧，%d 颗爱心，退出码 0" % (app.frames, len(app.hearts)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
