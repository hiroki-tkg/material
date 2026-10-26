"""世界のEC化率（国別）— Domuz デザインシステム「発表スライド」型で1枚のグラフを生成する。

出典: 経済産業省 令和5年度電子商取引に関する市場調査報告書（物販系分野、サービス系分野を含む）
使い方: python3 build_chart.py  → ec_ratio_world.pptx。PDF/SVG/PNG は domuz-deck の render.sh で書き出す。
"""
import os
import sys

SKILL_SCRIPTS = os.environ.get(
    "DOMUZ_DECK_SCRIPTS",
    os.path.expanduser("~/.claude/skills/synced/c877595e-9c45-49a9-8ea7-19fa3e366349_909874ba-85e7-4fba-9ee5-df754fdb136c/domuz-deck/scripts"),
)
sys.path.insert(0, SKILL_SCRIPTS)
from deck_lib import *  # noqa: E402,F401,F403

use_theme("domuz")

# ---- データ（EC化率 %、経産省 令和5年度報告書） ----
WORLD_AVG = ("世界平均", 19.4)
JAPAN = "日本"
rows = [
    ("中国", 48.0),
    ("英国", 29.6),
    ("インドネシア", 26.4),
    ("韓国", 25.1),
    ("ノルウェー", 18.7),
    ("フィンランド", 16.4),
    ("デンマーク", 16.1),
    ("米国", 15.6),
    (JAPAN, 13.7),
    ("メキシコ", 13.5),
    WORLD_AVG,  # 一番下ではなく、値の順に並べる
]
rows.sort(key=lambda r: -r[1])
jp = dict(rows)[JAPAN]
diff = jp - WORLD_AVG[1]

# ---- ページ ----
# 1枚ものなので content_slide は使わず、タイトルとサブの間を広めに取る（ページ番号なし）
s = new_slide()
rect(s, 0, 0, 8, H_PX, T.accent)
text(s, MARGIN, 44, 1000, 56, "世界と比べ、日本のEC市場はまだまだ伸び代がある", size=38, bold=True)
text(s, MARGIN, 122, 1000, 36, "国別のEC化率　単位：%", size=20, color=SECONDARY)

# グラフの枠
name_w = 150
gx, gy = MARGIN + name_w + 20, 216     # 棒の左端・上端
bar_w, row_h = 430, 40
vmax, ticks = 50, (0, 10, 20, 30, 40, 50)
gh = row_h * len(rows)

# 目盛り（上）と補助線
for t in ticks:
    tx = gx + bar_w * t / vmax
    text(s, tx - 30, gy - 24, 60, 18, f"{t}%", size=11, color=MUTED, align=PP_ALIGN.CENTER, en=True, spacing=1.0)
    vline(s, tx, gy, gh, WATERMARK if t else BORDER_LIGHT, 1.0)

# 凡例（グラフのタイトル行と同じ高さ）
lx = 470
for lab, col in [("日本", T.accent), ("世界平均", T.dark), ("その他の国", BG_GRAY)]:
    rect(s, lx, 166, 10, 10, col)
    text(s, lx + 16, 160, 120, 22, lab, size=11, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    lx += 16 + len(lab) * 11 + 28

# 横棒
for i, (name, v) in enumerate(rows):
    ry = gy + i * row_h
    is_jp, is_avg = name == JAPAN, name == WORLD_AVG[0]
    col = T.accent if is_jp else T.dark if is_avg else BG_GRAY
    bold = is_jp or is_avg
    text(s, MARGIN, ry, name_w, row_h, name, size=15, bold=bold, color=MOSS if bold else SECONDARY,
         align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    bw = bar_w * v / vmax
    rect(s, gx, ry + 8, bw, row_h - 16, col)
    text(s, gx + bw + 8, ry, 80, row_h, f"{v:.1f}%", size=14, bold=bold, color=MOSS if bold else SECONDARY,
         anchor=MSO_ANCHOR.MIDDLE, en=True, spacing=1.0)

# 右側：日本の数字の見せ場
bx, by = 800, 316
big_number(s, bx, by, "日本のEC化率", f"{jp:.1f}", "%", size=72, w=300)
text(s, bx, by + 134, 300, 26, f"世界平均 {WORLD_AVG[1]:.1f}% との差", size=14, color=SECONDARY, spacing=1.0)
text(s, bx, by + 160, 300, 40, f"▲{abs(diff):.1f}pt", size=30, bold=True, color=STRONG, en=True, spacing=1.0)
hline(s, bx, by + 222, 240, BORDER_LIGHT)
text(s, bx, by + 240, 300, 26, f"中国（{dict(rows)['中国']:.1f}%）と比べると", size=14, color=SECONDARY, spacing=1.0)
text(s, bx, by + 266, 300, 40, "3分の1以下", size=24, bold=True, color=MOSS, spacing=1.0)

# 結論の1行と脚注
text(s, MARGIN, 694, CONTENT_W, 44,
     f"日本は[[{jp:.1f}%]]。世界平均の{WORLD_AVG[1]:.1f}%を下回り、中国の3分の1以下", size=28, bold=True)
footnote(s, "※ 出所：経済産業省「令和5年度電子商取引に関する市場調査報告書」。物販系分野、サービス系分野を含む数値")

save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ec_ratio_world.pptx"))
