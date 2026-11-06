"""カインズ様向け 植物EC共同事業のご提案（1枚）— Domuz「発表スライド」型で .pptx を生成する。

使い方:
    python3 build_deck.py            # cainz_proposal.pptx を書き出す
    bash <domuz-deck>/scripts/render.sh cainz_proposal.pptx "..." "..."   # PDF / HTML / 確認用 PNG

構成: 上段がモノの流れ（種苗 → 生産 → 流通 → 管理・梱包・発送 → お客様へ）、
下段がお客様の流れ（認知 → 調べる → 来店 → 購入 → サポート → CRM → 再来店・再購入）。
各工程の箱を「誰が担うか」で色分けし、下に「どこから始めるか」（STEP 1 → 3 → GOAL）を置く。
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
# 役割: 1/2/3 = 共同化する STEP、0 = カインズ様の売り場（そのまま）
# (工程, いまの中身, ご提案, 役割)
GOODS = [  # 上段: モノの流れ。列 0〜3 を使い、「管理・梱包・発送」が下段の「購入」の真上に来る
    ("種苗",           "海外種苗（台湾・雲南）", "共同で調達・開発",   3),
    ("生産",           "国内での大規模生産",     "共同で投資・生産",   3),
    ("流通",           "卸を介さない産地直送",   "仕入れの共通化",     2),
    ("管理・梱包・発送", "生体を扱える拠点・梱包", "Domuzが受託",      1),
]
CUSTOMER = [  # 下段: お客様の流れ（6列）
    ("認知",             "SNS・TV・口コミ・AIO", "SNS・発信を受託",     1),
    ("調べる",           "検索・比較・AI",       "カインズ様の集客",     0),
    ("来店",             "オンライン／店舗",     "カインズ様の売り場",   0),
    ("購入",             "カインズEC・店舗",     "カインズ様の売り場",   0),
    ("カスタマーサポート", "CSチーム＋アプリ",   "Domuzが受託",         1),
    ("CRM",              "再来店・再購入へ",     "アプリで育て方を支援", 1),
]
LOOP = ("再来店・再購入", 2)  # CRM から戻る先の列（来店）
KEY = ["売り場（来店・購入）はカインズ様の強み。",
       "その前後をDomuzが担い、受託で見えた",
       "売れ筋と数量を根拠に、産地まで一緒に広げる。"]
STEPS = [  # どこから始めるか（左から順に）
    ("STEP 1", "Domuzが受託して開始", "梱包・発送、SNS、CS、アプリ", 1),
    ("STEP 2", "仕入れ・物流を共同構築", "受託で見えた売れ筋が根拠", 2),
    ("STEP 3", "種苗・生産を共同で投資", "共同仕入れの実績が根拠", 3),
    ("GOAL",   "資本提携で一体化", "産地からお客様まで長期の共同事業に", 4),
]

# ---- 見た目 -------------------------------------------------------------
STYLE = {  # 役割ごと。今すぐ始める STEP 1 は軽く、上流（将来）ほど濃く。売り場は灰の枠
    0: dict(fill=WHITE, line=BORDER_LIGHT, fg=SECONDARY, sub=SECONDARY, offer=MUTED, dash=True),
    1: dict(fill=WHITE, line=T.accent, fg=MOSS, sub=SECONDARY, offer=T.dark, dash=False),
    2: dict(fill=PALE, line=None, fg=MOSS, sub=SECONDARY, offer=T.dark, dash=False),
    3: dict(fill=MOSS, line=None, fg=WHITE, sub=WHITE, offer=WHITE, dash=False),
    4: dict(fill=WHITE, line=MOSS, fg=MOSS, sub=SECONDARY, offer=MOSS, dash=False),
}
COLS, GAP = 6, 16
BW = (CONTENT_W - GAP * (COLS - 1)) / COLS  # 156
BH = 112


def col_x(i):
    return MARGIN + i * (BW + GAP)


def right_arrow(s, x, cy, color=BORDER_LIGHT):
    """箱と箱の間の右向き矢印（線＋三角）。"""
    hline(s, x + 2, cy, GAP - 10, color, weight=1.5)
    tri = rect(s, x + GAP - 10, cy - 5, 8, 10, color, shape=MSO_SHAPE.ISOSCELES_TRIANGLE)
    tri.rotation = 90.0


def down_arrow(s, cx, y, h, color=BORDER_LIGHT):
    vline(s, cx, y, h - 6, color, weight=1.5)
    tri = rect(s, cx - 5, y + h - 8, 10, 8, color, shape=MSO_SHAPE.ISOSCELES_TRIANGLE)
    tri.rotation = 180.0


def up_arrow_head(s, cx, y, color):
    rect(s, cx - 5, y, 10, 8, color, shape=MSO_SHAPE.ISOSCELES_TRIANGLE)


def box(s, x, y, w, h, name, body, offer, role, name_size=15):
    st = STYLE[role]
    r = rect(s, x, y, w, h, st["fill"], line=st["line"], weight=2.0, dash=st["dash"],
             shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    r.adjustments[0] = 0.08
    text(s, x + 8, y + 12, w - 16, 24, name, size=name_size, bold=True, color=st["fg"], spacing=1.0,
         align=PP_ALIGN.CENTER)
    text(s, x + 8, y + 38, w - 16, 18, body, size=11, color=st["sub"], spacing=1.0, align=PP_ALIGN.CENTER)
    hline(s, x + 14, y + h - 34, w - 28, WHITE if role == 3 else BORDER_LIGHT, weight=0.75)
    text(s, x + 8, y + h - 28, w - 16, 20, offer, size=11, bold=True, color=st["offer"], spacing=1.0,
         align=PP_ALIGN.CENTER)


def row(s, items, y, start_col=0):
    for i, (name, body, offer, role) in enumerate(items):
        c = start_col + i
        box(s, col_x(c), y, BW, BH, name, body, offer, role)
        if i + 1 < len(items):
            right_arrow(s, col_x(c) + BW, y + BH / 2)


s = content_slide("売り場の前後を一緒に。受託から始め、産地まで広げる",
                  "カインズ様との植物EC共同事業のご提案 ｜ 2つの流れのどこを、どの順で一緒にやるか")

# ---- 上段: モノの流れ ----
Y1 = 190
text(s, MARGIN, Y1 - 28, 400, 22, "モノの流れ", size=15, bold=True, spacing=1.0)
text(s, MARGIN + 92, Y1 - 26, 400, 20, "産地からお客様へ", size=12, color=SECONDARY, spacing=1.0)
row(s, GOODS, Y1, start_col=0)
# 右の空き（列 4〜5）に要点
kx = col_x(4)
rect(s, kx, Y1, 2 * BW + GAP, BH, None, line=None)
text(s, kx + 4, Y1 + 2, 2 * BW + GAP - 8, BH - 4, KEY, size=14, color=MOSS, spacing=1.45,
     anchor=MSO_ANCHOR.MIDDLE)

# ---- 下段: お客様の流れ ----
Y2 = Y1 + BH + 80
text(s, MARGIN, Y2 - 28, 400, 22, "お客様の流れ", size=15, bold=True, spacing=1.0)
text(s, MARGIN + 110, Y2 - 26, 400, 20, "認知から再購入まで", size=12, color=SECONDARY, spacing=1.0)
row(s, CUSTOMER, Y2, start_col=0)

# 上段 → 下段: 「管理・梱包・発送」から「購入」へお届け
cx = col_x(3) + BW / 2
down_arrow(s, cx, Y1 + BH + 4, Y2 - (Y1 + BH) - 8, MUTED)
text(s, cx + 10, Y1 + BH + 26, 80, 20, "お届け", size=11, color=SECONDARY, spacing=1.0)

# CRM → 来店 へ戻るループ（箱の下を通す）
ly = Y2 + BH + 22
x_from = col_x(5) + BW / 2
x_to = col_x(LOOP[1]) + BW / 2
vline(s, x_from, Y2 + BH + 2, ly - (Y2 + BH + 2), T.accent, weight=1.5)
hline(s, x_to, ly, x_from - x_to, T.accent, weight=1.5)
vline(s, x_to, Y2 + BH + 10, ly - (Y2 + BH + 10), T.accent, weight=1.5)
up_arrow_head(s, x_to, Y2 + BH + 3, T.accent)
text(s, x_to, ly + 4, x_from - x_to, 18, LOOP[0], size=11, color=T.dark, bold=True, spacing=1.0,
     align=PP_ALIGN.CENTER)

# ---- どこから始めるか ----
Y3 = ly + 60
text(s, MARGIN, Y3 - 28, 400, 22, "どこから始めるか", size=15, bold=True, spacing=1.0)
text(s, MARGIN + 138, Y3 - 26, 600, 20, "前のSTEPの実績を根拠に、次へ進む", size=12, color=SECONDARY,
     spacing=1.0)
SW, SGAP, SH = (CONTENT_W - 3 * 28) / 4, 28, 98
for i, (lab, head, body, role) in enumerate(STEPS):
    st = STYLE[role]
    x = MARGIN + i * (SW + SGAP)
    r = rect(s, x, Y3, SW, SH, st["fill"], line=st["line"], weight=2.0, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    r.adjustments[0] = 0.08
    text(s, x + 16, Y3 + 10, SW - 32, 26, lab, size=20, bold=True, color=st["fg"], en=True, spacing=1.0)
    text(s, x + 16, Y3 + 38, SW - 32, 22, head, size=14, bold=True, color=st["fg"], spacing=1.0)
    text(s, x + 16, Y3 + 62, SW - 32, 20, body, size=11, color=st["sub"], spacing=1.0)
    if i + 1 < len(STEPS):
        ax = x + SW + 6
        hline(s, ax, Y3 + SH / 2, SGAP - 20, T.accent, weight=2.0)
        tri = rect(s, ax + SGAP - 20, Y3 + SH / 2 - 6, 10, 12, T.accent, shape=MSO_SHAPE.ISOSCELES_TRIANGLE)
        tri.rotation = 90.0

footnote(s, "※ 箱の色は担い手：緑枠＝Domuzが受託して開始、灰地＝共同で構築、濃緑＝共同で投資、点線＝カインズ様の売り場（そのまま）。"
            "各STEPの範囲と条件は、前のSTEPの実績をもとに都度合意して進める。")

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cainz_proposal.pptx")
save(OUT)
print("wrote", OUT)
