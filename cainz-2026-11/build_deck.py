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
import math
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


def arrow_to(s, p0, p1, color=BORDER_LIGHT, weight=1.5):
    """p0 から p1 へ向かう矢印（斜めでも可）。先端の三角は進行方向に回す。"""
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    polyline(s, [(x0, y0), (x1 - ux * 8, y1 - uy * 8)], color, weight=weight)
    tri = rect(s, x1 - ux * 6 - 6, y1 - uy * 6 - 6, 12, 12, color, shape=MSO_SHAPE.ISOSCELES_TRIANGLE)
    tri.rotation = math.degrees(math.atan2(dx, -dy)) % 360


ROLE_LABELS = [(1, "Domuzが受託して開始"), (2, "共同で構築"), (3, "共同で投資"), (0, "カインズ様の売り場（そのまま）")]


def role_legend(s, y):
    """箱の色の凡例: 色付きの小さな箱＋説明を横に並べる。"""
    x = MARGIN
    text(s, x, y, 60, 20, "箱の色", size=12, color=MUTED, spacing=1.0)
    x += 56
    for role, lab in ROLE_LABELS:
        st = STYLE[role]
        r = rect(s, x, y + 1, 28, 18, st["fill"], line=st["line"] or st["fill"], weight=1.5, dash=st["dash"],
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        r.adjustments[0] = 0.2
        text(s, x + 36, y, 260, 20, lab, size=12, color=SECONDARY, spacing=1.0)
        x += 36 + int(sum(1.0 if ord(ch) > 0x7F else 0.6 for ch in lab) * 12) + 28


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

role_legend(s, 712)
footnote(s, "※ 各STEPの範囲と条件は、前のSTEPの実績をもとに都度合意して進める。")

# =====================================================================
# 2ページ目: OMO（来店 → 購入 → サポート → CRM の循環。認知・調べるは円の外から入る始点）
# =====================================================================
s = content_slide("店舗とECをまたいで、購入後も回り続ける循環をつくる",
                  "OMO ｜ 認知・調べるを入口に、来店 → 購入 → サポート → CRM を一つの循環として回す")

CX, CY, R = 452, 478, 168
NW, NH = 168, 66
# 円（矢印つきのリング）
rect(s, CX - R, CY - R, 2 * R, 2 * R, None, line=T.accent, weight=3.0, shape=MSO_SHAPE.OVAL)
for deg in (315, 45, 135):  # 225° は入口の矢印が入るので省く
    th = math.radians(deg)
    ax, ay = CX + R * math.cos(th), CY + R * math.sin(th)
    tri = rect(s, ax - 7, ay - 7, 14, 14, T.accent, shape=MSO_SHAPE.ISOSCELES_TRIANGLE)
    tri.rotation = (deg + 180) % 360  # 時計回りの接線方向（三角は既定で上向き）
# 中央
text(s, CX - 100, CY - 44, 200, 40, "OMO", size=34, bold=True, color=T.dark, en=True,
     align=PP_ALIGN.CENTER, spacing=1.0)
text(s, CX - 110, CY + 2, 220, 44, ["店舗とECをまたいで", "回り続けるお客様"], size=13, color=SECONDARY,
     align=PP_ALIGN.CENTER, spacing=1.3)

# 円上の4つの工程（左 → 上 → 右 → 下 の時計回り）
NODES = [  # (角度, 工程, 中身, 役割)
    (180, "来店",             "オンライン／店舗",            0),
    (270, "購入",             "カインズEC・店舗",            0),
    (0,   "カスタマーサポート", "CSチーム＋アプリ",            1),
    (90,  "CRM",              "メルマガ・LINE・アプリ・SNS・DM", 1),
]
def node(s, cx, cy, name, body, role, w=NW, h=NH):
    st = STYLE[role]
    r = rect(s, cx - w / 2, cy - h / 2, w, h, st["fill"], line=st["line"], weight=2.0, dash=st["dash"],
             shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    r.adjustments[0] = 0.12
    text(s, cx - w / 2 + 6, cy - h / 2 + 10, w - 12, 24, name, size=15, bold=True, color=st["fg"],
         align=PP_ALIGN.CENTER, spacing=1.0)
    text(s, cx - w / 2 + 6, cy - h / 2 + 36, w - 12, 18, body, size=10, color=st["sub"],
         align=PP_ALIGN.CENTER, spacing=1.0)

for deg, name, body, role in NODES:
    th = math.radians(deg)
    node(s, CX + R * math.cos(th), CY + R * math.sin(th), name, body, role)

# 入口: 認知 → 調べる → 来店（円の左上から「ピヨっと」出ている始点）
ENTRY = [((150, 222), "認知", "SNS・TV・口コミ・AIO", 1), ((238, 330), "調べる", "検索・比較・AI", 0)]
for (ex, ey), name, body, role in ENTRY:
    node(s, ex, ey, name, body, role, w=152, h=60)
text(s, 56, 160, 200, 20, "始点（入口）", size=12, color=MUTED, spacing=1.0)
arrow_to(s, (176, 252), (212, 300), MUTED, weight=2.0)           # 認知 → 調べる
arrow_to(s, (262, 360), (CX - R - 4, CY - NH / 2 - 2), MUTED, weight=2.0)  # 調べる → 来店

# 右の説明
EX, EW = 728, 344
text(s, EX, 150, EW, 22, "循環で何が変わるか", size=15, bold=True, spacing=1.0)
EXPL = [
    (1, "入口", "SNS・TV・口コミ・AIOで知り、検索やAIで調べる。", "SNS・発信とコンテンツはDomuzが受託"),
    (0, "来店", "オンラインでも店舗でも、同じお客様として迎える。", "カインズ様の売り場（そのまま）"),
    (0, "購入", "ECで買って店舗で受け取る、店舗で見てECで買う。", "どちらでも同じ体験に"),
    (1, "カスタマーサポート", "CSチームとアプリで、買ったあとの育て方まで伴走。", "枯らさない体験が次の購入をつくる"),
    (1, "CRM", "メルマガ・LINE・アプリ・SNS・DMで呼び戻す。", "来店に戻り、循環が回り続ける"),
]
ey = 186
for role, name, body, note in EXPL:
    st = STYLE[role]
    r = rect(s, EX, ey + 3, 14, 14, st["fill"], line=st["line"] or st["fill"], weight=1.5, dash=st["dash"],
             shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    r.adjustments[0] = 0.2
    text(s, EX + 24, ey, EW - 24, 22, name, size=14, bold=True, spacing=1.0)
    text(s, EX + 24, ey + 26, EW - 24, 22, body, size=12, color=MOSS, spacing=1.0)
    text(s, EX + 24, ey + 48, EW - 24, 20, note, size=11, color=SECONDARY, spacing=1.0)
    ey += 96

role_legend(s, 712)
footnote(s, "※ OMO：Online Merges with Offline。店舗とECの区別なく、一人のお客様の体験としてつなぐこと。")

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cainz_proposal.pptx")
save(OUT)
print("wrote", OUT)
