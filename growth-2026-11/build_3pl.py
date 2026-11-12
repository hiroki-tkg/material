"""ドムズ 事業成長可能性資料 — 追加ページ「川崎拠点（高付加価値 3PL）を軸にした同梱出荷の全体図」。

ギフティ様 2026.11 定例資料 p.13「イネイブラー商品を自社 EC でも販売」の図を更新したもの。図だけのページ。
  - 中央は Domuz 川崎拠点（高付加価値 3PL 倉庫）。その下に、川崎に準じて同じ規格で出荷する連携倉庫（SBS・佐川・ヤマト等）を並列に置く
  - 右は取引先 EC と、Domuz の販売チャネル（AND FLOWER・楽天・Amazon・LINE ギフト等）を並列に置く

    python3 build_3pl.py out/kawasaki_3pl.pptx
"""
import glob
import os
import sys

_SKILL = sorted(glob.glob(os.path.expanduser("~/.claude/skills/**/domuz-deck/scripts"), recursive=True))
sys.path.insert(0, _SKILL[-1] if _SKILL else os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deck_lib import *  # noqa: E402,F401,F403
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN  # noqa: E402
from diagram_lib import arrow_h, arrow_v, box, chip  # noqa: E402

out = sys.argv[1] if len(sys.argv) > 1 else "out/kawasaki_3pl.pptx"
use_theme("domuz")

s = content_slide("川崎拠点を軸に、取引先の商品を全チャネルで同梱出荷",
                  "取引先の商品を預かり、取引先 EC と Domuz の全チャネルで同じセットを販売。倉庫は川崎に準じて拡張")

TOP = 150
# ---- 左：取引先 ----
CL_X, CL_W = 56, 176
box(s, CL_X, TOP, CL_W, 490, BORDER_LIGHT)
text(s, CL_X + 14, TOP + 12, CL_W - 28, 24, "取引先", size=16, bold=True, spacing=1.0)
text(s, CL_X + 14, TOP + 38, CL_W - 28, 40, "商品を Domuz の拠点へまとめて納品", size=12, color=SECONDARY, spacing=1.3)
for i, lab in enumerate(["キャンディ", "スープ", "コスメ", "スイーツ"]):
    chip(s, CL_X + 14, TOP + 90 + i * 38, CL_W - 28, 30, lab, size=13, fill=PALE, line=None, align=PP_ALIGN.CENTER)
text(s, CL_X + 14, TOP + 242, CL_W - 28, 18, "など", size=11, color=MUTED, align=PP_ALIGN.RIGHT, spacing=1.0)
text(s, CL_X + 14, 560, CL_W - 28, 70, "納品先は川崎でも連携倉庫でも同じ手順。取引先の出荷作業は発生しない", size=12, color=SECONDARY, spacing=1.35)

# ---- 中央：Domuz 川崎拠点 ----
HB_X, HB_W, HB_Y, HB_H = 290, 400, TOP, 320
box(s, HB_X, HB_Y, HB_W, HB_H, LIGHT, weight=2.5)
text(s, HB_X + 16, HB_Y + 10, 170, 28, "Domuz 川崎拠点", size=20, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
text(s, HB_X + 190, HB_Y + 10, HB_W - 206, 28, "高付加価値 3PL 倉庫", size=13, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
text(s, HB_X + 16, HB_Y + 42, HB_W - 32, 20, "取引先の商品を委託在庫として保管し、花とセットにして発送する", size=12, color=SECONDARY, spacing=1.0)
text(s, HB_X + 16, HB_Y + 70, 200, 18, "取引先の商品", size=12, bold=True, spacing=1.0)
for i, lab in enumerate(["キャンディ", "スープ", "コスメ", "スイーツ"]):
    chip(s, HB_X + 16 + i * 94, HB_Y + 90, 84, 32, lab, size=12, align=PP_ALIGN.CENTER)
text(s, HB_X + 16, HB_Y + 126, 24, 24, "＋", size=16, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
chip(s, HB_X + 44, HB_Y + 128, HB_W - 60, 36, "**AND FLOWER の花**（ミニブーケ・フラワーボックス等）", size=12, line=FLOWER, color=FLOWER)
text(s, HB_X + 16, HB_Y + 170, 24, 24, "＝", size=16, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
chip(s, HB_X + 44, HB_Y + 172, HB_W - 60, 36, "ギフトボックスにセットして同梱出荷", size=13, fill=LIGHT, line=None, bold=True, color=WHITE)
text(s, HB_X + 16, HB_Y + 216, HB_W - 32, 18, "※ 受注・顧客データも Domuz に蓄積", size=11, color=SECONDARY, align=PP_ALIGN.RIGHT, spacing=1.0)
hline(s, HB_X + 16, HB_Y + 244, HB_W - 32)
text(s, HB_X + 16, HB_Y + 252, HB_W - 32, 60,
     ["**川崎で規格をつくる**", "セット内容・箱・ラベル・出荷手順を決め、連携倉庫へ横展開する"], size=12, color=SECONDARY, spacing=1.35)

# 取引先 → 川崎拠点
text(s, CL_X + CL_W, 282, HB_X - CL_X - CL_W, 18, "納品", size=11, color=SECONDARY, align=PP_ALIGN.CENTER, spacing=1.0)
arrow_h(s, CL_X + CL_W + 6, HB_X - 2, 306, SECONDARY)

# ---- 中央下：連携倉庫（川崎に準じる） ----
WH_Y, WH_H = 500, 140
box(s, HB_X, WH_Y, HB_W, WH_H, LIGHT, weight=1.5, dash=True)
text(s, HB_X + 16, WH_Y + 8, HB_W - 32, 24, "連携倉庫　川崎拠点に準じて、同じ規格で出荷する", size=14, bold=True, spacing=1.0)
for i, lab in enumerate(["SBS 倉庫", "佐川倉庫", "ヤマト倉庫", "…"]):
    chip(s, HB_X + 16 + i * 94, WH_Y + 42, 84, 32, lab, size=12, align=PP_ALIGN.CENTER)
text(s, HB_X + 16, WH_Y + 84, HB_W - 32, 50, "物量と商材に応じて拠点を増やせる。川崎の規格と Domuz の受注データで運用は共通", size=12,
     color=SECONDARY, spacing=1.35)
# 川崎拠点 → 連携倉庫（規格の横展開）
arrow_v(s, HB_X + 40, HB_Y + HB_H + 2, WH_Y - 2, LIGHT, weight=2.0)
text(s, HB_X + 54, HB_Y + HB_H + 2, 200, 26, "規格・運用を横展開", size=11, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
# 取引先 → 連携倉庫
text(s, CL_X + CL_W, 536, HB_X - CL_X - CL_W, 18, "納品", size=11, color=SECONDARY, align=PP_ALIGN.CENTER, spacing=1.0)
arrow_h(s, CL_X + CL_W + 6, HB_X - 2, 560, SECONDARY, dash=True)

# ---- 右：取引先の EC と Domuz の販売チャネル ----
EC_X, EC_W = 750, 200
box(s, EC_X, TOP, EC_W, 140, BORDER_LIGHT)
text(s, EC_X + 14, TOP + 12, EC_W - 28, 24, "取引先の EC", size=15, bold=True, spacing=1.0)
text(s, EC_X + 14, TOP + 40, EC_W - 28, 90,
     ["イネイブラー", "取引先が自社の EC で販売し、", "注文情報を Domuz へ連携"], size=12, color=SECONDARY, spacing=1.35)
CH_Y, CH_H = 320, 320
box(s, EC_X, CH_Y, EC_W, CH_H, LIGHT, weight=2.0)
text(s, EC_X + 14, CH_Y + 12, EC_W - 28, 24, "Domuz の販売チャネル", size=15, bold=True, spacing=1.0)
text(s, EC_X + 14, CH_Y + 40, EC_W - 28, 36, "全く同じセット商品を Domuz が販売・出荷", size=12, color=SECONDARY, spacing=1.3)
channels = [("AND FLOWER EC", FLOWER), ("楽天市場", None), ("Amazon", None), ("LINE ギフト", None), ("Yahoo! ショッピング など", None)]
for i, (lab, band) in enumerate(channels):
    chip(s, EC_X + 14, CH_Y + 84 + i * 42, EC_W - 28, 34, lab, size=12, band=band or LIGHT,
         bold=band is not None, color=band or MOSS)
# EC → 川崎拠点（注文情報）
text(s, HB_X + HB_W, 196, EC_X - HB_X - HB_W, 18, "注文情報", size=11, color=SECONDARY, align=PP_ALIGN.CENTER, spacing=1.0)
arrow_h(s, EC_X - 6, HB_X + HB_W + 2, 222, SECONDARY)
text(s, HB_X + HB_W, 376, EC_X - HB_X - HB_W, 18, "注文", size=11, color=SECONDARY, align=PP_ALIGN.CENTER, spacing=1.0)
arrow_h(s, EC_X - 6, HB_X + HB_W + 2, 402, SECONDARY)
text(s, HB_X + HB_W, 536, EC_X - HB_X - HB_W, 18, "注文", size=11, color=SECONDARY, align=PP_ALIGN.CENTER, spacing=1.0)
arrow_h(s, EC_X - 6, HB_X + HB_W + 2, 560, SECONDARY, dash=True)

# ---- 右端：お客様 ----
CU_X, CU_W, CU_Y, CU_H = 980, 92, TOP, 530
rect(s, CU_X, CU_Y, CU_W, CU_H, PALE)
rect(s, CU_X + CU_W / 2 - 14, 372, 28, 28, MOSS, shape=MSO_SHAPE.OVAL)
rect(s, CU_X + CU_W / 2 - 22, 404, 44, 26, MOSS, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
text(s, CU_X, 438, CU_W, 22, "お客様", size=13, bold=True, align=PP_ALIGN.CENTER, spacing=1.0)
# 購入
text(s, EC_X + EC_W, 196, CU_X - EC_X - EC_W, 18, "購入", size=11, color=SECONDARY, align=PP_ALIGN.CENTER, spacing=1.0)
arrow_h(s, CU_X - 2, EC_X + EC_W + 2, 222, SECONDARY)
text(s, EC_X + EC_W, 376, CU_X - EC_X - EC_W, 18, "購入", size=11, color=SECONDARY, align=PP_ALIGN.CENTER, spacing=1.0)
arrow_h(s, CU_X - 2, EC_X + EC_W + 2, 402, SECONDARY)
# 発送（川崎拠点 → お客様、連携倉庫 → お客様）
text(s, EC_X, 288, EC_W, 18, "発送（拠点から直接お客様へ）", size=11, color=SECONDARY, align=PP_ALIGN.CENTER, spacing=1.0)
arrow_h(s, HB_X + HB_W + 2, CU_X - 2, 308, MOSS, weight=2.0)
vline(s, HB_X + HB_W / 2, WH_Y + WH_H, 22, MOSS, 2.0)
hline(s, HB_X + HB_W / 2, WH_Y + WH_H + 22, 0, MOSS, 2.0)
text(s, EC_X, WH_Y + WH_H + 2, EC_W, 18, "発送", size=11, color=SECONDARY, align=PP_ALIGN.CENTER, spacing=1.0)
arrow_h(s, HB_X + HB_W / 2, CU_X - 2, WH_Y + WH_H + 22, MOSS, weight=2.0)

footnote(s, "※ 在庫は取引先からの委託在庫、Domuz チャネルでは消化仕入（売れた分を精算）を想定。倉庫名・EC 名は例で、物量と商材に応じて選ぶ")

os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
save(out)
