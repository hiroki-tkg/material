#!/usr/bin/env bash
# pptx → PDF → ページごとの SVG → 単一 HTML。
# 使い方: render.sh <deck.pptx> "<HTMLのタイトル>" "<サブ（日付・社名）>"
# 出力: 同じディレクトリに <name>.pdf, preview/svg/sNN.svg, <name>.html
set -euo pipefail
PPTX="$1"; TITLE="${2:-}"; SUB="${3:-}"
DIR="$(cd "$(dirname "$PPTX")" && pwd)"; NAME="$(basename "${PPTX%.pptx}")"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"
soffice --headless --convert-to pdf "$NAME.pptx" >/dev/null 2>&1
N=$(pdfinfo "$NAME.pdf" | awk '/^Pages:/ {print $2}')
rm -rf preview/svg && mkdir -p preview/svg
for i in $(seq 1 "$N"); do
  pdftocairo -svg -f "$i" -l "$i" "$NAME.pdf" "preview/svg/s$(printf %02d "$i").svg"
done
python3 "$HERE/build_html.py" preview/svg "$NAME.html" "${TITLE:-$NAME}" "$SUB"
# 目視確認用の PNG（100dpi。ラベルの重なりは 60dpi では見えない）
mkdir -p preview/png && pdftoppm -r 100 -png "$NAME.pdf" preview/png/p >/dev/null
echo "pages: $N  pdf: $DIR/$NAME.pdf  html: $DIR/$NAME.html  png: $DIR/preview/png/"
