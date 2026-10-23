"""ギフティ様向け ハナイチ 事業エコノミクス資料 — giftee-2026-10 と同じ型（Domuz デザインシステム「発表スライド」）。

データは data_hanaichi.py（管理画面の売上・限界利益、Marketing Master の広告費、顧客単位の集計）。
直接固定費（FIXED）は発送人件費（現場の作業時間×時給の概算）と川崎拠点の家賃按分。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from deck_lib import *  # noqa
from deck_lib import _set_font  # noqa
from data_hanaichi import (YM, FY, mi, S, GP, AD, NET, ORDERS, FIXED, FIXED_IS_PLACEHOLDER, LTV25, NEW26, AOV26,
                           GP_RATE26, GP_RATE26_SMALL, FIRST_GP26, SEGMENTS, BIG, SMALL, REPEAT_RATE, REPEAT_SHARE, FB_S, FB_GP,
                           REP_YM, REP_ORDERS, REP_REPEAT, REP_ACTIVE, REP_ACTIVE_REP, REP_NEW, REP_CUM, REP_CUM_REP, COHORT,
                           CAT_MARGIN, ACCOUNTS_TOTAL, ACCOUNTS_BOUGHT, KAWASAKI_RENT, RENT_SHARE, SHIP_LABOR_RATE, REPEAT_CUSTOMERS, REPEAT_AOV, BIZ_CATEGORIES, fy_sum)

N = len(S)
HANA = RGBColor(0xF5, 0xB7, 0x00)  # ハナイチの色（黄）
HANA_LIGHT = RGBColor(0xFB, 0xE3, 0x8C)
HANA_DARK = RGBColor(0xA6, 0x7C, 0x00)  # 線・強調用の濃い黄
_divider = divider


def divider(num, en_label, title, sub=""):
    return _divider(num, en_label, title, sub, bg=HANA, fg=MOSS)


_content_slide = content_slide


def content_slide(title=None, sub=None):
    return _content_slide(title, sub, accent=HANA)


fy_s, fy_gp, fy_ad, fy_net = fy_sum(S), fy_sum(GP), fy_sum(AD), fy_sum(NET)
FY_NAMES = [f[0] for f in FY]

# =====================================================================
# 1. 表紙
# =====================================================================
s = new_slide()
rect(s, 0, 0, 8, H_PX, HANA)
text(s, 96, 220, 960, 40, "株式会社ギフティ様　ご参考資料", size=26, color=SECONDARY)
text(s, 96, 290, 980, 180, ["ハナイチ", "事業エコノミクスの整理とまとめ"], size=56, bold=True, spacing=1.3)
text(s, 96, 480, 960, 40, "売上・限界利益・広告費の推移と、今後のエコノミクス", size=24, color=SECONDARY)
text(s, 96, 640, 900, 120, ["2026年10月", "株式会社DOMUZ", "髙木 弘貴"], size=22, color=SECONDARY, spacing=1.5)

# =====================================================================
# 2. 本資料の構成・要約
# =====================================================================
s = content_slide("本資料の構成")
items = [
    ("1", "ハナイチのエコノミクスの整理と経年推移", "24年9月期（2024年2月の開始）〜26年9月期、花き市場とターゲット層"),
    ("2", "今後の事業におけるエコノミクスの整理", "原価・全体ROAS・直接固定費、LTV/CACとリピートの積み上がり、損益分岐の月商"),
    ("3", "中長期の可能性と事業間シナジー", "卸仕入れサイトからの広がり、アンドフラワー／アンドプランツとの連携、仕入れのスケールメリット"),
]
y = 220
for n, label, sub in items:
    text(s, 96, y + 16, 80, 64, n, size=60, color=HANA, bold=True, en=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, 190, y + 16, 870, 64, label, size=34, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, 190, y + 84, 870, 30, sub, size=20, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    if n != items[-1][0]:
        hline(s, 96, y + 128, 936)
    y += 150
footnote(s, "※ 用語と集計の前提は最終ページにまとめています")

summary_slide = content_slide("ハナイチ")

# =====================================================================
# 章 01：推移
# =====================================================================
divider("01", "ECONOMICS TREND", "ハナイチのエコノミクスの推移", "24年9月期（2024年2月）〜 26年9月期（2026年9月）")

# ---- 四半期の区切り（2024年2月〜：最初の四半期は2〜3月の2か月）
QTR = []  # (ラベル, 開始位置, 終了位置, 期の番号)
_q_bounds = [(0, 2)] + [(2 + 3 * k, 5 + 3 * k) for k in range(10)]
_q_labels = ["2〜3月", "4〜6月", "7〜9月"] + ["10〜12月", "1〜3月", "4〜6月", "7〜9月"] * 2
for (a_, b_), lab in zip(_q_bounds, _q_labels):
    QTR.append((lab, a_, b_, 0 if b_ <= 8 else (1 if b_ <= 20 else 2)))
q_s = [sum(S[a_:b_]) for _, a_, b_, _ in QTR]
q_gp = [sum(GP[a_:b_]) for _, a_, b_, _ in QTR]
q_ad = [sum(AD[a_:b_]) for _, a_, b_, _ in QTR]
q_net = [sum(NET[a_:b_]) for _, a_, b_, _ in QTR]
q_orders = [sum(ORDERS[a_:b_]) for _, a_, b_, _ in QTR]
q_fb = [sum(FB_S[a_:b_]) for _, a_, b_, _ in QTR]
NQ = len(QTR)
fy_fb, fy_fbgp = fy_sum(FB_S), fy_sum(FB_GP)
fy_tot = [a + b for a, b in zip(fy_s, fy_fb)]
fy_totgp = [a + b for a, b in zip(fy_gp, fy_fbgp)]

s = content_slide("ハナイチ：四半期の売上と期別の限界利益")
msg = (f"売上は{fy_tot[1]:.0f} → {fy_tot[2]:.0f}百万円（+{(fy_tot[2] / fy_tot[1] - 1) * 100:.0f}%）。"
       f"卸仕入れサイトは{fy_s[1]:.0f} → {fy_s[2]:.0f}百万円、限界利益率{fy_gp[2] / fy_s[2] * 100:.0f}%")
text(s, 56, 104, 1016, 36, msg, size=21, bold=True)
x0, x1 = 214, 914
text(s, x0, 154, 600, 24, "24年9月期（2024年2月）〜26年9月期（2026年9月）の四半期　単位：百万円", size=14, color=SECONDARY)
rect(s, 820, 160, 12, 12, HANA)
text(s, 838, 154, 90, 24, "ハナイチ", size=12, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
rect(s, 920, 160, 12, 12, HANA_LIGHT)
text(s, 938, 154, 140, 24, "ボックス等（参考）", size=12, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
top, base = 206, 434
slot = (x1 - x0) / NQ
bw = slot * 0.6
vmax = max(a + b for a, b in zip(q_s, q_fb)) * 1.18  # 上に目印のラベルの余白
sy = lambda v: base - (base - top) * v / vmax
for qi, (lab, a_, b_, k) in enumerate(QTR):
    bx = x0 + qi * slot + (slot - bw) / 2
    rect(s, bx, sy(q_s[qi]), bw, base - sy(q_s[qi]), HANA)
    tot = q_s[qi] + q_fb[qi]
    if q_fb[qi] > 0.05:
        rect(s, bx, sy(tot), bw, sy(q_s[qi]) - sy(tot), HANA_LIGHT)
    text(s, bx - 20, sy(tot) - 24, bw + 40, 22, f"{tot:.1f}", size=14, bold=True, align=PP_ALIGN.CENTER, en=True)
    text(s, bx - 16, base + 6, bw + 32, 20, lab, size=11, color=MUTED, align=PP_ALIGN.CENTER)
for k, (name, a_, b_) in enumerate(FY):
    qa = [qi for qi, q in enumerate(QTR) if q[3] == k]
    gx = x0 + qa[0] * slot
    gw = len(qa) * slot
    if k > 0:
        vline(s, gx, 190, base - 190 + 84, BORDER_LIGHT, 1.0, dash=True)
    text(s, gx, base + 30, gw, 26, name, size=17, bold=True, align=PP_ALIGN.CENTER)
    text(s, gx, base + 56, gw, 24, f"{fy_tot[k]:.0f}", size=16, color=SECONDARY, align=PP_ALIGN.CENTER, en=True)
hline(s, x0 - 4, base, x1 - x0 + 8, BORDER_LIGHT, 1.5)
xl = x0 + 6 * slot  # 25年7〜9月の四半期の左端
vline(s, xl, top - 24, base - top + 24, HANA_DARK, 2.0)
text(s, xl + 6, top - 30, 300, 22, "25年7月〜 生花のSKUを本格的に拡充", size=14, bold=True, color=HANA_DARK)
hdr = ["期", "売上（計）", "うちハナイチ", "うちボックス等", "限界利益（計）", "同率", "ハナイチの率"]
cxs = [56, 190, 330, 480, 640, 790, 920]
cws = [130, 140, 150, 160, 150, 130, 152]
ty = 526
rect(s, 56, ty, 1016, 40, MOSS)
for j, h in enumerate(hdr):
    text(s, cxs[j] + (12 if j == 0 else 0), ty, cws[j] - (0 if j == 0 else 12), 40, h, size=16, color=WHITE, bold=True,
         anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.LEFT if j == 0 else PP_ALIGN.RIGHT)
y = ty + 40
rh = 52
for k in range(3):
    if k == 2:
        rect(s, 56, y, 1016, rh, WATERMARK)
    vals = [FY_NAMES[k], f"{fy_tot[k]:.1f}", f"{fy_s[k]:.1f}", f"{fy_fb[k]:.1f}", f"{fy_totgp[k]:.1f}",
            f"{fy_totgp[k] / fy_tot[k] * 100:.1f}%", f"{fy_gp[k] / fy_s[k] * 100:.1f}%"]
    for j, v in enumerate(vals):
        text(s, cxs[j] + (12 if j == 0 else 0), y, cws[j] - (0 if j == 0 else 12), rh, v, size=19 if j else 17, bold=True,
             color=STRONG if v.startswith("-") else MOSS, anchor=MSO_ANCHOR.MIDDLE,
             align=PP_ALIGN.LEFT if j == 0 else PP_ALIGN.RIGHT)
    y += rh
    hline(s, 56, y, 1016, BORDER_LIGHT)
footnote(s, "※ 税抜・注文日ベース。ハナイチは管理画面の純売上と限界利益（限界利益＝売上−商品原価・送料・資材・決済手数料。AP/AFの限界利益に相当）。"
            "フラワーボックス等はマスター管理表のイネイブラー事業の売上・限界利益（24年9月期の限界利益は未集計）。24年9月期は2024年2月〜9月の8か月")

# ---- 広告投資：四半期の広告費・売上・ROAS（24年10〜12月〜26年7〜9月）
s = content_slide("広告投資：生花の新規獲得に広告を投下", "卸仕入れサイトの四半期の売上・広告費・ROAS（24年10月〜26年9月）　単位：百万円")
Q0 = 3  # 25年9月期の最初の四半期
nq = NQ - Q0
x0, x1 = 214, 914
slot = (x1 - x0) / nq
cx = lambda qi: x0 + (qi - Q0) * slot + slot / 2
top, base = 190, 440
vmax_ = 20
sy = lambda v: base - (base - top) * v / vmax_
for v in range(0, vmax_ + 1, 5):
    hline(s, x0 - 4, sy(v), x1 - x0 + 4, BORDER_LIGHT if v == 0 else WATERMARK)
    text(s, x0 - 60, sy(v) - 11, 50, 22, str(v), size=12, color=MUTED, align=PP_ALIGN.RIGHT, en=True)
for qi in range(Q0, NQ):
    bw_ = slot * 0.5
    rect(s, cx(qi) - bw_ / 2, sy(q_s[qi]), bw_, base - sy(q_s[qi]), HANA)
    text(s, cx(qi) - 40, sy(q_s[qi]) - 24, 80, 22, f"{q_s[qi]:.1f}", size=13, bold=True, align=PP_ALIGN.CENTER, en=True)
polyline(s, [(cx(qi), sy(q_ad[qi])) for qi in range(Q0, NQ)], HANA_DARK, 3.0)
for qi in range(Q0, NQ):
    rect(s, cx(qi) - 4, sy(q_ad[qi]) - 4, 8, 8, HANA_DARK, shape=MSO_SHAPE.OVAL)
    text(s, cx(qi) - 40, sy(q_ad[qi]) + 6, 80, 20, f"{q_ad[qi]:.1f}", size=12, bold=True, color=HANA_DARK, align=PP_ALIGN.CENTER, en=True)
rt, rb = 492, 600
rmax = 1200
ry = lambda v: rb - (rb - rt) * min(v, rmax) / rmax
text(s, x0, rt - 30, 300, 22, "ROAS（売上÷広告費）", size=13, color=SECONDARY, bold=True)
for v in (0, 400, 800, 1200):
    hline(s, x0 - 4, ry(v), x1 - x0 + 4, BORDER_LIGHT if v == 0 else WATERMARK)
    text(s, x0 - 70, ry(v) - 10, 60, 20, f"{v}%", size=11, color=MUTED, align=PP_ALIGN.RIGHT, en=True)
q_roas = [q_s[qi] / q_ad[qi] * 100 if q_ad[qi] > 0 else None for qi in range(NQ)]
polyline(s, [(cx(qi), ry(q_roas[qi])) for qi in range(Q0 + 1, NQ)], MOSS, 2.5)  # 広告が本格化した25年1〜3月から
for qi in range(Q0, NQ):
    if qi > Q0:
        text(s, cx(qi) - 40, ry(q_roas[qi]) - 22, 80, 18, f"{q_roas[qi]:,.0f}%", size=11, bold=True, align=PP_ALIGN.CENTER, en=True)
    text(s, cx(qi) - 50, rb + 4, 100, 18, QTR[qi][0], size=11, color=MUTED, align=PP_ALIGN.CENTER)
for lab, qi in (("25年9月期", 3), ("26年9月期", 7)):
    text(s, cx(qi) - slot / 2, rb + 22, 4 * slot, 20, lab, size=13, color=SECONDARY, bold=True, align=PP_ALIGN.CENTER)
vline(s, cx(7) - slot / 2, top - 10, rb - top + 36, BORDER_LIGHT, 1.0, dash=True)
xl = cx(NQ - 1) - slot / 2
vline(s, xl, top - 24, base - top + 24, HANA_DARK, 2.0)
text(s, xl - 266, top - 30, 260, 22, "26年7月〜 広告費を増やした", size=14, bold=True, color=HANA_DARK, align=PP_ALIGN.RIGHT)
rect(s, x0, 150, 16, 16, HANA)
text(s, x0 + 22, 146, 80, 24, "売上", size=14, color=SECONDARY)
rect(s, x0 + 86, 156, 28, 4, HANA_DARK)
text(s, x0 + 120, 146, 80, 24, "広告費", size=14, color=SECONDARY)
rect(s, x0 + 190, 156, 28, 4, MOSS)
text(s, x0 + 224, 146, 80, 24, "ROAS", size=14, color=SECONDARY)
qa_ = (q_ad[6], q_ad[10])
qs_ = (q_s[6], q_s[10])
text(s, 56, 660, 1016, 70,
     [f"26年7〜9月は広告費を{qa_[1]:.1f}百万円（前年同期{qa_[0]:.1f}）に増やし、注文数は{q_orders[10]:,}件（前年同期の約{q_orders[10] / q_orders[6]:.1f}倍）。",
      f"売上は{qs_[0]:.1f} → {qs_[1]:.1f}百万円（{(qs_[1] / qs_[0] - 1) * 100:+.0f}%）、全体ROASは{qs_[0] / qa_[0] * 100:.0f} → {qs_[1] / qa_[1] * 100:.0f}%"],
     size=18, bold=True, spacing=1.45)
footnote(s, "※ フラワーボックス等は含まない。広告は生花のみ（植木鉢・資材は広告なし）。ROASは生花以外も含むサイト全体の売上÷広告費。24年10〜12月は広告費が小さいためROASの線は25年1〜3月から")

# ---- 花き市場とハナイチのターゲット層
s = content_slide("花き市場とハナイチのターゲット層", "国内の花き消費のどこにアクセスしているか、どの順で広げるか")
# 左：市場の構造（農水省「花きの現状について」）
x, w = 56, 330
text(s, x, 150, w, 30, "国内の花き市場（農水省）", size=18, bold=True)
hline(s, x, 186, w, MOSS, 1.5)
MKT = [
    ("花きの消費額", "約1.2兆円", "個人消費 9,327億円＋業務用 2,491億円"),
    ("うち業務用需要", "2,491億円", "葬儀 1,727／婚礼 372／稽古 392億円"),
    ("国内産出額", "3,695億円", "切り花 2,147、鉢もの 957億円ほか（令和5年）"),
    ("輸入額", "618億円", "国内流通の約1割"),
    ("卸売市場の経由率", "約7割", "小売が零細で、市場を通る流通が中心"),
]
yy = 198
for lab, val, sub in MKT:
    text(s, x, yy, 150, 24, lab, size=13, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, x + 150, yy, w - 150, 24, val, size=19, bold=True, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0, en=False)
    text(s, x, yy + 26, w, 20, sub, size=11, color=MUTED, spacing=1.0)
    yy += 60
    hline(s, x, yy - 8, w)
text(s, x, yy + 8, w, 120,
     ["個人消費が約8割、冠婚葬祭などの業務用が約2割。", "花屋などの小売は零細で、仕入れは卸売市場経由が中心。",
      "ハナイチは、この「小売と業務用の仕入れ」をオンラインに置き換える"],
     size=13, color=SECONDARY, spacing=1.45)
# 右：ターゲットの階層（上ほど大口、下ほど裾野が広い）
TIERS = [  # (層, 説明, 現状のアクセス, 段階, 取り方)
    ("式場・葬儀社など", "花を一度に大量に使う法人。葬儀 1,727億円、婚礼 372億円の需要", "中長期", "営業（イネイブラー・法人営業）で大口の定期取引を取りにいく"),
    ("生花小売店", "街の花屋。市場から仕入れる零細な小売が中心", "次の段階", "品揃え・卸価格・請求書払いで、オンラインと紹介で獲得"),
    ("半スモールB", "個人事業主・フリーランス、アレンジメント教室や華道の先生、撮影スタジオなど", "現在", "広告・SEOでオンライン獲得し、リピート化する"),
    ("個人", "趣味で花を使う人。裾野は広いが単価が小さい", "現在", "広告・SEOでオンライン獲得。半スモールBへの入口"),
]
rx, rw = 430, 642
text(s, rx, 150, rw, 30, "ターゲットの階層と、取りにいく順番", size=18, bold=True)
hline(s, rx, 186, rw, MOSS, 1.5)
ty = 200
TH = 92
for k, (name, desc, stage, how) in enumerate(TIERS):
    bw_ = 150 + k * 50  # 下ほど広い
    col = HANA if stage == "現在" else (HANA_LIGHT if stage == "次の段階" else WATERMARK)
    bx = rx + (300 - bw_) / 2
    rect(s, bx, ty + 6, bw_, TH - 16, col)
    text(s, bx, ty + 6, bw_, TH - 16, name, size=15, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    tagc = HANA if stage == "現在" else (HANA_LIGHT if stage == "次の段階" else WATERMARK)
    rect(s, rx + 318, ty + 8, 72, 22, tagc)
    text(s, rx + 318, ty + 8, 72, 22, stage, size=11, bold=True, color=MOSS, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, rx + 400, ty + 6, rw - 400, 26, how, size=12, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, rx + 318, ty + 34, rw - 318, 50, desc, size=11, color=SECONDARY, spacing=1.35)
    ty += TH
# 矢印：下から上へ広げる
hline(s, 56, 600, 1016)
cnt_smallb = sum(c for n, c, _ in BIZ_CATEGORIES if n in ("個人事業主", "スクール・ワークショップ", "オンライン販売"))
text(s, 56, 616, 1016, 110,
     [f"現状の顧客は個人〜半スモールBが中心（26年9月期の登録区分：個人事業主・スクールなど{cnt_smallb}人、法人・店舗{[c for n, c, _ in BIZ_CATEGORIES if n == '法人・店舗'][0]}人）。",
      "まずこの層でリピートを積み上げて卸の品揃えと物流を整え、次に生花小売店、中長期には式場・葬儀社などの大口へ、オンラインに営業を加えて広げていく"],
     size=16, bold=True, spacing=1.5)
footnote(s, "※ 市場の数字は農林水産省「花きの現状について」（消費額・業務用需要は令和4年の推計、産出額・輸入額は令和5年）。階層の幅は規模のイメージで、金額の比率ではない")


# =====================================================================
# 章 02：今後のエコノミクス
# =====================================================================
divider("02", "UNIT ECONOMICS", "今後の事業におけるエコノミクス", "原価・全体ROAS・直接固定費")


def econ(months):
    idx = [mi(m) for m in months]
    e = dict(S=sum(S[i] for i in idx), GP=sum(GP[i] for i in idx), AD=sum(AD[i] for i in idx))
    e["COGS"] = e["S"] - e["GP"]
    e["NET"] = e["GP"] - e["AD"]
    e["SHIP"] = FIXED["SHIP"] * len(idx)
    e["OTHER"] = FIXED["RENT"] * len(idx)
    e["FIXED"] = e["SHIP"] + e["OTHER"]
    e["CONTRIB"] = e["NET"] - e["FIXED"]
    e["ROAS"] = e["S"] / e["AD"] * 100
    e["N"] = len(idx)
    e["ORDERS"] = sum(ORDERS[i] for i in idx)
    return e


Q3 = ["2026-07", "2026-08", "2026-09"]
FY26 = [f"{y_}-{m_:02d}" for y_, m_ in YM[20:32]]
FY25 = [f"{y_}-{m_:02d}" for y_, m_ in YM[8:20]]
PERIODS = {
    "q": dict(label="26年7〜9月（直近四半期）", short="26年7〜9月", e=econ(Q3), rep=REPEAT_RATE["q"]),
    "fy": dict(label="26年9月期（通年）", short="26年9月期", e=econ(FY26), rep=REPEAT_RATE["fy"]),
    "fy25": dict(label="前期（25年9月期）", short="25年9月期", e=econ(FY25), rep=REPEAT_RATE["fy25"]),
}
PH = ""

s = content_slide("エコノミクス：直近の四半期と通年", "棒の数字は売上を100としたときの割合（%）。金額は期間名の下　※税抜、ボックス等は含まない")
for k, (key, x) in enumerate((("q", 150), ("fy", 640))):
    e = PERIODS[key]["e"]
    waterfall(s, x, PERIODS[key]["label"], [("原価等", e["COGS"]), ("広告費", e["AD"]), ("発送\n人件費", e["SHIP"]), ("拠点費", e["OTHER"])],
              "貢献\n利益", e["CONTRIB"], e["S"], MOSS, lo=-60, unit=f"（{e['N']}か月計）", bar=HANA)
vline(s, 564, 160, 500)
eq, ef = PERIODS["q"]["e"], PERIODS["fy"]["e"]
text(s, 56, 678, 1016, 60,
     [f"広告費込み限界利益は四半期で{yen(eq['NET'])}百万円（売上比{eq['NET'] / eq['S'] * 100:.0f}%）、通年で{yen(ef['NET'])}百万円（同{ef['NET'] / ef['S'] * 100:.0f}%）。",
      f"直接固定費（月{FIXED['SHIP'] + FIXED['RENT']:.2f}百万円）を引いた貢献利益は[[{('+' if ef['CONTRIB'] > 0 else '') + yen(ef['CONTRIB'])}百万円]]（通年）、直近四半期は{yen(eq['CONTRIB'])}百万円"],
     size=20, bold=True, spacing=1.4)
footnote(s, "※ 原価等＝商品原価・送料・資材・決済手数料（管理画面の定義）。広告費はMarketing Master。"
            f"発送人件費は月{FIXED['SHIP']:.2f}百万円（26年8月の作業時間×時給からの概算、生花売上の約{SHIP_LABOR_RATE * 100:.0f}%）、拠点費は川崎拠点の家賃（月{KAWASAKI_RENT:.2f}百万円）の{RENT_SHARE * 100:.0f}%（月{FIXED['RENT']:.2f}百万円）")

# ---- 主要指標（表）
s = content_slide("エコノミクスの主要指標", "直近の四半期（26年7〜9月）と通年（26年9月期・25年9月期）　※税抜、ボックス等は含まない")
cols = ["q", "fy", "fy25"]
cx2 = [56, 430, 650, 870]
CW2 = 180
y = 160
for j, key in enumerate(cols):
    text(s, cx2[1 + j], y, CW2, 28, PERIODS[key]["short"], size=17, bold=True, align=PP_ALIGN.RIGHT)
hline(s, 56, y + 40, 1016, MOSS, 1.5)
y += 40
RH = 50


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
        v = fn(PERIODS[key]["e"], PERIODS[key])
        text(s, cx2[1 + j], y, CW2, RH, v, size=18, bold=bold, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE,
             spacing=1.0, color=STRONG if v.startswith("▲") else MOSS)
    y += RH
    hline(s, 56, y, 1016)


r2("売上（百万円）", lambda e, P: f"{e['S']:.1f}", "期間の合計")
r2("購入数（注文数）", lambda e, P: f"{e['ORDERS']:,}件")
r2("リピート購入率", lambda e, P: f"{P['rep']:.1f}%", "2回目以降の購入が注文に占める割合")
r2("原価率", lambda e, P: f"{e['COGS'] / e['S'] * 100:.0f}%", "商品原価・送料・資材・決済手数料を含む")
r2("全体ROAS", lambda e, P: f"{e['ROAS']:.0f}%", "売上÷広告費（広告は生花のみ）")
r2("広告費込み限界利益率", lambda e, P: f"{e['NET'] / e['S'] * 100:.1f}%", bold=True)
r2("直接固定費（百万円）", lambda e, P: f"{e['FIXED']:.1f}", "発送人件費＋拠点費")
r2("貢献利益（百万円）", lambda e, P: yen(e["CONTRIB"]), bold=True)
be_q = eq["FIXED"] / eq["N"] / (eq["NET"] / eq["S"])
be_fy = ef["FIXED"] / ef["N"] / (ef["NET"] / ef["S"])
text(s, 56, y + 16, 1016, 70,
     [f"損益分岐の月商は、通年の広告費込み限界利益率（{ef['NET'] / ef['S'] * 100:.1f}%）なら約[[{be_fy:.0f}百万円]]、"
      f"直近四半期の率（{eq['NET'] / eq['S'] * 100:.1f}%）なら約{be_q:.0f}百万円。",
      f"26年9月期の月平均は{fy_s[2] / 12:.1f}百万円"], size=19, bold=True, spacing=1.45)
footnote(s, "※ 損益分岐＝直接固定費÷広告費込み限界利益率。固定費が売上に比例して増えない前提の概算")

# ---- LTV/CAC
cac26 = fy_ad[2] * 1e6 / NEW26
cac25 = fy_ad[1] * 1e6 / LTV25["new"]
gp12 = LTV25["sales12"] * GP_RATE26_SMALL / 100
first_gp26 = FIRST_GP26
ratio = gp12 / cac26
ratio_s = LTV25["sales12"] / cac26
seg_best = SEGMENTS[0]
seg_ratio = {n_: g_ / cac26 for n_, t_, nw_, c_, a_, r_, g_, f_ in SEGMENTS}
s = content_slide("LTV/CAC：広告で獲得する層と、成り立つセグメント", "自社サイトの顧客単位。大口（請求書払いの契約先）は広告を使わないので分けて見る　※税抜")
x, w = 56, 470
rect(s, x, 150, w, 6, HANA)
text(s, x, 172, w, 34, "広告で獲得する層：新規顧客1人あたりの採算", size=21, bold=True)
text(s, x, 214, 230, 22, "LTV/CAC（限界利益ベース）", size=13, color=SECONDARY, bold=True)
tb = text(s, x, 236, 230, 66, f"{ratio:.1f}", size=56, bold=True, color=STRONG, en=True, spacing=1.0, anchor=MSO_ANCHOR.BOTTOM)
r = tb.text_frame.paragraphs[0].add_run()
r.text = "倍"
_set_font(r, 22, STRONG, True, en=False)
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
    ("初回購入の限界利益", "—", f"{first_gp26:,.0f}円"),
    ("限界利益率（この層）", "—", f"{GP_RATE26_SMALL:.1f}%"),
    ("12か月の購入回数", f"{LTV25['orders12']:.2f}回", "—"),
    ("12か月の売上（LTV・売上）", f"{LTV25['sales12']:,}円", "—"),
    ("12か月の限界利益（LTV）", f"{gp12:,.0f}円", "—"),
    ("リピート率（3か月以内）", f"{LTV25['rep3']:.1f}%", "—"),
    ("リピート率（12か月以内）", f"{LTV25['rep12']:.1f}%", "—"),
]
yy = 334
text(s, x + w - 250, yy, 120, 24, "25年9月期", size=14, color=SECONDARY, bold=True, align=PP_ALIGN.RIGHT)
text(s, x + w - 120, yy, 120, 24, "26年9月期", size=14, color=SECONDARY, bold=True, align=PP_ALIGN.RIGHT)
hline(s, x, yy + 30, w, MOSS, 1.5)
yy += 38
for lab, v1, v2 in rows_:
    bold_ = lab.startswith("12か月の限界利益") or lab.startswith("CAC")
    text(s, x, yy, w - 250, 30, lab, size=15, bold=bold_)
    text(s, x + w - 250, yy, 120, 30, v1, size=16, bold=bold_, align=PP_ALIGN.RIGHT, color=MUTED if v1 == "—" else MOSS)
    text(s, x + w - 120, yy, 120, 30, v2, size=16, bold=bold_, align=PP_ALIGN.RIGHT, color=MUTED if v2 == "—" else MOSS)
    yy += 34
    hline(s, x, yy - 8, w)
vline(s, 548, 150, 540)
# 右：セグメント別の1顧客あたりの採算（LTV/CACの高い順）。大口は別枠
x2, w2 = 568, 504
rect(s, x2, 150, w2, 6, MOSS)
text(s, x2, 172, w2, 34, "セグメント別の採算（LTV/CACの高い順）", size=21, bold=True)
text(s, x2, 214, w2, 22, "LTV＝26年9月期の顧客1人あたりの年間限界利益。CACは左と同じ値", size=12, color=SECONDARY)
# 大口の帯
by = 246
rect(s, x2, by, w2, 64, HANA_LIGHT)
text(s, x2 + 14, by + 6, 200, 26, "大口（請求書払い・営業で獲得）", size=13, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
text(s, x2 + 14, by + 32, w2 - 28, 24,
     f"{BIG['n']}社で限界利益の{BIG['gp_share']}%（{BIG['gp']:.1f}百万円、1社あたり年{BIG['gp'] / BIG['n'] * 100:.0f}万円）。広告CACはかからない。前期の{BIG['n25']}社中{BIG['retained']}社が継続",
     size=11, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
# 表頭
ty = by + 80
C_NAME, C_BAR, C_BARW, C_NEW, C_GP = x2, x2 + 164, 190, x2 + 372, x2 + 430
text(s, C_NAME, ty, 160, 22, "セグメント", size=11, color=SECONDARY, bold=True)
text(s, C_BAR, ty, C_BARW, 22, "LTV/CAC", size=11, color=SECONDARY, bold=True)
text(s, C_NEW, ty, 56, 22, "新規", size=11, color=SECONDARY, bold=True, align=PP_ALIGN.RIGHT)
text(s, C_GP, ty, 74, 22, "年間限界利益", size=11, color=SECONDARY, bold=True, align=PP_ALIGN.RIGHT)
hline(s, x2, ty + 26, w2, MOSS, 1.5)
RH_ = 38
ry0 = ty + 32
rmax = 1.5
cac_x = C_BAR + C_BARW * (1.0 / rmax)
for i, (n_, t_, nw_, c_, a_, r_, g_, f_) in enumerate(SEGMENTS):
    ry = ry0 + i * RH_
    rt = g_ / cac26
    text(s, C_NAME, ry, 120, RH_, n_, size=13, bold=rt >= 1, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, C_NAME + 122, ry, 40, RH_, t_, size=9, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0, en=True)
    bw2 = C_BARW * min(rt, rmax) / rmax
    rect(s, C_BAR, ry + 9, bw2, RH_ - 18, HANA if rt >= 1 else HANA_LIGHT)
    text(s, C_BAR + bw2 + 6, ry, 60, RH_, f"{rt:.1f}倍", size=12, bold=True, color=MOSS if rt >= 1 else STRONG, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, C_NEW, ry, 56, RH_, f"{nw_:,}", size=13, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0, en=True)
    text(s, C_GP, ry, 74, RH_, f"{g_:,}円", size=13, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    hline(s, x2, ry + RH_, w2, BORDER_LIGHT, 0.75)
vline(s, cac_x, ry0 - 4, RH_ * len(SEGMENTS) + 8, STRONG, 1.25, dash=True)
text(s, cac_x - 50, ry0 + RH_ * len(SEGMENTS) + 4, 100, 18, "CAC＝LTV", size=10, color=STRONG, align=PP_ALIGN.CENTER, bold=True)
text(s, 56, 694, 1016, 60,
     [f"広告で獲得する層でCACを上回るのは{seg_best[0]}（{seg_ratio[seg_best[0]]:.1f}倍）だけで、レッスン・お稽古が{seg_ratio['レッスン・お稽古']:.1f}倍。"
      f"新規の半分を占める自宅鑑賞用・ギフトは{seg_ratio['自宅鑑賞用・ギフト']:.1f}倍。",
      f"限界利益の{BIG['gp_share']}%は営業で獲得した大口{BIG['n']}社。広告は販売・レッスンなど事業者セグメントに寄せ、個人向けはオーガニック中心にする"],
     size=16, bold=True, spacing=1.45)
footnote(s, "※ 匿名化した受注・顧客データを顧客単位で集計（社内アカウント・返金は除外）。広告で獲得する層＝会員・ゲスト（割引区分A・Z）、大口＝請求書払いの契約先（区分B〜E）。"
            f"12か月LTVは25年9月期に初回購入した顧客の12か月の売上×この層の限界利益率{GP_RATE26_SMALL:.1f}%。セグメントは顧客登録の用途・主な使い方から分類（マーケダッシュボードと同じ7区分、未分類は除く）。"
            "CACは広告費をすべて新規獲得にかかったとみなした値で、セグメント別には分けられないため共通")

# ---- リピートの状況（卸のサービスなので、LTV/CACよりリピートの積み上がりで採算を見る）
s = content_slide("リピートの状況：顧客基盤の積み上がり", "卸のサービスなので、LTV/CACよりもリピートの積み上がりで見る　※自社サイトの受注のみ")
NM = len(REP_YM)
rep_ratio = [r / o * 100 for r, o in zip(REP_REPEAT, REP_ORDERS)]
cum_share = [r / c * 100 for r, c in zip(REP_CUM_REP, REP_CUM)]


def panel(x, y, w, h, title):
    text(s, x, y, w, 24, title, size=15, bold=True)
    return x, y + 50, w, h - 50


def month_axis(x, y, w, slot_w, n, base_y):
    for i in range(n):
        y_, m_ = REP_YM[i]
        if m_ in (1, 4, 7, 10):
            text(s, x + i * slot_w - 10, base_y + 4, slot_w + 20, 16, f"{str(y_)[2:]}/{m_}", size=9, color=MUTED, align=PP_ALIGN.CENTER, en=True)


PW, PH_ = 488, 250
# A: 月ごとのリピート注文数（棒）と、注文に占めるリピート比率（線）
px_, py_, pw_, ph_ = panel(56, 150, PW, PH_, "月ごとのリピート注文数と、注文に占める比率")
cx0, cx1 = px_ + 36, px_ + pw_ - 40
top_, base_ = py_ + 20, py_ + ph_ - 30
slot_ = (cx1 - cx0) / NM
vmax_ = 220
yv = lambda v: base_ - (base_ - top_) * v / vmax_
for v in (0, 100, 200):
    hline(s, cx0, yv(v), cx1 - cx0, BORDER_LIGHT if v == 0 else WATERMARK)
    text(s, px_, yv(v) - 8, 32, 16, str(v), size=9, color=MUTED, align=PP_ALIGN.RIGHT, en=True)
for i in range(NM):
    rect(s, cx0 + i * slot_ + slot_ * 0.2, yv(REP_REPEAT[i]), slot_ * 0.6, base_ - yv(REP_REPEAT[i]), HANA)
ry_ = lambda v: base_ - (base_ - top_) * v / 60
L0 = 2  # 注文が少ない25年1〜2月は比率の線から外す
polyline(s, [(cx0 + i * slot_ + slot_ / 2, ry_(rep_ratio[i])) for i in range(L0, NM)], MOSS, 2.0)
for v in (20, 40, 60):
    text(s, cx1 + 4, ry_(v) - 8, 36, 16, f"{v}%", size=9, color=MUTED, en=True)
text(s, cx0 + L0 * slot_ - 16, ry_(rep_ratio[L0]) - 20, slot_ + 32, 16, f"{rep_ratio[L0]:.0f}%", size=10, bold=True, align=PP_ALIGN.CENTER, en=True)
text(s, cx0 + (NM - 1) * slot_ - 60, ry_(rep_ratio[-1]) - 8, 56, 16, f"{rep_ratio[-1]:.0f}%", size=10, bold=True, align=PP_ALIGN.RIGHT, en=True)
text(s, cx0 + (NM - 1) * slot_ - 16, yv(REP_REPEAT[-1]) - 18, slot_ + 32, 16, f"{REP_REPEAT[-1]}", size=10, bold=True, align=PP_ALIGN.CENTER, en=True)
month_axis(cx0, 0, 0, slot_, NM, base_)
rect(s, cx0, py_ - 6, 10, 10, HANA)
text(s, cx0 + 14, py_ - 12, 120, 22, "リピート注文数", size=10, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
rect(s, cx0 + 110, py_ - 2, 20, 3, MOSS)
text(s, cx0 + 134, py_ - 12, 160, 22, "リピート比率（右軸）", size=10, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)

# B: 月ごとの購入顧客数（新規／リピート）
px_, py_, pw_, ph_ = panel(584, 150, PW, PH_, "月ごとの購入顧客数（新規とリピート）")
cx0, cx1 = px_ + 36, px_ + pw_ - 40
top_, base_ = py_ + 20, py_ + ph_ - 30
vmax_ = 380
yv = lambda v: base_ - (base_ - top_) * v / vmax_
for v in (0, 100, 200, 300):
    hline(s, cx0, yv(v), cx1 - cx0, BORDER_LIGHT if v == 0 else WATERMARK)
    text(s, px_, yv(v) - 8, 32, 16, str(v), size=9, color=MUTED, align=PP_ALIGN.RIGHT, en=True)
for i in range(NM):
    bx = cx0 + i * slot_ + slot_ * 0.2
    rect(s, bx, yv(REP_ACTIVE_REP[i]), slot_ * 0.6, base_ - yv(REP_ACTIVE_REP[i]), HANA)
    rect(s, bx, yv(REP_ACTIVE[i]), slot_ * 0.6, yv(REP_ACTIVE_REP[i]) - yv(REP_ACTIVE[i]), HANA_LIGHT)
text(s, cx0 + (NM - 1) * slot_ - 16, yv(REP_ACTIVE[-1]) - 18, slot_ + 32, 16, f"{REP_ACTIVE[-1]}", size=10, bold=True, align=PP_ALIGN.CENTER, en=True)
month_axis(cx0, 0, 0, slot_, NM, base_)
rect(s, cx0, py_ - 6, 10, 10, HANA)
text(s, cx0 + 14, py_ - 12, 120, 22, "リピート購入", size=10, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
rect(s, cx0 + 100, py_ - 6, 10, 10, HANA_LIGHT)
text(s, cx0 + 114, py_ - 12, 120, 22, "初回購入", size=10, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)

# C: リピーター人数（累計）と全顧客に占める割合
px_, py_, pw_, ph_ = panel(56, 418, PW, PH_, "リピーターの累計と、購入ありアカウントに占める割合")
cx0, cx1 = px_ + 36, px_ + pw_ - 40
top_, base_ = py_ + 20, py_ + ph_ - 30
vmax_ = 600
yv = lambda v: base_ - (base_ - top_) * v / vmax_
for v in (0, 200, 400, 600):
    hline(s, cx0, yv(v), cx1 - cx0, BORDER_LIGHT if v == 0 else WATERMARK)
    text(s, px_, yv(v) - 8, 32, 16, str(v), size=9, color=MUTED, align=PP_ALIGN.RIGHT, en=True)
for i in range(NM):
    rect(s, cx0 + i * slot_ + slot_ * 0.2, yv(REP_CUM_REP[i]), slot_ * 0.6, base_ - yv(REP_CUM_REP[i]), HANA)
ry_ = lambda v: base_ - (base_ - top_) * v / 60
polyline(s, [(cx0 + i * slot_ + slot_ / 2, ry_(cum_share[i])) for i in range(L0, NM)], MOSS, 2.0)
for v in (20, 40, 60):
    text(s, cx1 + 4, ry_(v) - 8, 36, 16, f"{v}%", size=9, color=MUTED, en=True)
for i in (L0, NM - 1):
    text(s, cx0 + i * slot_ - 16, ry_(cum_share[i]) - 20, slot_ + 32, 16, f"{cum_share[i]:.0f}%", size=10, bold=True, align=PP_ALIGN.CENTER, en=True)
text(s, cx0 + (NM - 1) * slot_ - 20, yv(REP_CUM_REP[-1]) - 18, slot_ + 40, 16, f"{REP_CUM_REP[-1]:,}", size=10, bold=True, align=PP_ALIGN.CENTER, en=True)
month_axis(cx0, 0, 0, slot_, NM, base_)
rect(s, cx0, py_ - 6, 10, 10, HANA)
text(s, cx0 + 14, py_ - 12, 120, 22, "リピーター数（累計）", size=10, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
rect(s, cx0 + 140, py_ - 2, 20, 3, MOSS)
text(s, cx0 + 164, py_ - 12, 200, 22, "購入ありに占める割合（右軸）", size=10, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)

# D: 初回購入の四半期ごとのリピート率（90日／180日以内）
px_, py_, pw_, ph_ = panel(584, 418, PW, PH_, "初回購入からのリピート率（初回購入の四半期ごと）")
cx0, cx1 = px_ + 36, px_ + pw_ - 10
top_, base_ = py_ + 20, py_ + ph_ - 44
nq_ = len(COHORT)
slotq = (cx1 - cx0) / nq_
vmax_ = 30
yv = lambda v: base_ - (base_ - top_) * v / vmax_
for v in (0, 10, 20, 30):
    hline(s, cx0, yv(v), cx1 - cx0, BORDER_LIGHT if v == 0 else WATERMARK)
    text(s, px_, yv(v) - 8, 32, 16, f"{v}%", size=9, color=MUTED, align=PP_ALIGN.RIGHT, en=True)
for i, (lab, n_, r90, r180) in enumerate(COHORT):
    bx = cx0 + i * slotq + slotq * 0.15
    bwq = slotq * 0.3
    rect(s, bx, yv(r90), bwq, base_ - yv(r90), HANA)
    rect(s, bx + bwq + 4, yv(r180), bwq, base_ - yv(r180), HANA_LIGHT)
    text(s, bx - 10, yv(r90) - 16, bwq + 20, 14, f"{r90:.0f}", size=9, bold=True, align=PP_ALIGN.CENTER, en=True)
    text(s, bx + bwq - 6, yv(r180) - 16, bwq + 20, 14, f"{r180:.0f}", size=9, bold=True, color=SECONDARY, align=PP_ALIGN.CENTER, en=True)
    text(s, cx0 + i * slotq, base_ + 4, slotq, 16, lab, size=9, color=MUTED, align=PP_ALIGN.CENTER)
    text(s, cx0 + i * slotq, base_ + 18, slotq, 16, f"{n_}人", size=9, color=MUTED, align=PP_ALIGN.CENTER)
rect(s, cx0, py_ - 6, 10, 10, HANA)
text(s, cx0 + 14, py_ - 12, 120, 22, "90日以内", size=10, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
rect(s, cx0 + 80, py_ - 6, 10, 10, HANA_LIGHT)
text(s, cx0 + 94, py_ - 12, 160, 22, "180日以内", size=10, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)

text(s, 56, 676, 1016, 60,
     [f"リピート注文は月{REP_REPEAT[0]}件（25年1月）→ {REP_REPEAT[-1]}件（26年9月）、比率は{rep_ratio[-1]:.0f}%。2回以上購入は{REP_CUM_REP[-1]:,}（購入あり{ACCOUNTS_BOUGHT:,}アカウントの{cum_share[-1]:.0f}%、登録は{ACCOUNTS_TOTAL:,}）。",
      f"初回から90日以内のリピート率は{min(c[2] for c in COHORT):.0f}〜{max(c[2] for c in COHORT):.0f}%で、26年1〜3月の新規が最も高い"],
     size=16, bold=True, spacing=1.45)
footnote(s, "※ 自社サイトの受注を顧客単位で集計（キャンセル・テスト注文は除く。フラワーボックス等のイネイブラー事業は含まない）。リピーター＝2回以上購入した顧客。リピート注文＝同じ顧客の2回目以降の注文。180日以内は90日以内を含む。累計は2024年2月の開始から。比率の線は注文が少ない25年1〜2月を除く")


# ---- 損益分岐に必要な月商
s = content_slide("損益分岐に必要な月商", "貢献利益が0になる月商と、26年9月期の月平均の売上　単位：百万円/月" + PH)
fixed_m = FIXED["SHIP"] + FIXED["RENT"]
act = fy_s[2] / 12
peak = max(S[20:32])
rows3 = [("通年の率（26年9月期）", ef["NET"] / ef["S"], be_fy), ("直近四半期の率（26年7〜9月）", eq["NET"] / eq["S"], be_q)]
bx0, bwid = 330, 600
vmax_ = max(be_fy, be_q, peak) * 1.1
y0 = 168
text(s, 56, y0, 400, 36, "損益分岐の月商", size=24, bold=True, anchor=MSO_ANCHOR.MIDDLE)
text(s, 460, y0, 612, 36, f"直接固定費 {fixed_m:.2f}百万円/月（発送人件費{FIXED['SHIP']:.2f}＋拠点費{FIXED['RENT']:.2f}）", size=15, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE)
yy = y0 + 48
for lab, m_, be in rows3:
    text(s, 56, yy, 270, 36, [lab, f"広告費込み限界利益率 {m_ * 100:.1f}%"], size=14, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.2)
    rect(s, bx0, yy + 10, bwid * be / vmax_, 24, MOSS)
    text(s, bx0 + bwid * be / vmax_ + 10, yy, 120, 36, f"{be:.1f}", size=17, bold=True, en=True, anchor=MSO_ANCHOR.MIDDLE)
    yy += 56
for lab, v, c_ in (("26年9月期の月平均", act, HANA), ("26年9月期の最高月", peak, BG_GRAY)):
    text(s, 56, yy, 270, 36, lab, size=16, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE)
    rect(s, bx0, yy + 10, bwid * v / vmax_, 24, c_)
    text(s, bx0 + bwid * v / vmax_ + 10, yy, 120, 36, f"{v:.1f}", size=17, bold=True, en=True, anchor=MSO_ANCHOR.MIDDLE)
    yy += 44
hline(s, 56, yy + 8, 1016)
rs = REPEAT_SHARE[1] / 100
new_need = be_fy * 1e6 * (1 - rs) / AOV26
mult = be_fy / act
text(s, 56, yy + 40, 1016, 160,
     [f"通年の率なら損益分岐の月商は約{be_fy:.1f}百万円で、26年9月期の月平均{act:.1f}百万円は[[わずかに上回る]]（貢献利益 +{ef['CONTRIB']:.1f}百万円）。",
      f"直近四半期は広告費を増やして広告費込み限界利益率が{eq['NET'] / eq['S'] * 100:.0f}%に下がり、損益分岐は約{be_q:.0f}百万円に上がる。",
      f"直接固定費が小さい事業なので、損益は広告効率と仕入れ原価（広告費込み限界利益率）でほぼ決まる。発送人件費は生花売上の約{SHIP_LABOR_RATE * 100:.0f}%で、売上とともに増える"],
     size=18, bold=True, spacing=1.5)
footnote(s, f"※ 損益分岐＝直接固定費÷広告費込み限界利益率。直接固定費＝発送人件費{FIXED['SHIP']:.2f}＋拠点費{FIXED['RENT']:.2f}百万円/月。発送人件費は26年8月の作業時間×時給からの概算")

# =====================================================================
# 要約（数字が出そろってから）
# =====================================================================
draw_claims(summary_slide, [
    ("1", "売上は3期で拡大、限界利益率は30%台を維持", [
        f"売上は{fy_s[0]:.0f} → {fy_s[1]:.0f} → {fy_s[2]:.0f}百万円（24年9月期は8か月）。ボックス等を含めると{fy_tot[0]:.0f} → {fy_tot[1]:.0f} → {fy_tot[2]:.0f}百万円",
        f"限界利益率は{fy_gp[1] / fy_s[1] * 100:.0f} → {fy_gp[2] / fy_s[2] * 100:.0f}%（生花 約{CAT_MARGIN['生花']:.0f}%※、植木鉢 約{CAT_MARGIN['植木鉢']:.0f}%）。広告費込み限界利益は{fy_net[1]:.1f} → {fy_net[2]:.1f}百万円"]),
    ("2", "広告は生花の新規獲得に集中。植木鉢はホームセンターへの営業等を実施", [
        f"CAC {cac26:,.0f}円に対し、初回の限界利益{first_gp26:,.0f}円、12か月の限界利益LTV {gp12:,.0f}円（LTV/CAC {ratio:.1f}倍）",
        f"CACを上回るセグメントは販売（{seg_ratio['販売']:.1f}倍）だけ。レッスン・お稽古{seg_ratio['レッスン・お稽古']:.1f}倍、自宅鑑賞用・ギフト{seg_ratio['自宅鑑賞用・ギフト']:.1f}倍",
        f"限界利益の{BIG['gp_share']}%は営業で獲得した大口{BIG['n']}社（広告CACなし）。広告で獲得する層の限界利益率は約{GP_RATE26_SMALL:.0f}%"]),
    ("3", "収益化の鍵は、リピート顧客（事業者）の積み上げと広告費込み限界利益率の改善", [
        f"売上の{REPEAT_SHARE[1]:.0f}%は2回目以降の注文。1注文あたりの売上はリピート{REPEAT_AOV[1]:,}円、初回{AOV26:,}円（約{REPEAT_AOV[1] / AOV26:.0f}倍）",
        f"リピート注文は月{REP_REPEAT[0]} → {REP_REPEAT[-1]}件、2回以上購入は{REP_CUM_REP[-1]:,}アカウント（購入ありアカウントの{REP_CUM_REP[-1] / ACCOUNTS_BOUGHT * 100:.0f}%）",
        f"現状は直接固定費は月{fixed_m:.2f}百万円と小さく、通年の貢献利益は+{ef['CONTRIB']:.1f}百万円。損益は広告効率と原価で決まる"]),
], y=124, color=HANA)
footnote(summary_slide, "※ 数値は税抜。生花の限界利益率は花材により変動（15%前後）。現状は少量仕入れのため仲卸などからも仕入れており、原価率が高くなっている。用語の定義と集計の前提は最終ページ")

# =====================================================================
# 章 03：中長期の可能性とシナジー
# =====================================================================
divider("03", "GROWTH & SYNERGY", "中長期の可能性と事業間シナジー", "卸仕入れサイトからの広がり、アンドフラワー／アンドプランツとの連携")

# ---- 中長期の可能性：卸仕入れサイトを起点に、花屋・植物屋向けのサービスを広げる
s = content_slide("中長期の可能性：卸仕入れサイトを起点に広げる", "花屋・植物屋・事業者との取引接点を持つことで、仕入れ以外のサービスに展開できる")
STEPS = [
    ("01", "卸仕入れサイト", "現在", ["花・植物・資材の仕入れEC", "生花SKUの拡充、法人・店舗の\nリピート顧客の積み上げ"], HANA),
    ("02", "情報サービス", "次の一歩", ["売れ筋・相場・産地の情報提供", "小売・卸の販売情報を生産側に\nつなぐ"], HANA_LIGHT),
    ("03", "人材紹介", "中期", ["花屋・植物屋・生産者の\n採用支援", "取引先ネットワークを活かした\nマッチング"], WATERMARK),
    ("04", "決済関連", "中長期", ["請求書払い・後払いの提供", "取引データをもとにした\n与信・資金繰り支援"], WATERMARK),
]
bx, bw_, gap = 56, 238, 21
y0, bh = 170, 330
for k, (num, name, when, lines_, col) in enumerate(STEPS):
    x = bx + k * (bw_ + gap)
    rect(s, x, y0, bw_, 8, col)
    text(s, x, y0 + 24, bw_, 40, num, size=34, color=HANA_DARK if k else HANA_DARK, bold=True, en=True, spacing=1.0)
    text(s, x, y0 + 70, bw_, 36, name, size=24, bold=True)
    text(s, x, y0 + 108, bw_, 24, when, size=14, color=SECONDARY, bold=True)
    yy = y0 + 148
    for ln_ in lines_:
        rect(s, x + 2, yy + 11, 7, 7, HANA_DARK)
        text(s, x + 16, yy, bw_ - 16, 60, ln_, size=14, color=SECONDARY, spacing=1.35)
        yy += 64
    if k < len(STEPS) - 1:
        text(s, x + bw_ - 2, y0 + 60, gap + 4, 40, "›", size=30, color=MUTED, align=PP_ALIGN.CENTER, en=True)
hline(s, 56, y0 + bh + 20, 1016)
text(s, 56, y0 + bh + 44, 1016, 120,
     ["仕入れで日常的に使われる接点を持つほど、同じ顧客に対して情報・人材・決済のサービスを重ねやすくなる。",
      "Domuzの花卉産業DXプラットフォームでは、ハナイチは花屋・植物屋とのB向けの接点にあたり、",
      "生花イネイブラー（異業種への花の販売機能）や生産者ロールアップへの送客・販売情報の起点になる"],
     size=17, bold=True, spacing=1.5)
footnote(s, "※ 02〜04は構想段階。いずれも仕入れサイトの取引先と取引データを前提にしたサービスで、順序や時期は今後の検討による")

# ---- 事業間シナジー
s = content_slide("事業間シナジー", "アンドフラワー・アンドプランツとの連携。現在すでに動いているものと、これから広げられるもの")
COLS = [
    ("アンドフラワー", FLOWER, [
        ("生花の仕入れ", "アンドフラワーの生花の仕入れを、ハナイチの仕入れ機能（市場・産地との取引）で担い、仕入れ量をまとめて仕入れ力を高める"),
        ("余剰在庫の販売", "アンドフラワー拠点の生花の余りを、ハナイチで「サンキューフラワー」（タイムセール）として事業者に販売し、ロスを減らす"),
        ("拠点・スタッフの共有", "川崎の花拠点とスタッフを共有し、生花の仕入れ・加工・発送の固定費を2事業で分け合う"),
    ]),
    ("アンドプランツ", LIGHT, [
        ("植木鉢・資材の仕入れ", "観葉植物に合わせる植木鉢・資材を、ハナイチの卸の仕入れルートで共通化し、原価を下げる"),
        ("商品・顧客の相互送客", "アンドプランツの法人・店舗の顧客にハナイチの仕入れを、ハナイチの事業者にアンドプランツの観葉植物を案内する"),
        ("販売情報の共有", "小売（アンドプランツ）で売れている商品の情報を、ハナイチの品揃えと生産側の企画に活かす"),
    ]),
]
for k, (name, col, items_) in enumerate(COLS):
    x = 56 + k * 528
    w = 488
    rect(s, x, 150, w, 6, col)
    text(s, x, 172, w, 34, f"ハナイチ × {name}", size=23, bold=True, color=MOSS)
    yy = 220
    for j, (head, body) in enumerate(items_):
        tag = "現在" if (k == 0 and j < 2) else ("現在" if (k == 1 and j == 0) else "今後")
        rect(s, x, yy, 56, 26, HANA if tag == "現在" else WATERMARK)
        text(s, x, yy, 56, 26, tag, size=12, bold=True, color=MOSS, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        text(s, x + 68, yy, w - 68, 26, head, size=17, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        text(s, x, yy + 32, w, 80, body, size=14, color=SECONDARY, spacing=1.4)
        yy += 118
        if j < len(items_) - 1:
            hline(s, x, yy - 14, w)
vline(s, 564, 150, 520)
text(s, 56, 690, 1016, 60,
     ["生花の仕入れと余剰在庫の販売はすでに運用中。拠点・仕入れ・顧客を共有することで、",
      "ハナイチ単体では吸収しにくい固定費を、事業間で薄められる"], size=17, bold=True, spacing=1.45)
footnote(s, "※ 「現在」は運用中の連携、「今後」は構想。アンドフラワーの余剰在庫の販売は2026年5月末に開始")

# ---- 仕入れが増えるほど効く：花市場起点のスケールメリット
s = content_slide("仕入れが増えるほど効く：花市場起点のスケールメリット", "ハナイチの卸が伸びるほど、生花の仕入れ量がまとまり、交渉力と売価の両方に事業横断で効く")
FLOW = [
    ("01", "ハナイチの卸が伸びる", "小売店・事業者のリピートが積み上がり、生花の仕入れ量が増える"),
    ("02", "仕入れを一本にまとめる", "アンドフラワー・イネイブラーの生花も同じ仕入れに乗せ、ロットを大きくする"),
    ("03", "交渉力が上がる", "市場・産地・輸入（卸や海外からの直接仕入れ）に対して、価格と品揃えで条件を引き出せる"),
    ("04", "原価率が下がり、品揃えが安定する", "同じ売価でも限界利益率が上がる。安定して仕入れられる品目が増える"),
]
bx, bw_, gap = 56, 238, 21
y0 = 160
for k, (num, name, desc) in enumerate(FLOW):
    x = bx + k * (bw_ + gap)
    rect(s, x, y0, bw_, 8, HANA)
    text(s, x, y0 + 22, bw_, 36, num, size=30, color=HANA_DARK, bold=True, en=True, spacing=1.0)
    text(s, x, y0 + 62, bw_, 56, name, size=18, bold=True, spacing=1.25)
    text(s, x, y0 + 124, bw_, 80, desc, size=13, color=SECONDARY, spacing=1.4)
    if k < len(FLOW) - 1:
        text(s, x + bw_ - 2, y0 + 56, gap + 4, 40, "›", size=30, color=MUTED, align=PP_ALIGN.CENTER, en=True)
# 下：各事業へのインパクト
hline(s, 56, 380, 1016)
text(s, 56, 396, 1016, 28, "売価と限界利益へのインパクト（事業横断）", size=18, bold=True)
IMP = [
    ("B向け：ハナイチ", HANA, "卸価格を下げても限界利益を保てるので、生花小売店や大口（式場・葬儀社）を取りにいきやすくなる"),
    ("C向け：アンドフラワー", FLOWER, "同じ売価で限界利益率が上がる。母の日など繁忙期の原価と欠品リスクを下げられる"),
    ("イネイブラー：フラワーボックス", HANA_LIGHT, "花材原価が下がるぶん、法人向けの提案価格に幅ができ、ロットの大きい案件を取りやすくなる"),
]
for k, (name, col, body) in enumerate(IMP):
    x = 56 + k * 345
    w = 324
    rect(s, x, 436, w, 6, col)
    text(s, x, 452, w, 30, name, size=16, bold=True)
    text(s, x, 486, w, 90, body, size=13, color=SECONDARY, spacing=1.4)
# 感応度：仕入れ原価が5%下がった場合
cogs = {"ハナイチ": fy_s[2] - fy_gp[2], "アンドフラワー": 87.1, "フラワーボックス等": fy_fb[2] - fy_fbgp[2]}
imp5 = {k_: v_ * 0.05 for k_, v_ in cogs.items()}
total5 = sum(imp5.values())
text(s, 56, 596, 1016, 90,
     [f"目安：仕入れ原価等が5%下がると、26年9月期の規模でも年{total5:.0f}百万円の限界利益改善（アンドフラワー{imp5['アンドフラワー']:.1f}、ハナイチ{imp5['ハナイチ']:.1f}、ボックス等{imp5['フラワーボックス等']:.1f}百万円）。",
      "仕入れ量が増えるほど交渉力が上がり、その効果が3事業の売価と限界利益に同時に効く。これが花市場起点で卸を伸ばす理由"],
     size=16, bold=True, spacing=1.5)
footnote(s, "※ 原価等＝売上−限界利益（商品原価のほか送料・資材・決済手数料を含む）。26年9月期：アンドフラワー87.1、ハナイチ"
            f"{cogs['ハナイチ']:.1f}、フラワーボックス等{cogs['フラワーボックス等']:.1f}百万円。5%は仮の感応度で、交渉の成果に応じて変わる")


# ---- 用語と集計の前提
terms = content_slide("用語と集計の前提")
TERMS = [
    ("期", "9月決算。「26年9月期」＝2025年10月〜2026年9月。24年9月期は2024年2月〜9月の8か月"),
    ("売上", "税抜・注文日ベースの純売上（確定請求額−返金）。自社サイトのみ、キャンセル・テスト注文は除く。フラワーボックス等（イネイブラー事業）は推移ページにのみ参考で含める"),
    ("限界利益", "売上 − 商品原価・送料・資材・決済手数料。ハナイチ管理画面の「粗利」と同じ定義で、AP/AFの限界利益に相当"),
    ("広告費", "Google・Meta・Yahoo!・Microsoft・Pinterest の広告費（税抜）。広告は生花のみ"),
    ("広告費込み限界利益", "限界利益 − 広告費"),
    ("全体ROAS", "売上 ÷ 広告費。分子は生花以外（植木鉢・資材）も含むサイト全体の売上"),
    ("直接固定費", "発送人件費（月0.33百万円。26年8月の作業時間×時給の概算、生花売上の約11%）＋拠点費（川崎拠点の家賃の20%＝月0.19百万円）"),
    ("貢献利益", "広告費込み限界利益 − 直接固定費。本社の人件費・共通費は含まない"),
    ("アカウント", "登録3,728アカウントのうち、2024年2月以降に購入のある2,542を顧客として集計（受注データの顧客ID）"),
    ("大口／セグメント", "大口＝請求書払いの契約先（割引区分B〜E、営業で獲得）。広告で獲得する層＝会員・ゲスト（区分A・Z）。セグメントは顧客登録の用途・主な使い方から分類（マーケダッシュボードの7区分）"),
    ("出典", "ハナイチ管理画面（売上・限界利益）、Marketing Master（広告費）、匿名化した受注・顧客データ（顧客単位のLTV・セグメント）"),
]
y = 150
hline(terms, 56, y, 1016)
for k_, v_ in TERMS:
    rh_ = 60 if len(TERMS) > 10 else 64
    text(terms, 56, y, 236, rh_, k_, size=19, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(terms, 300, y, 772, rh_, v_, size=16, color=SECONDARY, spacing=1.35, anchor=MSO_ANCHOR.MIDDLE)
    y += rh_
    hline(terms, 56, y, 1016)

prs.save("hanaichi_economics_2026-10.pptx")
print("saved", len(prs.slides._sldIdLst), "slides")
print("FY", [round(v, 1) for v in fy_s], [round(v, 1) for v in fy_ad], [round(v, 1) for v in fy_net])
print({k: {kk: round(vv, 2) for kk, vv in P["e"].items()} for k, P in PERIODS.items()})
print("cac", round(cac26), round(cac25), "ltv", round(gp12), "ratio", round(ratio, 2), "be", round(be_fy, 1), round(be_q, 1))
