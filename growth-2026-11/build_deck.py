"""ドムズ 事業成長可能性資料 — 追加ページ「ハナイチの事業構想と AND FLOWER との連携」。

Domuz デザインシステム「発表スライド」型（domuz-deck スキルの deck_lib）で 1 ページを生成する。
図解ページなので数字は持たず、配色はハナイチ（黄）。AND FLOWER はピンク、イネイブラーはライトグリーンで区別する。

    python3 build_deck.py out/hanaichi_platform.pptx
    bash <skill>/scripts/render.sh out/hanaichi_platform.pptx "ハナイチの事業構想" "2026.11 株式会社DOMUZ"
"""
import glob
import os
import sys

_SKILL = sorted(glob.glob(os.path.expanduser("~/.claude/skills/**/domuz-deck/scripts"), recursive=True))
sys.path.insert(0, _SKILL[-1] if _SKILL else os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deck_lib import *  # noqa: E402,F401,F403
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN  # noqa: E402

out = sys.argv[1] if len(sys.argv) > 1 else "out/hanaichi_platform.pptx"
use_theme("hanaichi")

from diagram_lib import arrow_h, arrow_v, box, chip  # noqa: E402

# =====================================================================
# ページ：ハナイチを花業界のプラットフォームに
# =====================================================================
s = content_slide("今後の方針：ハナイチを花業界のプラットフォームに",
                  "毎週の仕入れの上にメディア・人材・注文連携を重ね、AF・イネイブラーと物量を束ねて原価を下げる")

TOP, ROW_B, BAR_Y, BOTTOM = 150, 440, 516, 540
SUP_X, SUP_W = 56, 170           # 仕入れ元
PF_X, PF_W = 296, 500            # ハナイチ
USR_X, USR_W = 876, 196          # 会員店

# ---- 左：仕入れ元（卸・市場・生産者） ----
box(s, SUP_X, TOP, SUP_W, BOTTOM - TOP, BORDER_LIGHT)
text(s, SUP_X + 14, TOP + 12, SUP_W - 28, 24, "卸・市場・生産者", size=16, bold=True, spacing=1.0)
text(s, SUP_X + 14, TOP + 38, SUP_W - 28, 20, "花材・資材の仕入れ元", size=12, color=SECONDARY, spacing=1.0)
for i, lab in enumerate(["卸", "市場", "生産者"]):
    chip(s, SUP_X + 14, TOP + 70 + i * 40, SUP_W - 28, 30, lab, size=13, fill=PALE, line=None)
text(s, SUP_X + 14, 406, SUP_W - 28, 60, "物量があるからこそ、[[原価を下げる]]交渉ができる", size=12, spacing=1.4)
# 仕入れ元 → ハナイチ
text(s, SUP_X + SUP_W, 176, PF_X - SUP_X - SUP_W, 18, "花材・資材", size=11, color=SECONDARY, align=PP_ALIGN.CENTER, spacing=1.0)
arrow_h(s, SUP_X + SUP_W + 6, PF_X - 2, 202, SECONDARY)

# ---- 中央：ハナイチ ----
box(s, PF_X, TOP, PF_W, 250, T.accent, weight=2.5)
text(s, PF_X + 16, TOP + 10, 110, 28, "ハナイチ", size=20, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
text(s, PF_X + 120, TOP + 10, PF_W - 136, 28, "花や植物で商売する事業者向けの仕入れ EC（ToB）", size=13,
     color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
# 土台：仕入れ EC
rect(s, PF_X + 16, TOP + 44, PF_W - 32, 50, T.light)
text(s, PF_X + 28, TOP + 44, PF_W - 56, 50,
     ["**花材・資材・観葉植物の仕入れ EC**", "毎週買う ＝ 会員店の通常の仕入れフローに乗る"],
     size=13, anchor=MSO_ANCHOR.MIDDLE, spacing=1.25)
text(s, PF_X + 16, TOP + 102, PF_W - 32, 18, "＋ 仕入れ以外のサービスを重ねる（毎週の来訪が土台）", size=12,
     color=SECONDARY, spacing=1.0)
services = [
    ("メディア", "業界向けに情報を発信し、広告費を得る"),
    ("人材紹介・求人", "人手が足りない小売店に、人材と求人を紹介する"),
    ("注文の連携", "AND FLOWER の受注を会員店が制作・配達（花キューピット型）"),
]
CW, CG = 148, 12
for i, (head, body) in enumerate(services):
    cx = PF_X + 16 + i * (CW + CG)
    chip(s, cx, TOP + 124, CW, 112, "", band=T.accent)
    text(s, cx + 10, TOP + 134, CW - 20, 22, head, size=14, bold=True, spacing=1.0)
    text(s, cx + 10, TOP + 158, CW - 20, 70, body, size=12, color=SECONDARY, spacing=1.35)

# ハナイチ ↔ 会員店
text(s, PF_X + PF_W, 192, USR_X - PF_X - PF_W, 18, "商品とサービス", size=11, color=SECONDARY, align=PP_ALIGN.CENTER, spacing=1.0)
arrow_h(s, PF_X + PF_W + 6, USR_X - 2, 218, SECONDARY)
text(s, PF_X + PF_W, 292, USR_X - PF_X - PF_W, 18, "毎週の定期利用", size=11, color=SECONDARY, align=PP_ALIGN.CENTER, spacing=1.0)
arrow_h(s, USR_X - 6, PF_X + PF_W + 2, 318, SECONDARY)

# ---- 右：会員店 ----
box(s, USR_X, TOP, USR_W, 250, BORDER_LIGHT)
text(s, USR_X + 14, TOP + 12, USR_W - 28, 24, "花屋・植物屋", size=16, bold=True, spacing=1.0)
text(s, USR_X + 14, TOP + 38, USR_W - 28, 20, "花や植物で商売をする事業者", size=12, color=SECONDARY, spacing=1.0)
for i, lab in enumerate(["花材・資材を毎週仕入れる", "AND FLOWER の注文", "情報と人材を得る"]):
    chip(s, USR_X + 14, TOP + 70 + i * 38, USR_W - 28, 30, lab, size=11, fill=PALE, line=None)
text(s, USR_X + 14, TOP + 190, USR_W - 28, 50, "仕入れも注文も得られる、[[粘着性の高いサービス]]に", size=12, spacing=1.4)

# ---- 下段：AND FLOWER・イネイブラーとの連携 ----
AF_X, EN_X, BW, BH = PF_X, PF_X + 256, 244, 68
box(s, AF_X, ROW_B, BW, BH, FLOWER, weight=2.0)
text(s, AF_X + 12, ROW_B + 6, 110, 22, "AND FLOWER", size=14, bold=True, color=FLOWER, en=True, spacing=1.0)
text(s, AF_X + 132, ROW_B + 6, BW - 144, 22, "C 向け花 EC", size=11, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
text(s, AF_X + 12, ROW_B + 30, BW - 24, 36,
     ["受注を会員店に渡し、制作・配達してもらう", "ロスの花はハナイチのタイムセールで売る"], size=11, spacing=1.35)
box(s, EN_X, ROW_B, BW, BH, LIGHT, weight=2.0)
text(s, EN_X + 12, ROW_B + 6, 130, 22, "生花イネイブラー", size=14, bold=True, spacing=1.0)
text(s, EN_X + 130, ROW_B + 6, BW - 142, 22, "異業種に花を供給", size=11, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
text(s, EN_X + 12, ROW_B + 30, BW - 24, 36,
     ["ギフト同梱・法人案件で花材を大量に使う", "ハナイチと同じ花材・資材を共同で仕入れる"], size=11, spacing=1.35)
# AND FLOWER → ハナイチ（受注の連携・ロス品）
arrow_v(s, AF_X + 16, ROW_B - 2, TOP + 252, FLOWER)
text(s, AF_X + 28, TOP + 254, 90, 32, "受注の連携", size=11, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
arrow_v(s, AF_X + 118, ROW_B - 2, TOP + 252, FLOWER)
text(s, AF_X + 130, TOP + 254, 124, 32, "ロス品→タイムセール", size=11, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
# イネイブラー → ハナイチ（需要を束ねる）
arrow_v(s, EN_X + 16, ROW_B - 2, TOP + 252, LIGHT)
text(s, EN_X + 28, TOP + 254, 200, 32, "花材・資材の需要を持ち込む", size=11, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
# 共同仕入れの帯 → 仕入れ元
rect(s, PF_X, BAR_Y, PF_W, BOTTOM - BAR_Y, T.light)
text(s, PF_X, BAR_Y, PF_W, BOTTOM - BAR_Y, "3 事業の物量を束ねた共同仕入れ：卸・生産者と直接交渉し、原価を下げる",
     size=12, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
text(s, SUP_X + SUP_W, 506, PF_X - SUP_X - SUP_W, 18, "直接交渉", size=11, color=SECONDARY, align=PP_ALIGN.CENTER, spacing=1.0)
arrow_h(s, PF_X - 6, SUP_X + SUP_W + 2, 528, T.dark, weight=2.0)

# ---- 4 つの効き方 ----
BY = 554
benefits = [
    ("① 仕入れが毎週の習慣になる", "通常の仕入れフローに乗るので会員店は毎週使う。離脱しにくい土台ができる"),
    ("② 仕入れ以外の収益が増える", "メディアの広告費、人材紹介の手数料、注文連携の手数料が仕入れの粗利に乗る"),
    ("③ AF の制作・配達網になる", "会員店が AND FLOWER の受注を制作・配達し、ロス品はタイムセールで現金化。双方の粘着性が上がる"),
    ("④ 仕入れ力で原価が下がる", "3 事業の物量を束ねて卸・生産者と直接交渉。ハナイチ・AF・イネイブラー全部の原価に効く"),
]
COLW, COLG = 238, 21
for i, (head, body) in enumerate(benefits):
    x = MARGIN + i * (COLW + COLG)
    rect(s, x, BY, COLW, 4, T.accent)
    text(s, x, BY + 14, COLW, 24, head, size=14, bold=True, spacing=1.0)
    text(s, x, BY + 42, COLW, 60, body, size=12, color=SECONDARY, spacing=1.4)

# ---- 結論と補足 ----
text(s, MARGIN, 654, CONTENT_W, 56,
     "ハナイチを「仕入れ EC」で終わらせず、会員店が毎週使う導線の上に[[仕入れ以外のサービス]]を重ね、"
     "AND FLOWER・イネイブラーと[[物量を束ねて]]花業界のプラットフォームにする。", size=18, bold=True, spacing=1.45)
text(s, MARGIN, 716, CONTENT_W, 36,
     "注文の連携は花キューピットのように、AND FLOWER の受注を会員店に渡して制作・配達してもらう形。"
     "会員店は仕入れも注文も得られ、ハナイチは配達網を持たずに全国へ届けられる。", size=13, color=SECONDARY, spacing=1.3)
footnote(s, "※ 事業構想の段階。各サービスの開始時期・料率は未定。AF＝AND FLOWER")

os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
save(out)
