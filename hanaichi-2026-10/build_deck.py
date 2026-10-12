"""ギフティ様向け ハナイチ 事業エコノミクス資料 — giftee-2026-10 と同じ型（Domuz デザインシステム「発表スライド」）。

データは data_hanaichi.py（管理画面の売上・粗利、Marketing Master の広告費、顧客単位の集計）。
直接固定費は仮置き（FIXED）。社内の集計が出たら差し替える。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from deck_lib import *  # noqa
from deck_lib import _set_font  # noqa
from data_hanaichi import (YM, FY, mi, S, GP, AD, NET, ORDERS, FIXED, FIXED_IS_PLACEHOLDER, LTV25, NEW26, AOV26,
                           GP_RATE26, REPEAT_SHARE, REPEAT_CUSTOMERS, REPEAT_AOV, BIZ_CATEGORIES, fy_sum)

N = len(S)
fy_s, fy_gp, fy_ad, fy_net = fy_sum(S), fy_sum(GP), fy_sum(AD), fy_sum(NET)
FY_NAMES = [f[0] for f in FY]

# =====================================================================
# 1. 表紙
# =====================================================================
s = new_slide()
rect(s, 0, 0, 8, H_PX, LIGHT)
text(s, 96, 250, 960, 40, "株式会社ギフティ様　ご参考資料", size=26, color=SECONDARY)
text(s, 96, 330, 980, 100, "ハナイチ：事業エコノミクスの整理とまとめ", size=56, bold=True, spacing=1.3)
text(s, 96, 450, 960, 40, "売上・粗利・広告費の推移と、今後のエコノミクス", size=24, color=SECONDARY)
text(s, 96, 640, 900, 120, ["2026年10月", "株式会社DOMUZ", "髙木 弘貴"], size=22, color=SECONDARY, spacing=1.5)

# =====================================================================
# 2. 本資料の構成・要約
# =====================================================================
s = content_slide("本資料の構成")
items = [
    ("1", "ハナイチのエコノミクスの整理と経年推移", "24年9月期（2024年2月の開始）〜26年9月期"),
    ("2", "今後の事業におけるエコノミクスの整理", "原価・全体ROAS・直接固定費、LTV/CAC、損益分岐の月商"),
]
y = 260
for n, label, sub in items:
    text(s, 96, y + 16, 80, 64, n, size=60, color=LIGHT, bold=True, en=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, 190, y + 16, 870, 64, label, size=34, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, 190, y + 84, 870, 30, sub, size=20, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    if n != items[-1][0]:
        hline(s, 96, y + 128, 936)
    y += 160
footnote(s, "※ 用語と集計の前提は最終ページにまとめています")

summary_slide = content_slide("ハナイチ")

# =====================================================================
# 章 01：推移
# =====================================================================
divider("01", "ECONOMICS TREND", "ハナイチのエコノミクスの推移", "24年9月期（2024年2月）〜 26年9月期（2026年9月）")

s = content_slide("ハナイチ：月次売上と期別の収益性")
msg = (f"売上は{fy_s[1]:.0f}→{fy_s[2]:.0f}百万円（前期比 +{(fy_s[2] / fy_s[1] - 1) * 100:.0f}%）。"
       f"粗利率{fy_gp[2] / fy_s[2] * 100:.0f}%を保ち、広告費込み粗利は{fy_net[1]:.1f}→{fy_net[2]:.1f}百万円に")
text(s, 56, 104, 1016, 36, msg, size=21, bold=True)
x0, x1 = 214, 914
text(s, x0, 154, 900, 24, "24年9月期（2024年2月）〜26年9月期（2026年9月）　単位：百万円　棒の上は各期の最高月、期名の下は期合計",
     size=14, color=SECONDARY)
top, base = 206, 434
slot = (x1 - x0) / N
bw = slot * 0.66
vmax = max(S)
sy = lambda v: base - (base - top) * v / vmax
for k, (name, a, b) in enumerate(FY):
    idx = range(a, b)
    peak = max(idx, key=lambda i: S[i])
    for i in idx:
        if S[i] <= 0.01:
            continue
        bx = x0 + i * slot + (slot - bw) / 2
        rect(s, bx, sy(S[i]), bw, base - sy(S[i]), LIGHT)
        if i == peak:
            text(s, bx - 20, sy(S[i]) - 26, bw + 40, 22, f"{S[i]:.1f}", size=15, bold=True, align=PP_ALIGN.CENTER, en=True)
    gx = x0 + a * slot
    if k > 0:
        vline(s, gx, 190, base - 190 + 70, BORDER_LIGHT, 1.0, dash=True)
    text(s, gx, base + 12, (b - a) * slot, 26, name, size=17, bold=True, align=PP_ALIGN.CENTER)
    text(s, gx, base + 40, (b - a) * slot, 24, f"{fy_s[k]:.0f}", size=16, color=SECONDARY, align=PP_ALIGN.CENTER, en=True)
hline(s, x0 - 4, base, x1 - x0 + 8, BORDER_LIGHT, 1.5)
hdr = ["期", "売上", "粗利", "粗利率", "広告費", "全体ROAS", "広告費込み粗利", "同率"]
cxs = [56, 190, 290, 410, 520, 620, 740, 950]
cws = [130, 100, 120, 110, 100, 120, 210, 122]
ty = 512
rect(s, 56, ty, 1016, 40, MOSS)
for j, h in enumerate(hdr):
    text(s, cxs[j] + (12 if j == 0 else 0), ty, cws[j] - (0 if j == 0 else 12), 40, h, size=16, color=WHITE, bold=True,
         anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.LEFT if j == 0 else PP_ALIGN.RIGHT)
y = ty + 40
rh = 56
for k in range(3):
    if k == 2:
        rect(s, 56, y, 1016, rh, WATERMARK)
    roas = f"{fy_s[k] / fy_ad[k] * 100:.0f}%" if fy_ad[k] > 0 else "—"
    vals = [FY_NAMES[k], f"{fy_s[k]:.1f}", f"{fy_gp[k]:.1f}", f"{fy_gp[k] / fy_s[k] * 100:.1f}%",
            f"{fy_ad[k]:.1f}" if fy_ad[k] > 0 else "—", roas, f"{fy_net[k]:.1f}", f"{fy_net[k] / fy_s[k] * 100:.1f}%"]
    for j, v in enumerate(vals):
        text(s, cxs[j] + (12 if j == 0 else 0), y, cws[j] - (0 if j == 0 else 12), rh, v, size=19 if j else 17, bold=True,
             color=STRONG if v.startswith("-") else MOSS, anchor=MSO_ANCHOR.MIDDLE,
             align=PP_ALIGN.LEFT if j == 0 else PP_ALIGN.RIGHT)
    y += rh
    hline(s, 56, y, 1016, BORDER_LIGHT)
footnote(s, "※ 税抜・注文日ベース。ハナイチ管理画面の純売上と粗利（粗利＝売上−商品原価・送料・資材・決済手数料。AP/AFの限界利益に相当）。"
            "広告費はMarketing Master（生花の広告のみ）。24年9月期は2024年2月〜9月の8か月")

# ---- 広告投資：月次の広告費・売上・ROAS（24年10月〜26年9月）
s = content_slide("広告投資：生花の新規獲得に広告を投下", "ハナイチの月次の売上・広告費・ROAS（24年10月〜26年9月）　単位：百万円")
i0 = 8
n_ = N - i0
x0, x1 = 120, 1040
slot = (x1 - x0) / n_
cx = lambda i: x0 + (i - i0) * slot + slot / 2
top, base = 190, 440
vmax_ = 7
sy = lambda v: base - (base - top) * v / vmax_
for v in range(0, vmax_ + 1):
    hline(s, x0 - 4, sy(v), x1 - x0 + 4, BORDER_LIGHT if v == 0 else WATERMARK)
    text(s, 60, sy(v) - 11, 50, 22, str(v), size=12, color=MUTED, align=PP_ALIGN.RIGHT, en=True)
for i in range(i0, N):
    bw_ = slot * 0.62
    rect(s, cx(i) - bw_ / 2, sy(S[i]), bw_, base - sy(S[i]), LIGHT)
polyline(s, [(cx(i), sy(AD[i])) for i in range(i0, N)], STRONG, 3.0)
for i in range(i0, N):
    rect(s, cx(i) - 4, sy(AD[i]) - 4, 8, 8, STRONG, shape=MSO_SHAPE.OVAL)
rt, rb = 492, 600
rmax = 1600
ry = lambda v: rb - (rb - rt) * min(v, rmax) / rmax
text(s, 56, rt - 30, 300, 22, "ROAS（売上÷広告費）", size=13, color=SECONDARY, bold=True)
for v in (0, 500, 1000, 1500):
    hline(s, x0 - 4, ry(v), x1 - x0 + 4, BORDER_LIGHT if v == 0 else WATERMARK)
    text(s, 50, ry(v) - 10, 60, 20, f"{v}%", size=11, color=MUTED, align=PP_ALIGN.RIGHT, en=True)
roas_ = [S[i] / AD[i] * 100 if AD[i] > 0 else None for i in range(N)]
pts = [(cx(i), ry(roas_[i])) for i in range(i0, N) if roas_[i] is not None and i >= 11]  # 広告が本格化した25年1月から
polyline(s, pts, MOSS, 2.5)
for i in range(i0, N):
    text(s, cx(i) - 20, rb + 4, 40, 18, f"{YM[i][1]}", size=11, color=MUTED, align=PP_ALIGN.CENTER, en=True)
for lab, i in (("25年9月期", 8), ("26年9月期", 20)):
    text(s, cx(i) - slot / 2, rb + 22, 12 * slot, 20, lab, size=13, color=SECONDARY, bold=True, align=PP_ALIGN.CENTER)
vline(s, cx(20) - slot / 2, top - 10, rb - top + 36, BORDER_LIGHT, 1.0, dash=True)
rect(s, 120, 150, 16, 16, LIGHT)
text(s, 142, 146, 80, 24, "売上", size=14, color=SECONDARY)
rect(s, 206, 156, 28, 4, STRONG)
text(s, 240, 146, 80, 24, "広告費", size=14, color=SECONDARY)
rect(s, 310, 156, 28, 4, MOSS)
text(s, 344, 146, 80, 24, "ROAS", size=14, color=SECONDARY)
q_ad = (sum(AD[17:20]), sum(AD[29:32]))
q_s = (sum(S[17:20]), sum(S[29:32]))
text(s, 56, 660, 1016, 70,
     [f"26年8〜9月は広告費を月{AD[30]:.1f}〜{AD[31]:.1f}百万円に増やし、注文数は月{ORDERS[30]}件超（前年同月の約{ORDERS[30] / ORDERS[18]:.1f}倍）。",
      f"7〜9月の広告費は前年同期の{q_ad[0]:.1f}→{q_ad[1]:.1f}百万円、売上は{q_s[0]:.1f}→{q_s[1]:.1f}百万円（{(q_s[1] / q_s[0] - 1) * 100:+.0f}%）。"
      f"全体ROASは{q_s[0] / q_ad[0] * 100:.0f}→{q_s[1] / q_ad[1] * 100:.0f}%"],
     size=18, bold=True, spacing=1.45)
footnote(s, "※ 広告は生花のみ（植木鉢・資材は広告なし）。ROASは生花以外も含むサイト全体の売上÷広告費。24年10〜12月は広告費が小さいためROASの線は25年1月から")

# =====================================================================
# 章 02：今後のエコノミクス
# =====================================================================
divider("02", "UNIT ECONOMICS", "今後の事業におけるエコノミクス", "原価・全体ROAS・直接固定費")


def econ(months):
    idx = [mi(m) for m in months]
    e = dict(S=sum(S[i] for i in idx), GP=sum(GP[i] for i in idx), AD=sum(AD[i] for i in idx))
    e["COGS"] = e["S"] - e["GP"]
    e["NET"] = e["GP"] - e["AD"]
    e["LABOR"] = FIXED["LABOR"] * len(idx)
    e["OTHER"] = FIXED["RENT"] * len(idx)
    e["CONTRIB"] = e["NET"] - e["LABOR"] - e["OTHER"]
    e["ROAS"] = e["S"] / e["AD"] * 100
    e["N"] = len(idx)
    return e


Q3 = ["2026-07", "2026-08", "2026-09"]
FY26 = [f"{y_}-{m_:02d}" for y_, m_ in YM[20:32]]
FY25 = [f"{y_}-{m_:02d}" for y_, m_ in YM[8:20]]
PERIODS = {
    "q": dict(label="26年7〜9月（直近四半期）", short="26年7〜9月", e=econ(Q3)),
    "fy": dict(label="26年9月期（通年）", short="26年9月期", e=econ(FY26)),
    "fy25": dict(label="前期（25年9月期）", short="25年9月期", e=econ(FY25)),
}
PH = "（直接固定費は仮置き）" if FIXED_IS_PLACEHOLDER else ""

s = content_slide("エコノミクス：直近の四半期と通年", "棒の数字は売上を100としたときの割合（%）。金額は期間名の下　※税抜" + PH)
for k, (key, x) in enumerate((("q", 150), ("fy", 640))):
    e = PERIODS[key]["e"]
    waterfall(s, x, PERIODS[key]["label"], [("原価等", e["COGS"]), ("広告費", e["AD"]), ("人件費", e["LABOR"]), ("拠点費", e["OTHER"])],
              "貢献\n利益", e["CONTRIB"], e["S"], MOSS, lo=-60, unit=f"（{e['N']}か月計）", bar=LIGHT)
vline(s, 564, 160, 500)
eq, ef = PERIODS["q"]["e"], PERIODS["fy"]["e"]
text(s, 56, 678, 1016, 60,
     [f"広告費込み粗利は四半期で{yen(eq['NET'])}百万円（売上比{eq['NET'] / eq['S'] * 100:.0f}%）、通年で{yen(ef['NET'])}百万円（同{ef['NET'] / ef['S'] * 100:.0f}%）。",
      f"直接固定費（月{FIXED['LABOR'] + FIXED['RENT']:.1f}百万円）を引いた貢献利益は[[{yen(ef['CONTRIB'])}百万円]]（通年）"],
     size=20, bold=True, spacing=1.4)
footnote(s, "※ 原価等＝商品原価・送料・資材・決済手数料（管理画面の粗利の定義）。広告費はMarketing Master。"
            "人件費・拠点費は仮置き（月" + f"{FIXED['LABOR']:.1f}／{FIXED['RENT']:.1f}百万円" + "）で、社内の集計に差し替える前提")

# ---- 主要指標（表）
s = content_slide("エコノミクスの主要指標", "直近の四半期（26年7〜9月）と通年（26年9月期・25年9月期）　※税抜" + PH)
cols = ["q", "fy", "fy25"]
cx2 = [56, 430, 650, 870]
CW2 = 180
y = 160
for j, key in enumerate(cols):
    text(s, cx2[1 + j], y, CW2, 28, PERIODS[key]["short"], size=17, bold=True, align=PP_ALIGN.RIGHT)
hline(s, 56, y + 40, 1016, MOSS, 1.5)
y += 40
RH = 60


def r2(label, fn, sub=None, bold=False):
    global y
    tb = text(s, cx2[0], y, 340, RH, label, size=18, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    if sub:
        p_ = tb.text_frame.add_paragraph()
        p_.line_spacing = 1.0
        p_.space_before = Emu(int(pt(4) * 12700))
        r_ = p_.add_run()
        r_.text = sub
        _set_font(r_, 12, SECONDARY, False)
    for j, key in enumerate(cols):
        v = fn(PERIODS[key]["e"])
        text(s, cx2[1 + j], y, CW2, RH, v, size=18, bold=bold, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE,
             spacing=1.0, color=STRONG if v.startswith("▲") else MOSS)
    y += RH
    hline(s, 56, y, 1016)


r2("売上（百万円）", lambda e: f"{e['S']:.1f}", "期間の合計")
r2("原価率", lambda e: f"{e['COGS'] / e['S'] * 100:.0f}%", "商品原価・送料・資材・決済手数料を含む")
r2("全体ROAS", lambda e: f"{e['ROAS']:.0f}%", "売上÷広告費（広告は生花のみ）")
r2("広告費込み粗利率", lambda e: f"{e['NET'] / e['S'] * 100:.1f}%", bold=True)
r2("直接固定費（百万円）", lambda e: f"{e['LABOR'] + e['OTHER']:.1f}", "人件費＋拠点費（仮置き）" if FIXED_IS_PLACEHOLDER else "人件費＋拠点費")
r2("貢献利益（百万円）", lambda e: yen(e["CONTRIB"]), bold=True)
be_q = (eq["LABOR"] + eq["OTHER"]) / eq["N"] / (eq["NET"] / eq["S"])
be_fy = (ef["LABOR"] + ef["OTHER"]) / ef["N"] / (ef["NET"] / ef["S"])
text(s, 56, y + 16, 1016, 70,
     [f"損益分岐の月商は、通年の広告費込み粗利率（{ef['NET'] / ef['S'] * 100:.1f}%）なら約[[{be_fy:.0f}百万円]]、"
      f"直近四半期の率（{eq['NET'] / eq['S'] * 100:.1f}%）なら約{be_q:.0f}百万円。",
      f"26年9月期の月平均は{fy_s[2] / 12:.1f}百万円"], size=19, bold=True, spacing=1.45)
footnote(s, "※ 損益分岐＝直接固定費÷広告費込み粗利率。固定費が売上に比例して増えない前提の概算")

# ---- LTV/CAC
cac26 = fy_ad[2] * 1e6 / NEW26
cac25 = fy_ad[1] * 1e6 / LTV25["new"]
gp12 = LTV25["sales12"] * LTV25["gp_rate"] / 100
first_gp26 = AOV26 * GP_RATE26 / 100
ratio = gp12 / cac26
ratio_s = LTV25["sales12"] / cac26
s = content_slide("LTV/CAC：ハナイチ", "自社サイトの新規顧客1人あたり　※税抜")
x, w = 56, 488
rect(s, x, 150, w, 6, LIGHT)
text(s, x, 172, w, 34, "新規顧客1人あたりの採算", size=23, bold=True)
text(s, x, 214, 230, 22, "LTV/CAC（粗利ベース）", size=13, color=SECONDARY, bold=True)
tb = text(s, x, 236, 230, 66, f"{ratio:.1f}", size=56, bold=True, color=MOSS, en=True, spacing=1.0, anchor=MSO_ANCHOR.BOTTOM)
r = tb.text_frame.paragraphs[0].add_run()
r.text = "倍"
_set_font(r, 22, MOSS, True, en=False)
text(s, x + 236, 214, w - 236, 22, "売上ベース", size=13, color=SECONDARY, bold=True)
tb = text(s, x + 236, 236, w - 236, 60, f"{ratio_s:.1f}", size=30, bold=True, color=SECONDARY, en=True, spacing=1.0,
          anchor=MSO_ANCHOR.BOTTOM)
r = tb.text_frame.paragraphs[0].add_run()
r.text = "倍"
_set_font(r, 14, SECONDARY, True, en=False)
text(s, x, 300, w, 22, f"LTV {gp12:,.0f}円 ÷ CAC {cac26:,.0f}円　／　売上ベースは12か月の売上{LTV25['sales12']:,}円 ÷ CAC", size=12, color=SECONDARY)
rows_ = [
    ("CAC（広告費÷新規顧客数）", f"{cac25:,.0f}円", f"{cac26:,.0f}円"),
    ("初回の購入単価", f"{LTV25['aov']:,}円", f"{AOV26:,}円"),
    ("初回購入の粗利", f"{LTV25['aov'] * LTV25['gp_rate'] / 100:,.0f}円", f"{first_gp26:,.0f}円"),
    ("12か月の購入回数", f"{LTV25['orders12']:.2f}回", "—"),
    ("12か月の売上（LTV・売上）", f"{LTV25['sales12']:,}円", "—"),
    ("12か月の粗利（LTV）", f"{gp12:,.0f}円", "—"),
    ("リピート率（3か月以内）", f"{LTV25['rep3']:.1f}%", "—"),
    ("リピート率（12か月以内）", f"{LTV25['rep12']:.1f}%", "—"),
    ("売上に占めるリピート顧客", f"{REPEAT_SHARE[0]:.1f}%", f"{REPEAT_SHARE[1]:.1f}%"),
]
yy = 334
text(s, x + w - 250, yy, 120, 24, "25年9月期", size=14, color=SECONDARY, bold=True, align=PP_ALIGN.RIGHT)
text(s, x + w - 120, yy, 120, 24, "26年9月期", size=14, color=SECONDARY, bold=True, align=PP_ALIGN.RIGHT)
hline(s, x, yy + 30, w, MOSS, 1.5)
yy += 38
for lab, v1, v2 in rows_:
    bold_ = lab.startswith("12か月の粗利") or lab.startswith("CAC")
    text(s, x, yy, w - 250, 30, lab, size=15, bold=bold_)
    text(s, x + w - 250, yy, 120, 30, v1, size=16, bold=bold_, align=PP_ALIGN.RIGHT, color=MUTED if v1 == "—" else MOSS)
    text(s, x + w - 120, yy, 120, 30, v2, size=16, bold=bold_, align=PP_ALIGN.RIGHT, color=MUTED if v2 == "—" else MOSS)
    yy += 34
    hline(s, x, yy - 8, w)
vline(s, 564, 150, 550)
# 右：リピート顧客（事業者）の重み
x2 = 584
rect(s, x2, 150, w, 6, MOSS)
text(s, x2, 172, w, 34, "売上の大半はリピート顧客（事業者）", size=23, bold=True)
text(s, x2, 216, w, 60,
     [f"26年9月期の売上{fy_s[2]:.1f}百万円のうち、リピート購入が{REPEAT_SHARE[1]:.0f}%。",
      f"リピート顧客{REPEAT_CUSTOMERS[1]}人の客単価は{REPEAT_AOV[1]:,}円と、初回（{AOV26:,}円）の約{REPEAT_AOV[1] / AOV26:.0f}倍"],
     size=15, color=SECONDARY, spacing=1.45)
yy = 300
text(s, x2, yy, w, 24, "26年9月期の顧客の業態（登録区分）", size=14, color=SECONDARY, bold=True)
text(s, x2 + w - 230, yy, 110, 24, "顧客数", size=14, color=SECONDARY, bold=True, align=PP_ALIGN.RIGHT)
text(s, x2 + w - 110, yy, 110, 24, "売上（百万円）", size=14, color=SECONDARY, bold=True, align=PP_ALIGN.RIGHT)
hline(s, x2, yy + 30, w, MOSS, 1.5)
yy += 38
for name, cnt, sales in BIZ_CATEGORIES:
    text(s, x2, yy, w - 240, 30, name, size=15)
    text(s, x2 + w - 230, yy, 110, 30, f"{cnt:,}", size=16, align=PP_ALIGN.RIGHT, en=True)
    text(s, x2 + w - 110, yy, 110, 30, f"{sales:.1f}", size=16, align=PP_ALIGN.RIGHT, en=True)
    yy += 34
    hline(s, x2, yy - 8, w)
text(s, x2, yy + 4, w, 60, "「未設定」が売上の大半で、法人・店舗や個人事業主の大口顧客が含まれる。業態の登録を進めると、どの顧客層を増やすべきかが見える",
     size=13, color=SECONDARY, spacing=1.4)
text(s, 56, 694, 1016, 60,
     [f"初回購入の粗利（{first_gp26:,.0f}円）ではCAC（{cac26:,.0f}円）を回収できず、12か月の粗利LTV（{gp12:,.0f}円）でも{ratio:.1f}倍。",
      "新規の採算は、2年目以降のリピートか、初回の購入単価・粗利率の改善で成り立たせる必要がある"],
     size=16, bold=True, spacing=1.45)
footnote(s, "※ 自社サイトを顧客単位で集計。LTVは25年9月期に初回購入した顧客の初回から12か月の平均（売上は受注データ、粗利は期の粗利率で換算）。"
            "CACは広告費をすべて新規獲得にかかったとみなした値。LTV/CACは26年9月期のCACで計算")

# ---- 損益分岐に必要な月商
s = content_slide("損益分岐に必要な月商", "貢献利益が0になる月商と、26年9月期の月平均の売上　単位：百万円/月" + PH)
fixed_m = FIXED["LABOR"] + FIXED["RENT"]
act = fy_s[2] / 12
peak = max(S[20:32])
rows3 = [("通年の率（26年9月期）", ef["NET"] / ef["S"], be_fy), ("直近四半期の率（26年7〜9月）", eq["NET"] / eq["S"], be_q)]
bx0, bwid = 330, 600
vmax_ = max(be_fy, be_q, peak) * 1.1
y0 = 168
text(s, 56, y0, 400, 36, "損益分岐の月商", size=24, bold=True, anchor=MSO_ANCHOR.MIDDLE)
text(s, 460, y0, 612, 36, f"直接固定費 {fixed_m:.1f}百万円/月（仮置き）", size=15, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE)
yy = y0 + 48
for lab, m_, be in rows3:
    text(s, 56, yy, 270, 36, [lab, f"広告費込み粗利率 {m_ * 100:.1f}%"], size=14, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.2)
    rect(s, bx0, yy + 10, bwid * be / vmax_, 24, MOSS)
    text(s, bx0 + bwid * be / vmax_ + 10, yy, 120, 36, f"{be:.1f}", size=17, bold=True, en=True, anchor=MSO_ANCHOR.MIDDLE)
    yy += 56
for lab, v, c_ in (("26年9月期の月平均", act, LIGHT), ("26年9月期の最高月", peak, BG_GRAY)):
    text(s, 56, yy, 270, 36, lab, size=16, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE)
    rect(s, bx0, yy + 10, bwid * v / vmax_, 24, c_)
    text(s, bx0 + bwid * v / vmax_ + 10, yy, 120, 36, f"{v:.1f}", size=17, bold=True, en=True, anchor=MSO_ANCHOR.MIDDLE)
    yy += 44
hline(s, 56, yy + 8, 1016)
rs = REPEAT_SHARE[1] / 100
new_need = be_fy * 1e6 * (1 - rs) / AOV26
mult = be_fy / act
text(s, 56, yy + 40, 1016, 160,
     [f"損益分岐の月商は約{be_fy:.0f}百万円で、26年9月期の月平均{act:.1f}百万円の約{mult:.1f}倍。固定費が仮置きのため幅はあるが、",
      f"現状の広告費込み粗利率（{ef['NET'] / ef['S'] * 100:.0f}%）のままでは、売上を数倍にしないと貢献利益は黒字にならない。",
      f"広告費込み粗利率を高める（広告効率・粗利率の改善）か、リピート顧客（事業者）の積み上げで固定費を吸収する売上規模に乗せるかが論点"],
     size=18, bold=True, spacing=1.5)
footnote(s, "※ 損益分岐＝直接固定費÷広告費込み粗利率。直接固定費は仮置き（人件費1.2＋拠点費0.3百万円/月）。社内の集計で差し替える")

# =====================================================================
# 要約（数字が出そろってから）
# =====================================================================
draw_claims(summary_slide, [
    ("1", "売上は3期で拡大、粗利率は30%台を維持", [
        f"売上は{fy_s[0]:.0f}→{fy_s[1]:.0f}→{fy_s[2]:.0f}百万円（24年9月期は8か月）。26年9月期は前期比+{(fy_s[2] / fy_s[1] - 1) * 100:.0f}%",
        f"粗利率は{fy_gp[1] / fy_s[1] * 100:.0f}→{fy_gp[2] / fy_s[2] * 100:.0f}%。広告費込み粗利は{fy_net[1]:.1f}→{fy_net[2]:.1f}百万円（同率{fy_net[2] / fy_s[2] * 100:.0f}%）"]),
    ("2", "広告は生花の新規獲得に集中。1人あたりの採算はまだ成立していない", [
        f"CAC {cac26:,.0f}円に対し、初回購入の粗利は{first_gp26:,.0f}円、12か月の粗利LTVは{gp12:,.0f}円（LTV/CAC {ratio:.1f}倍）",
        f"全体ROASは{fy_s[2] / fy_ad[2] * 100:.0f}%だが、広告対象の生花はサイト売上の一部で、初回の購入単価（{AOV26:,}円）が小さい"]),
    ("3", "収益化の鍵は、リピート顧客（事業者）の積み上げと広告費込み粗利率の改善", [
        f"売上の{REPEAT_SHARE[1]:.0f}%はリピート顧客で、客単価は初回の約{REPEAT_AOV[1] / AOV26:.0f}倍。法人・店舗・個人事業主の大口が利益の源泉",
        f"損益分岐の月商は約{be_fy:.0f}百万円（直接固定費は仮置き）で、26年9月期の月平均{act:.1f}百万円の約{mult:.1f}倍"]),
])
footnote(summary_slide, "※ 数値は税抜。用語の定義と集計の前提は最終ページ。直接固定費は仮置きで、社内の集計に差し替える")

# ---- 用語と集計の前提
terms = content_slide("用語と集計の前提")
TERMS = [
    ("期", "9月決算。「26年9月期」＝2025年10月〜2026年9月。24年9月期は開始の2024年2月からの8か月"),
    ("売上", "税抜・注文日ベースの純売上（確定請求額−返金）。自社サイトのみ、キャンセル・テスト注文は除く"),
    ("粗利", "売上 − 商品原価・送料・資材・決済手数料（管理画面の定義）。AP/AFの「限界利益」に相当"),
    ("広告費", "Google・Meta・Yahoo!・Microsoft・Pinterest の広告費（税抜）。広告は生花のみ"),
    ("広告費込み粗利", "粗利 − 広告費"),
    ("全体ROAS", "売上 ÷ 広告費。分子は生花以外（植木鉢・資材）も含むサイト全体の売上"),
    ("直接固定費", "ハナイチに直接かかる人件費と、拠点の家賃・水道光熱費。本資料では仮置き（月1.2＋0.3百万円）"),
    ("貢献利益", "広告費込み粗利 − 直接固定費。本社の人件費・共通費は含まない"),
    ("出典", "ハナイチ管理画面（売上・粗利・顧客）、Marketing Master（広告費）、受注データ（顧客単位のLTV）"),
]
y = 150
hline(terms, 56, y, 1016)
for k_, v_ in TERMS:
    rh_ = 64
    text(terms, 56, y, 236, rh_, k_, size=19, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(terms, 300, y, 772, rh_, v_, size=16, color=SECONDARY, spacing=1.35, anchor=MSO_ANCHOR.MIDDLE)
    y += rh_
    hline(terms, 56, y, 1016)

prs.save("hanaichi_economics_2026-10.pptx")
print("saved", len(prs.slides._sldIdLst), "slides")
print("FY", [round(v, 1) for v in fy_s], [round(v, 1) for v in fy_ad], [round(v, 1) for v in fy_net])
print({k: {kk: round(vv, 2) for kk, vv in P["e"].items()} for k, P in PERIODS.items()})
print("cac", round(cac26), round(cac25), "ltv", round(gp12), "ratio", round(ratio, 2), "be", round(be_fy, 1), round(be_q, 1))
