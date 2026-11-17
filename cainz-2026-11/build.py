"""カインズ様向け協業提案デッキ（HTML）を単一ファイルに書き出し、PDF と確認用 PNG を作る。

  python3 build.py            # dist/ に HTML・PDF・preview/*.png
  python3 build.py --no-pdf   # HTML だけ

deck.html が元データ。img/ の画像と fonts/ のフォントは data URI で埋め込むので、
dist の HTML は 1 ファイルで開ける。欧文は Europa（Adobe Fonts）を local() で解決し、
無い環境では埋め込みの Jost にフォールバックする。和文は Zen Kaku Gothic New（Google Fonts）。
"""
import base64
import mimetypes
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_NAME = "20261117_カインズ様_協業のご提案"
DIST = os.path.join(HERE, "dist")
os.makedirs(DIST, exist_ok=True)


def data_uri(path):
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    if path.endswith(".woff2"):
        mime = "font/woff2"
    with open(path, "rb") as f:
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"


html = open(os.path.join(HERE, "deck.html"), encoding="utf-8").read()
html = re.sub(r'src="((?:img|fonts)/[^"]+)"', lambda m: f'src="{data_uri(os.path.join(HERE, m.group(1)))}"', html)
html = re.sub(r'url\((fonts/[^)]+)\)', lambda m: f'url("{data_uri(os.path.join(HERE, m.group(1)))}")', html)

out_html = os.path.join(DIST, OUT_NAME + ".html")
open(out_html, "w", encoding="utf-8").write(html)
print(out_html, len(html) // 1024, "KB")

if "--no-pdf" not in sys.argv:
    out_pdf = os.path.join(DIST, OUT_NAME + ".pdf")
    subprocess.run(["node", os.path.join(HERE, "render.js"), out_html, out_pdf], check=True)
    prev = os.path.join(DIST, "preview")
    os.makedirs(prev, exist_ok=True)
    for f in os.listdir(prev):
        os.remove(os.path.join(prev, f))
    subprocess.run(["pdftoppm", "-r", "96", "-png", out_pdf, os.path.join(prev, "p")], check=True)
    print(out_pdf)
