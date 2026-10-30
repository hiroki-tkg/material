"""ページごとの SVG（render.sh が作る preview/svg/sNN.svg）を 1 枚の HTML にまとめる。
SVG は文字を図形として持つので、閲覧側にフォントがなくても PDF と同じ見た目になる。

使い方: python3 build_html.py <svgディレクトリ> <出力html> "<ヘッダーのタイトル>" "<サブ（日付・社名）>"
"""
import glob
import os
import re
import sys

svg_dir, out, title, sub = sys.argv[1], sys.argv[2], sys.argv[3], (sys.argv[4] if len(sys.argv) > 4 else "")
slides = []
for k, path in enumerate(sorted(glob.glob(os.path.join(svg_dir, "s*.svg"))), 1):
    svg = open(path, encoding="utf-8").read()
    svg = re.sub(r"<\?xml[^>]*\?>\s*", "", svg)
    svg = re.sub(r'id="([^"]+)"', rf'id="p{k}-\1"', svg)  # ページごとに id が重なるので接頭辞を付ける
    svg = re.sub(r'(xlink:href|href)="#([^"]+)"', rf'\1="#p{k}-\2"', svg)
    svg = re.sub(r"url\(#([^)]+)\)", rf"url(#p{k}-\1)", svg)
    svg = re.sub(r'width="720" height="540"', 'role="img" aria-label="スライド %d"' % k, svg, count=1)
    slides.append(f'<section class="slide" id="s{k}">{svg}</section>')

html = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
:root {{ --bg: #eef1f1; --fg: #004347; --muted: #626262; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--fg);
  font-family: Montserrat, "Noto Sans JP", "Hiragino Sans", sans-serif; }}
header {{ max-width: 1040px; margin: 0 auto; padding: 24px 16px 8px; }}
header h1 {{ font-size: 20px; margin: 0 0 4px; }}
header p {{ font-size: 13px; color: var(--muted); margin: 0; }}
main {{ max-width: 1040px; margin: 0 auto; padding: 8px 16px 48px; display: grid; gap: 20px; }}
.slide {{ background: #fff; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,.12); overflow: hidden; }}
.slide svg {{ display: block; width: 100%; height: auto; }}
@media print {{
  body {{ background: #fff; }} header {{ display: none; }}
  main {{ padding: 0; gap: 0; max-width: none; }}
  .slide {{ box-shadow: none; border-radius: 0; page-break-after: always; }}
}}
</style>
</head>
<body>
<header>
<h1>{title}</h1>
<p>{sub}　全{len(slides)}ページ</p>
</header>
<main>
{chr(10).join(slides)}
</main>
</body>
</html>
"""
open(out, "w", encoding="utf-8").write(html)
print(out, len(html) // 1024, "KB")
