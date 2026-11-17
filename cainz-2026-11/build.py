"""カインズ様向け協業提案デッキ。deck.html（単一ファイル・画像とフォントは埋め込み済み）を
dist/ に名前を付けて複製し、Chromium で PDF と確認用 PNG を作る。

  python3 build.py
"""
import os, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "20261117_カインズ様_協業のご提案"
DIST = os.path.join(HERE, "dist"); os.makedirs(DIST, exist_ok=True)
html = os.path.join(DIST, OUT + ".html"); pdf = os.path.join(DIST, OUT + ".pdf")
shutil.copyfile(os.path.join(HERE, "deck.html"), html)
subprocess.run(["node", os.path.join(HERE, "render.js"), html, pdf], check=True)
prev = os.path.join(DIST, "preview"); os.makedirs(prev, exist_ok=True)
for f in os.listdir(prev): os.remove(os.path.join(prev, f))
subprocess.run(["pdftoppm", "-r", "96", "-png", pdf, os.path.join(prev, "p")], check=True)
print(pdf)
