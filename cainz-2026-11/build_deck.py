"""カインズ様向け 植物EC共同事業のご提案（1枚）— Domuz「発表スライド」型で .pptx を生成する。

使い方:
    python3 build_deck.py            # cainz_proposal.pptx を書き出す
    bash <domuz-deck>/scripts/render.sh cainz_proposal.pptx "..." "..."   # PDF / HTML / 確認用 PNG

読ませ方: 左の列はモノの流れ（産地 → お客様）、右の列は進め方の順番（STEP 1 → 3、下から上）。
下流の受託から入り、仕入れ・物流、産地へと上流に広げ、最後に資本で固める。
産地の具体名（沖縄・指宿など）と出資スキームは意図して書かない（STEP 2 の合意後に開示・協議）。
"""
import glob
import os
import sys

SKILL = glob.glob(os.path.expanduser("~/.claude/skills/synced/*/domuz-deck/scripts"))
sys.path.insert(0, SKILL[0] if SKILL else os.path.join(os.path.dirname(__file__), "deck_lib"))
from deck_lib import *  # noqa: E402,F401

use_theme("domuz")

# ---- 内容 -------------------------------------------------------------
# 左の列（上＝産地、下＝お客様）。step は進め方の番号。
AREAS = [  # (領域, 中身, STEP)
    ("産地の共同開発",       "海外種苗（台湾・雲南）× 国内での大規模生産", 3),
    ("共同サプライチェーン", "卸を介さない産地直送・仕入れの共通化",       2),
    ("発送拠点の開発・運営", "生体を扱える出荷・保管拠点",                 2),
    ("EC運営（イネイブラー）", "カインズEC（植物）の発送設備・梱包・CS",   1),
    ("SNS・発信の運営",      "観葉・ガーデン系コンテンツの受託",           1),
]
STEPS = {  # STEP → (見出し, カインズ様にとっての意味)
    1: ("Domuzが受託して開始",
        ["初期投資なしで、生体を扱える発送・梱包・CSと",
         "発信の体制をそのまま使える"]),
    2: ("仕入れ・物流を共同構築",
        ["受託で見えた売れ筋を根拠に仕入れを共同で最適化。",
         "卸を介さず、原価と鮮度を改善する"]),
    3: ("共同で投資・開発",
        ["海外種苗 × 国内大規模生産を共同で投資・開発。",
         "両社でしか作れない商品と供給力を持つ"]),
}
# STEP の間をつなぐ根拠（下の STEP の成果が、上の STEP に進む理由になる）
BRIDGE = {
    1: "受託で見えた出荷量・売れ筋が、共同仕入れの根拠になる",
    2: "共同仕入れの実績と数量が、産地投資の判断根拠になる",
}
GOAL = ("資本提携で一体化", "産地からお客様まで、互いに離れられない長期の共同事業に")

# ---- レイアウト ---------------------------------------------------------
AX_X = 56                  # 左端の軸（産地 → お客様）
BOX_X, BOX_W = 104, 404    # 領域の箱
STEP_X, STEP_W = 536, 176  # STEP の帯
WHY_X, WHY_W = 740, 332    # カインズ様にとっての意味
BOX_H, GAP_IN, GAP_STEP = 74, 14, 44
TOP = 172

STYLE = {  # STEP ごとの見た目: 下流（今すぐ）は軽く、上流（将来）ほど濃く
    1: dict(fill=WHITE, line=T.accent, fg=MOSS, sub=SECONDARY),
    2: dict(fill=PALE, line=None, fg=MOSS, sub=SECONDARY),
    3: dict(fill=MOSS, line=None, fg=WHITE, sub=WHITE),
}


def down_arrow(s, cx, y, h, color=BORDER_LIGHT):
    """下向きの矢印（線＋三角）。"""
    vline(s, cx, y, h - 6, color, weight=1.5)
    tri = rect(s, cx - 5, y + h - 8, 10, 8, color, shape=MSO_SHAPE.ISOSCELES_TRIANGLE)
    tri.rotation = 180.0


def up_arrow(s, cx, y, h, color=T.accent):
    """上向きの矢印（三角＋線）。"""
    rect(s, cx - 5, y, 10, 8, color, shape=MSO_SHAPE.ISOSCELES_TRIANGLE)
    vline(s, cx, y + 6, h - 6, color, weight=1.5)


s = content_slide("受託から始め、仕入れ・産地へ広げ、資本で一体化する",
                  "カインズ様との植物EC共同事業のご提案 ｜ お客様側（下流）から産地側（上流）へ、3つのSTEPで進める")

# 列見出し
text(s, BOX_X, 146, BOX_W, 20, "共同で担う領域", size=12, color=MUTED)
text(s, STEP_X, 146, STEP_W, 20, "進め方", size=12, color=MUTED)
text(s, WHY_X, 146, WHY_W, 20, "カインズ様にとっての意味", size=12, color=MUTED)

# 箱の y 座標（上から順に。STEP が変わるところは広めに空ける）
ys = []
y = TOP
for i, (_, _, st) in enumerate(AREAS):
    if i > 0:
        y += BOX_H + (GAP_STEP if AREAS[i - 1][2] != st else GAP_IN)
    ys.append(y)
BOTTOM = ys[-1] + BOX_H

# 左端の軸: 産地 → お客様（モノの流れ）
text(s, AX_X - 8, TOP - 2, 48, 20, "産地", size=12, color=SECONDARY, align=PP_ALIGN.CENTER)
down_arrow(s, AX_X + 16, TOP + 24, BOTTOM - TOP - 48, MUTED)
text(s, AX_X - 8, BOTTOM - 18, 48, 20, "お客様", size=12, color=SECONDARY, align=PP_ALIGN.CENTER)

# 領域の箱と、その間の矢印
for i, ((name, body, st), y) in enumerate(zip(AREAS, ys)):
    st_ = STYLE[st]
    rect(s, BOX_X, y, BOX_W, BOX_H, st_["fill"], line=st_["line"], weight=2.0,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE).adjustments[0] = 0.08
    text(s, BOX_X + 20, y + 12, BOX_W - 40, 26, name, size=18, bold=True, color=st_["fg"], spacing=1.0)
    text(s, BOX_X + 20, y + 42, BOX_W - 40, 20, body, size=13, color=st_["sub"], spacing=1.0)
    if i + 1 < len(AREAS):
        gap = ys[i + 1] - (y + BOX_H)
        down_arrow(s, BOX_X + BOX_W / 2, y + BOX_H + 3, gap - 6, BORDER_LIGHT)

# STEP の帯（同じ STEP の箱をまとめて囲う）と、その右の意味
for st in (3, 2, 1):
    idx = [i for i, a in enumerate(AREAS) if a[2] == st]
    y0, y1 = ys[idx[0]], ys[idx[-1]] + BOX_H
    st_ = STYLE[st]
    rect(s, STEP_X, y0, STEP_W, y1 - y0, st_["fill"], line=st_["line"], weight=2.0,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE).adjustments[0] = 0.08 * BOX_H / (y1 - y0)
    cy = (y0 + y1) / 2
    text(s, STEP_X, cy - 26, STEP_W, 26, f"STEP {st}", size=22, bold=True, color=st_["fg"],
         align=PP_ALIGN.CENTER, en=True, spacing=1.0)
    text(s, STEP_X, cy + 2, STEP_W, 22, STEPS[st][0], size=13, color=st_["sub"],
         align=PP_ALIGN.CENTER, spacing=1.0)
    # 右: カインズ様にとっての意味（STEP の帯の縦中央に揃える）
    text(s, WHY_X, cy - 22, WHY_W, 48, STEPS[st][1], size=13, color=MOSS, spacing=1.35,
         anchor=MSO_ANCHOR.MIDDLE)
    # 次の STEP へ進む根拠（帯の間）
    if st in BRIDGE:
        gy = y0 - GAP_STEP
        up_arrow(s, STEP_X + STEP_W / 2, gy + 3, GAP_STEP - 6, T.accent)
        text(s, WHY_X, gy + 2, WHY_W, GAP_STEP - 4, "[[↑]] " + BRIDGE[st], size=12, color=SECONDARY,
             anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)

# ゴール: 資本提携で一体化
GY = BOTTOM + 26
rect(s, BOX_X, GY, WHY_X + WHY_W - BOX_X, 62, None, line=MOSS, weight=2.0,
     shape=MSO_SHAPE.ROUNDED_RECTANGLE).adjustments[0] = 0.12
text(s, BOX_X + 24, GY, 230, 62, "GOAL", size=22, bold=True, color=T.dark, en=True,
     anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
text(s, BOX_X + 110, GY + 10, 820, 26, GOAL[0], size=20, bold=True, spacing=1.0)
text(s, BOX_X + 110, GY + 36, 820, 20, GOAL[1], size=13, color=SECONDARY, spacing=1.0)

footnote(s, "※ 各STEPの範囲と条件は、前のSTEPの実績をもとに都度合意して進める。資本面はまず方向性の共有から。")

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cainz_proposal.pptx")
save(OUT)
print("wrote", OUT)
