#!/usr/bin/env python3
"""src/*.src.html から配布用HTMLを生成する。

使い方:
    python3 build.py                 # 全資料のHTMLを生成（ふだんはこちら）
    python3 build.py --pdf           # HTML生成 + PDF生成（先方へ送るときだけ）
    python3 build.py cainz --pdf     # ファイル名に "cainz" を含む資料だけ

各 src/*.src.html は次の2つを持つ。
  ・`<!-- OUT: 出力ファイル名.html -->`   出力名（デザインシステム §0 の命名規約に従う）
  ・`<style>` 内の `/* @@BASE@@ */`      共通スタイル src/_base.css を差し込む位置

_base.css 側にある2つのマーカーは build.py が埋める。
  ・`/* @@FONTS@@ */`   欧文フォント（Century Gothic → Europa Gothic → 埋め込みLato）
  ・`/* @@IMAGES@@ */`  その資料が参照している画像だけを data URI で差し込む

生成後のHTMLは単体で完結する（相対パス参照なし。デザインシステム §8-1）。
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_CSS = os.path.join(ROOT, "src", "_base.css")
IMAGES = os.path.join(ROOT, "assets", "images.json")
FONTS = os.path.join(ROOT, "assets", "fonts.json")

BASE_MARKER = "/* @@BASE@@ */"
FONT_MARKER = "/* @@FONTS@@ */"
IMG_MARKER = "/* @@IMAGES@@ */"

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/pw-browsers/chromium",
    shutil.which("chromium") or "",
    shutil.which("google-chrome") or "",
]

# local() で「Century Gothic → Europa Gothic → 埋め込みLato」の順に解決させる。
# 素の font-family 羅列だと、未導入フォント名が OS 側で別フォントに置換されてしまい
# 次の候補へフォールバックしない環境がある（Linux の fontconfig など）。
FONT_LOCALS = {
    400: ["Century Gothic Pro", "CenturyGothicPro", "Century Gothic", "CenturyGothic",
          "Europa Gothic", "EuropaGothic"],
    700: ["Century Gothic Pro Bold", "CenturyGothicPro-Bold", "Century Gothic Bold",
          "CenturyGothic-Bold", "Europa Gothic Bold", "EuropaGothic-Bold"],
}


def font_css() -> str:
    fonts = json.load(open(FONTS, encoding="utf-8"))
    faces = []
    for f in sorted(fonts.values(), key=lambda x: x["weight"]):
        src = ", ".join([f'local("{n}")' for n in FONT_LOCALS[f["weight"]]]
                        + [f'url({f["src"]}) format("woff2")'])
        faces.append("  @font-face { font-family: 'Domuz EN'; font-style: normal; "
                     "font-weight: %d;\n               src: %s; }" % (f["weight"], src))
    return "\n".join(faces)


def build_html(src_path: str) -> str:
    src = open(src_path, encoding="utf-8").read()
    m = re.search(r"<!--\s*OUT:\s*(.+?)\s*-->", src)
    if not m:
        sys.exit(f"{src_path}: `<!-- OUT: 出力ファイル名.html -->` がありません")
    out_path = os.path.join(ROOT, m.group(1))

    if BASE_MARKER not in src:
        sys.exit(f"{src_path}: {BASE_MARKER} がありません")
    html = src.replace(BASE_MARKER, open(BASE_CSS, encoding="utf-8").read())
    html = html.replace(FONT_MARKER, font_css())

    # 参照している画像だけを入れる。全画像を毎回入れると資料が無駄に重くなる
    images = json.load(open(IMAGES, encoding="utf-8"))
    refs = set(re.findall(r"\bim-([A-Za-z0-9_]+)", html))
    missing = sorted(refs - set(images))
    if missing:
        sys.exit(f"{src_path}: assets/images.json にないキーを参照しています: {missing}")
    used = sorted(refs)
    html = html.replace(IMG_MARKER, "\n".join(
        f"  .im-{k} {{ background-image: url({images[k]}); }}" for k in used))

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML: {os.path.basename(out_path)} "
          f"({os.path.getsize(out_path)/1024/1024:.2f} MB, 画像 {len(used)} 点)")
    return out_path


def find_chrome() -> str:
    for c in CHROME_CANDIDATES:
        if c and os.path.exists(c):
            return c
    return ""


def build_pdf(html_path: str) -> None:
    chrome = find_chrome()
    if not chrome:
        print("  Chrome/Chromium が見つからないため PDF 生成をスキップしました")
        return
    pdf_path = os.path.splitext(html_path)[0] + ".pdf"
    subprocess.run(
        [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
         f"--print-to-pdf={pdf_path}", f"file://{html_path}"],
        check=True, capture_output=True,
    )
    print(f"PDF : {os.path.basename(pdf_path)} ({os.path.getsize(pdf_path)/1024/1024:.2f} MB)")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    srcs = [p for p in sorted(glob.glob(os.path.join(ROOT, "src", "*.src.html")))
            if not os.path.basename(p).startswith("_")]
    if args:
        srcs = [p for p in srcs if any(a in os.path.basename(p) for a in args)]
    if not srcs:
        sys.exit("対象の src/*.src.html がありません")
    for src_path in srcs:
        out = build_html(src_path)
        if "--pdf" in sys.argv:
            build_pdf(out)
    if "--pdf" not in sys.argv:
        print("PDFは生成していません。先方へ送るときは `python3 build.py --pdf` を実行してください。")
