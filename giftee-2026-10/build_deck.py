"""ギフティ様向け 事業エコノミクス資料 — Domuz デザインシステム v2.1「発表スライド」型で .pptx を生成する。

retreat-2026-10/build_deck.py と同じ型（4:3・1128×846px 基準、Google スライドへは Drive の pptx 変換で取り込む）。

データの出どころ:
- AP/AF/ハナイチの月次（売上・限界利益・ROAS）: BigQuery and-plants の事業別月次エコノミクス（注文日ベース・税抜）
  26年6月までは「直近4期 月次エコノミクス」の広告費込み限界利益、26年7〜9月は 限界利益 − 売上÷ROAS で算出
- 現在のエコノミクス（AP/AF）: #リーダー 26年9月 貢献利益（速報値、AP Marketing Master ベース）
- 川崎拠点: スプレッドシート「花拠点_坪単位売上効率_月次推移」
"""
import os
import re

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu

# ---- デザイントークン（design-system/domuz_design_system.md §2） ----
MOSS = RGBColor(0x00, 0x43, 0x47)        # --brand-primary / --text-primary
LIGHT = RGBColor(0x00, 0xD7, 0x9C)       # --brand-secondary
FLOWER = RGBColor(0xEF, 0x66, 0x7D)      # --brand-flower
FLOWER_LIGHT = RGBColor(0xF7, 0xB3, 0xBE)  # 花の薄い色
SECONDARY = RGBColor(0x62, 0x62, 0x62)   # --text-secondary
STRONG = RGBColor(0xE1, 0x64, 0x64)      # --text-strong
MUTED = RGBColor(0x99, 0x99, 0x99)       # --text-muted
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BG_GRAY = RGBColor(0xCB, 0xD0, 0xD3)     # --bg-gray
BORDER_LIGHT = RGBColor(0xC9, 0xCF, 0xCF)
WATERMARK = RGBColor(0xEC, 0xEE, 0xEE)   # --watermark
PALE = RGBColor(0xE4, 0xE8, 0xE9)        # 売上の棒（背景寄りのグレー）

FONT_EN = "Montserrat"  # ギフティ向け株主報告資料と同じ
FONT_JA = "Zen Kaku Gothic New"  # 和文はデザインシステムの指定フォント（Montserrat にない文字を補う）

W_PX, H_PX = 1128, 846
EMU_PER_PX = 9144000 / W_PX  # 10in 幅


def px(v):
    return Emu(int(round(v * EMU_PER_PX)))


def pt(px_size):
    """発表スライドの px サイズ → pt（38px ≒ 24pt）。"""
    return px_size * 24 / 38


prs = Presentation()
prs.slide_width = px(W_PX)
prs.slide_height = px(H_PX)
BLANK = prs.slide_layouts[6]
page_no = 0


def _set_font(run, size_px, color, bold, en=None):
    """英数字は Montserrat、和文は Noto Sans CJK JP（1つのランの中でも文字ごとに使い分けられる）。"""
    f = run.font
    f.size = Emu(int(pt(size_px) * 12700))
    f.bold = bold
    f.color.rgb = color
    f.name = FONT_EN
    rpr = run._r.get_or_add_rPr()
    for tag, face in (("a:ea", FONT_JA), ("a:cs", FONT_EN)):
        el = rpr.find(qn(tag))
        if el is None:
            el = rpr.makeelement(qn(tag), {})
            rpr.append(el)
        el.set("typeface", face)


def text(slide, x, y, w, h, lines, size=25, color=MOSS, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, spacing=1.5, en=None, letter=None, para_gap=0):
    """lines: 文字列 or 文字列のリスト。[[語]] はライトグリーン、!!語!! は赤、**語** は太字。"""
    tb = slide.shapes.add_textbox(px(x), px(y), px(w), px(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    tf.vertical_anchor = anchor
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, 0)
    if isinstance(lines, str):
        lines = [lines]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        if para_gap and i > 0:
            p.space_before = Emu(int(pt(para_gap) * 12700))
        for part in re.split(r"(\[\[.*?\]\]|\*\*.*?\*\*|!!.*?!!)", line):
            if not part:
                continue
            c, b = color, bold
            if part.startswith("[["):
                part, c, b = part[2:-2], LIGHT, True
            elif part.startswith("!!"):
                part, c, b = part[2:-2], STRONG, True
            elif part.startswith("**"):
                part, b = part[2:-2], True
            r = p.add_run()
            r.text = part
            _set_font(r, size, c, b, en)
            if letter:
                r.font._rPr.set("spc", str(int(letter * 100)))
    return tb


def _drop_style(shape):
    """テーマ由来の影（effectRef）を出さないよう、図形の p:style を外す。"""
    st = shape._element.find(qn("p:style"))
    if st is not None:
        shape._element.remove(st)


def rect(slide, x, y, w, h, fill, line=None, dash=False, shape=MSO_SHAPE.RECTANGLE, weight=1.5):
    s = slide.shapes.add_shape(shape, px(x), px(y), px(w), px(h))
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Emu(int(weight * 12700))
        if dash:
            s.line.dash_style = 4
    s.shadow.inherit = False
    _drop_style(s)
    return s


def hline(slide, x, y, w, color=BORDER_LIGHT, weight=1.0, dash=False):
    ln = slide.shapes.add_connector(1, px(x), px(y), px(x + w), px(y))
    ln.line.color.rgb = color
    ln.line.width = Emu(int(weight * 12700))
    if dash:
        ln.line.dash_style = 4
    _drop_style(ln)
    return ln


def vline(slide, x, y, h, color=BORDER_LIGHT, weight=1.0, dash=False):
    ln = slide.shapes.add_connector(1, px(x), px(y), px(x), px(y + h))
    ln.line.color.rgb = color
    ln.line.width = Emu(int(weight * 12700))
    if dash:
        ln.line.dash_style = 4
    _drop_style(ln)
    return ln


def polyline(slide, pts, color, weight=2.5):
    """pts: [(x_px, y_px), ...] を折れ線で描く（Google スライドでも図形として残る）。"""
    fb = slide.shapes.build_freeform(px(pts[0][0]), px(pts[0][1]), scale=1.0)
    fb.add_line_segments([(px(x), px(y)) for x, y in pts[1:]], close=False)
    s = fb.convert_to_shape()
    s.fill.background()
    s.line.color.rgb = color
    s.line.width = Emu(int(weight * 12700))
    s.shadow.inherit = False
    _drop_style(s)
    return s


def badge(slide, x, y, n, color=MOSS, d=22):
    """トピック番号の丸。"""
    rect(slide, x - d / 2, y - d / 2, d, d, color, shape=MSO_SHAPE.OVAL)
    text(slide, x - d / 2, y - d / 2, d, d, str(n), size=13, color=WHITE, bold=True, en=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)


def content_slide(title=None, sub=None):
    """白背景＋左端ライトグリーン縦帯8px＋左上タイトル＋右下ページ番号。"""
    global page_no
    page_no += 1
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, 8, H_PX, LIGHT)
    if title:
        text(s, 56, 44, 1000, 56, title, size=38, bold=True)
    if sub:
        text(s, 56, 104, 1000, 36, sub, size=20, color=SECONDARY)
    text(s, W_PX - 120, H_PX - 44, 80, 24, str(page_no), size=14, color=MUTED,
         align=PP_ALIGN.RIGHT, en=True)
    return s


def footnote(s, body):
    text(s, 56, H_PX - 84, 960, 40, body, size=13, color=SECONDARY, spacing=1.3)


def divider(num, en_label, title, sub=""):
    """P-3 章扉: Moss 全面＋アウトライン章番号＋英字 ALL CAPS＋和文タイトル。"""
    global page_no
    page_no += 1
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = MOSS
    tb = text(s, 80, 240, 400, 150, num, size=120, color=WHITE, en=True, spacing=1.0)
    rpr = tb.text_frame.paragraphs[0].runs[0].font._rPr
    for el in rpr.findall(qn("a:solidFill")):
        rpr.remove(el)
    ln = rpr.makeelement(qn("a:ln"), {"w": "19050"})
    sf = ln.makeelement(qn("a:solidFill"), {})
    sf.append(sf.makeelement(qn("a:srgbClr"), {"val": "FFFFFF"}))
    ln.append(sf)
    rpr.insert(0, ln)
    rpr.insert(1, rpr.makeelement(qn("a:noFill"), {}))
    text(s, 80, 416, 900, 32, en_label, size=22, color=WHITE, en=True, letter=6)
    text(s, 80, 460, 960, 64, title, size=46, color=WHITE, bold=True)
    if sub:
        text(s, 80, 544, 960, 36, sub, size=22, color=WHITE)
    return s


# =====================================================================
# データ（2022年10月〜2026年9月の48か月。単位：百万円・税抜）
# =====================================================================
from data_monthly import (YM, mi, AP_S, AP_MP, AP_AD, AP_NET, AF_S, AF_MP, AF_AD, AF_NET,
                          WEB_AP_AD, WEB_AF_AD, MALL_AP_AD, MALL_AP_S, MALL_AD_RATIO)

FY_NAMES = ["23年9月期", "24年9月期", "25年9月期", "26年9月期"]
assert all(len(v) == 48 for v in (AP_S, AP_MP, AP_NET, AP_AD, AF_S, AF_MP, AF_NET, AF_AD))


def fy_sum(series):
    return [sum(series[i * 12:(i + 1) * 12]) for i in range(4)]


# =====================================================================
# 1. 表紙
# =====================================================================
page_no += 1
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, 8, H_PX, LIGHT)
text(s, 96, 250, 960, 40, "株式会社ギフティ様　ご参考資料", size=26, color=SECONDARY)
text(s, 96, 330, 980, 100, "事業エコノミクスの整理とまとめ", size=60, bold=True, spacing=1.3)
text(s, 96, 450, 960, 40, "アンドプランツ/アンドフラワーの推移と、今後のエコノミクス", size=24,
     color=SECONDARY)
text(s, 96, 640, 900, 120, ["2026年10月", "株式会社DOMUZ", "髙木 弘貴"], size=22, color=SECONDARY, spacing=1.5)

# =====================================================================
# 2. 本資料の構成・要約・用語
# =====================================================================
s = content_slide("本資料の構成")
items = [
    ("1", "各事業のエコノミクスの整理と経年推移", "アンドプランツ/アンドフラワー（23年9月期〜26年9月期）"),
    ("2", "今後の事業におけるエコノミクスの整理", "原価・全体ROAS・直接固定費、LTV/CAC、損益分岐の月商"),
]
y = 260
for n, label, sub in items:
    # 番号とタイトルは同じ高さの箱に入れて上下中央でそろえる（説明はタイトルの下）
    text(s, 96, y + 16, 80, 64, n, size=60, color=LIGHT, bold=True, en=True, anchor=MSO_ANCHOR.MIDDLE,
         spacing=1.0)
    text(s, 190, y + 16, 870, 64, label, size=34, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, 190, y + 84, 870, 30, sub, size=20, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    if n != items[-1][0]:
        hline(s, 96, y + 128, 936)
    y += 160
footnote(s, "※ 用語と集計の前提は最終ページにまとめています")

summary_slide = content_slide("アンドプランツ")
summary_slide2 = content_slide("アンドフラワー")

# =====================================================================
# 章 01
# =====================================================================
divider("01", "ECONOMICS TREND", "各事業のエコノミクスの推移", "23年9月期（2022年10月）〜 26年9月期（2026年9月）")


def trend_slide(title, sales, mp, ad, net, color, ymax, note, msg, fy0=0, mp_label="限界利益",
                net_label="広告費込み限界利益", fy_names=None):
    """月次売上の棒（事業の色）＋期別の収益性の表。棒の上は各期の最高月、期名の下は期合計。"""
    s = content_slide(title)
    if msg:
        text(s, 56, 104, 1016, 36, msg, size=21, bold=True)
    fy_names = fy_names or FY_NAMES
    x0, x1 = 214, 914
    text(s, x0, 154, 900, 24, f"{FY_NAMES[fy0]}（{YM[fy0 * 12][0]}年10月）〜26年9月期（2026年9月）　単位：百万円　"
         "棒の上は各期の最高月、期名の下は期合計", size=14, color=SECONDARY)
    top, base = 206, 434
    n = 48 - fy0 * 12
    slot = (x1 - x0) / n
    bw = slot * 0.66
    vmax = max(sales)
    sy = lambda v: base - (base - top) * v / vmax
    for k in range(fy0, 4):
        idx = range(k * 12, k * 12 + 12)
        peak = max(idx, key=lambda i: sales[i])
        for i in idx:
            if sales[i] <= 0:
                continue
            bx = x0 + (i - fy0 * 12) * slot + (slot - bw) / 2
            rect(s, bx, sy(sales[i]), bw, base - sy(sales[i]), color)
            if i == peak:
                text(s, bx - 20, sy(sales[i]) - 26, bw + 40, 22, f"{sales[i]:.0f}" if vmax >= 20 else f"{sales[i]:.1f}", size=15, bold=True,
                     align=PP_ALIGN.CENTER, en=True)
        gx = x0 + (k - fy0) * 12 * slot
        if k > fy0:
            vline(s, gx, 190, base - 190 + 70, BORDER_LIGHT, 1.0, dash=True)
        text(s, gx, base + 12, 12 * slot, 26, fy_names[k], size=17, bold=True, align=PP_ALIGN.CENTER)
        text(s, gx, base + 40, 12 * slot, 24, f"{sum(sales[i] for i in idx):.0f}", size=16, color=SECONDARY,
             align=PP_ALIGN.CENTER, en=True)
    hline(s, x0 - 4, base, x1 - x0 + 8, BORDER_LIGHT, 1.5)
    # 期別の表
    hdr = ["期", "売上", mp_label, f"{mp_label}率", "広告費", "全体ROAS", net_label, "同率"]
    cxs = [56, 190, 290, 410, 520, 620, 740, 950]
    cws = [130, 100, 120, 110, 100, 120, 210, 122]
    ty = 512
    rect(s, 56, ty, 1016, 40, MOSS if color != FLOWER else FLOWER)
    for j, h in enumerate(hdr):
        text(s, cxs[j] + (12 if j == 0 else 0), ty, cws[j] - (0 if j == 0 else 12), 40, h, size=16, color=WHITE,
             bold=True, anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.LEFT if j == 0 else PP_ALIGN.RIGHT)
    y = ty + 40
    fs, fm, fa, fn = fy_sum(sales), fy_sum(mp), fy_sum(ad), fy_sum(net)
    rh = 48 if fy0 == 0 else 56
    for k in range(fy0, 4):
        if k == 3:
            rect(s, 56, y, 1016, rh, WATERMARK)
        roas = f"{fs[k] / fa[k] * 100:.0f}%" if fa[k] > 0 else "—"
        vals = [fy_names[k], f"{fs[k]:.1f}", f"{fm[k]:.1f}", f"{fm[k] / fs[k] * 100:.1f}%", f"{fa[k]:.1f}" if fa[k] > 0 else "—", roas,
                f"{fn[k]:.1f}", f"{fn[k] / fs[k] * 100:.1f}%"]
        for j, v in enumerate(vals):
            text(s, cxs[j] + (12 if j == 0 else 0), y, cws[j] - (0 if j == 0 else 12), rh, v, size=19, bold=True,
                 color=STRONG if v.startswith("-") else MOSS, anchor=MSO_ANCHOR.MIDDLE,
                 align=PP_ALIGN.LEFT if j == 0 else PP_ALIGN.RIGHT)
        y += rh
        hline(s, 56, y, 1016, BORDER_LIGHT)
    footnote(s, note)
    return s


ap_fy_s, ap_fy_net, ap_fy_ad = fy_sum(AP_S), fy_sum(AP_NET), fy_sum(AP_AD)
af_fy_s, af_fy_net, af_fy_ad = fy_sum(AF_S), fy_sum(AF_NET), fy_sum(AF_AD)

AP_GREEN = LIGHT
trend_slide(
    "アンドプランツ：月次売上と期別の収益性", AP_S, AP_MP, AP_AD, AP_NET, AP_GREEN, 70,
    f"※ 税抜・注文日ベース。売上・限界利益・広告費はいずれも自社EC＋モール（楽天・Amazon・Yahoo!）。"
    f"モール広告費は社内集計のある月（25年4〜6月・26年4〜9月）は実績、それ以外はモール限界利益の{MALL_AD_RATIO[1] * 100:.0f}%で推計",
    f"年間の売上は{ap_fy_s[3]:.0f}百万円。広告費を絞って広告費込み限界利益は年間{ap_fy_net[3]:.0f}百万円（前期比 +{(ap_fy_net[3] / ap_fy_net[2] - 1) * 100:.0f}%）に",
)
AF69 = {k_: (sum(v_[i] for i in range(32, 36)), sum(v_[i] for i in range(44, 48)))
        for k_, v_ in (("s", AF_S), ("ad", AF_AD), ("net", AF_NET))}  # 6〜9月の合計（25年, 26年）
trend_slide(
    "アンドフラワー：月次売上と期別の収益性", AF_S, AF_MP, AF_AD, AF_NET, FLOWER, 35,
    f"※ 税抜・注文日ベース。自社EC＋モール（花のモール売上は微小）。母の日の広告は花に計上、そのほかの共通広告は売上比で配賦。"
    f"6〜9月の合計（25年→26年）：広告費{AF69['ad'][0]:.1f}→{AF69['ad'][1]:.1f}、売上{AF69['s'][0]:.1f}→{AF69['s'][1]:.1f}百万円",
    f"26年6〜9月は広告費を前年の半分以下に絞り、広告費込み限界利益は{AF69['net'][0]:.1f}→{AF69['net'][1]:.1f}百万円に増加",
)

# =====================================================================
# 章 02
# =====================================================================
divider("02", "UNIT ECONOMICS", "今後の事業におけるエコノミクス", "原価・全体ROAS・直接固定費")

# ---- 現在のエコノミクス（繁忙期を含む四半期＝26年4〜6月、繁忙期の単月＝26年5月）
# AP/AF: 予実管理Master「貢献利益(四半期)」の費目別の値（円）。9月は速報値。
# 人件費 = 社員・アルバイト・CS按分・スポット・外部加工（三和園芸）、倉庫・光熱費 = 水道光熱費＋地代家賃・賃借料＋SBS賃借料。
# 車両費・修繕費・備品消耗品費・通信費は含めない（貢献利益はこの2つだけを引いた値）。
# 広告費 = 売上 × 限界利益率（BigQuery の同月） − 広告費込み限界利益（共通広告は売上比で配賦されたもの）
MONTHLY = {  # (売上, 広告費込み限界利益, 人件費, 倉庫・光熱費) 円
    ("af", "2025-04"): (21734977, 978842, 4984896, 1098982), ("af", "2025-05"): (23754556, 2086304, 7138855, 1140465),
    ("af", "2025-06"): (10871098, 59379, 4601611, 1234798), ("af", "2026-04"): (28093399, 8578532, 6362155, 1094708),
    ("af", "2026-05"): (30414263, 9422901, 8291874, 1133449), ("af", "2026-06"): (8409756, 2020824, 4941862, 1179500),
    ("af", "2026-07"): (7458530, 1865033, 5057033, 1135886), ("af", "2026-08"): (8886431, 2531001, 5070723, 1135886),
    ("af", "2026-09"): (11345345, 2567548, 5079569, 1135886),
    ("ap", "2025-04"): (62105259, 19183154, 4920629, 260984), ("ap", "2025-05"): (62440913, 17745077, 5033776, 3373667),
    ("ap", "2025-06"): (46857628, 11322154, 4399589, 3361754), ("ap", "2026-04"): (59030438, 20521614, 4599936, 3005339),
    ("ap", "2026-05"): (65895599, 21702271, 6140455, 2415372), ("ap", "2026-06"): (49027036, 14755323, 5653467, 2695599),
    ("ap", "2026-07"): (50032306, 14791661, 4974759, 2206555), ("ap", "2026-08"): (42078221, 12800591, 5035606, 1978470),
    ("ap", "2026-09"): (44436966, 12772467, 4839419, 2199960),
}


def econ(biz, months):
    """売上・人件費・倉庫光熱費は社内の貢献利益集計、原価率と広告費は月次推移と同じ受注データ（BigQuery）。
    貢献利益集計は母の日などの共通広告の AP/AF への配賦が BigQuery と違うため、広告費は BigQuery にそろえる。"""
    mp_series, s_series, ad_series = (AP_MP, AP_S, AP_AD) if biz == "ap" else (AF_MP, AF_S, AF_AD)
    e = dict(S=0.0, NET=0.0, LABOR=0.0, OTHER=0.0, COGS=0.0, AD=0.0)
    for ym in months:
        S, _net_sheet, L, W = (v / 1e6 for v in MONTHLY[(biz, ym)])
        i = mi(ym)
        mpr = mp_series[i] / s_series[i]
        ad = ad_series[i] * S / s_series[i]  # 売上の集計差ぶんだけ比例させる
        e["S"] += S
        e["LABOR"] += L
        e["OTHER"] += W
        e["COGS"] += S * (1 - mpr)
        e["AD"] += ad
        e["NET"] += S * mpr - ad
    e["CONTRIB"] = e["NET"] - e["LABOR"] - e["OTHER"]
    e["ROAS"] = e["S"] / e["AD"] * 100
    return e


def yen(v):
    return f"▲{-v:.1f}" if v <= -0.05 else f"{abs(v):.1f}"


def per_month(e, n):
    return {k: (v / n if k != "ROAS" else v) for k, v in e.items()}


Q3 = ["2026-04", "2026-05", "2026-06"]
PERIODS = {
    "q": dict(label="繁忙期を含む四半期（26年4〜6月）", short="4〜6月",
              ap=econ("ap", Q3), af=econ("af", Q3)),
    "may": dict(label="繁忙期（26年5月・母の日）", short="5月",
                ap=econ("ap", ["2026-05"]), af=econ("af", ["2026-05"])),
}
PREV_Q = {b_: econ(b_, ["2025-04", "2025-05", "2025-06"]) for b_ in ("ap", "af")}  # 前年同期
# 損益分岐・感応度は四半期の月平均で見る
ap, af = per_month(PERIODS["q"]["ap"], 3), per_month(PERIODS["q"]["af"], 3)


def waterfall(s, x, name, steps, end_label, end_val, sales, color, lo=-40, unit="", bar=None):
    """steps: [(ラベル, 金額)] を売上から順に引く。縦軸は 100 〜 lo（%）で3事業共通。"""
    text(s, x, 156, 330, 34, name, size=24, bold=True, color=color)
    end_name = end_label.replace("\n", "")
    text(s, x, 192, 340, 26, f"売上 {sales:.1f}／{end_name} {yen(end_val)}百万円{unit}", size=15, color=SECONDARY)
    top, bot = 262, 612
    yv = lambda v: top + (bot - top) * (100 - v) / (100 - lo)
    bw, gap = 46, 12
    bx = x
    rect(s, bx, yv(100), bw, yv(0) - yv(100), PALE)
    text(s, bx - 10, yv(100) - 24, bw + 20, 22, "100", size=14, bold=True, align=PP_ALIGN.CENTER, en=True)
    labels = [(bx, "売上", SECONDARY, False)]
    cur = 100.0
    for lab, v in steps:
        bx += bw + gap
        p = v / sales * 100
        y0, y1 = yv(cur), yv(cur - p)
        rect(s, bx, y0, bw, y1 - y0, BG_GRAY)
        text(s, bx - 12, y1 + 3, bw + 24, 20, f"{p:.1f}", size=12, color=SECONDARY, align=PP_ALIGN.CENTER, en=True)
        labels.append((bx, lab, SECONDARY, False))
        cur -= p
    bx += bw + gap
    endp = end_val / sales * 100
    col = (bar or color) if endp >= 0 else (MUTED if abs(endp) < 0.05 else STRONG)
    y0, y1 = sorted((yv(0), yv(endp)))
    rect(s, bx, y0, bw, max(y1 - y0, 2), col)
    ly = y0 - 24 if endp >= 0 else y1 + 3
    text(s, bx - 12, ly, bw + 24, 22, f"{(0.0 if abs(endp) < 0.05 else endp):.1f}", size=14, bold=True, color=col,
         align=PP_ALIGN.CENTER, en=True)
    labels.append((bx, end_label, MOSS, True))
    hline(s, x - 6, yv(0), bx + bw + 12 - x, MUTED)
    ly_ = yv(min(0.0, endp)) + 10 + (0 if endp >= 0 else 20)  # 0の線（赤字なら棒の下）のすぐ下に項目名
    for lx, lab, c, b in labels:
        text(s, lx - 10, ly_, bw + 20, 44, lab, size=12, color=c, bold=b, align=PP_ALIGN.CENTER, spacing=1.2)
    return s


def econ_slide(key, n, takeaway, note):
    P = PERIODS[key]
    s = content_slide(f"エコノミクス{n}：{P['label']}", "棒の数字は売上を100としたときの割合（%）。金額は各事業名の下　※税抜")
    a_, f_ = P["ap"], P["af"]
    unit = "（3か月計）" if key == "q" else ""
    waterfall(s, 150, "アンドプランツ",
              [("原価等", a_["COGS"]), ("広告費", a_["AD"]), ("人件費", a_["LABOR"]), ("倉庫・\n光熱費", a_["OTHER"])],
              "貢献\n利益", a_["CONTRIB"], a_["S"], MOSS, unit=unit, bar=LIGHT)
    waterfall(s, 640, "アンドフラワー",
              [("原価等", f_["COGS"]), ("広告費", f_["AD"]), ("人件費", f_["LABOR"]), ("倉庫・\n光熱費", f_["OTHER"])],
              "貢献\n利益", f_["CONTRIB"], f_["S"], FLOWER, unit=unit)
    vline(s, 564, 160, 500)
    text(s, 56, 678, 1016, 60, takeaway, size=20, bold=True, spacing=1.4)
    footnote(s, note)


NOTE_ECON = ("人件費＝社員・アルバイト・スポット・CS按分・外部加工。倉庫・光熱費＝倉庫の賃借料・家賃（APは外部倉庫SBS）＋水道光熱費。"
             "原価率と広告費は月次推移と同じ受注データ（BigQuery）の値で、全体ROAS＝売上÷広告費")
qa, qf = PERIODS["q"]["ap"], PERIODS["q"]["af"]
econ_slide("q", "①", [f"アンドプランツの貢献利益は3か月で{qa['CONTRIB']:.1f}百万円（売上比{qa['CONTRIB'] / qa['S'] * 100:.0f}%）。",
                      f"アンドフラワーは前年同期（25年4〜6月）の{yen(PREV_Q['af']['CONTRIB'])}百万円から、"
                      f"[[{'+' if qf['CONTRIB'] > 0 else ''}{yen(qf['CONTRIB'])}百万円に改善]]"],
           "※ 社内の貢献利益集計（26年4〜6月の3か月合計）。" + NOTE_ECON)
econ_slide("may", "②", [f"繁忙期はアンドプランツの貢献利益が月{PERIODS['may']['ap']['CONTRIB']:.1f}百万円。"
                        "アンドフラワーは売上が平常月の約3倍になり、",
                        "人件費（スポット含む）も増えるが、[[ほぼ損益分岐]]" if abs(PERIODS['may']['af']['CONTRIB']) < 0.5
                        else ("人件費（スポット含む）も増えるが、[[損益分岐を達成]]" if PERIODS['may']['af']['CONTRIB'] > 0
                              else f"人件費（スポット含む）も増え、貢献利益は[[{yen(PERIODS['may']['af']['CONTRIB'])}百万円]]")],
           "※ 社内の貢献利益集計（26年5月）。APの人件費は外部加工費1.1百万円を含む。" + NOTE_ECON)

# ---- 主要指標（表）：四半期と単月を並べる
s = content_slide("エコノミクスの主要指標", "繁忙期を含む四半期（26年4〜6月）と繁忙期の単月（26年5月）　※税抜")
cx2 = [56, 400, 560, 740, 900]
CW2 = 150
y = 160
for j, (name, col) in enumerate([("アンドプランツ", MOSS), ("アンドフラワー", FLOWER)]):
    text(s, cx2[1 + 2 * j], y, 310, 28, name, size=18, bold=True, color=col, align=PP_ALIGN.CENTER)
    hline(s, cx2[1 + 2 * j] + 12, y + 32, 286, col, 2.0)
    for q, lab in enumerate(["4〜6月", "5月"]):
        text(s, cx2[1 + 2 * j + q], y + 40, CW2, 24, lab, size=15, color=SECONDARY, align=PP_ALIGN.RIGHT)
hline(s, 56, y + 74, 1016, MOSS, 1.5)
y += 74
SEQ = [PERIODS["q"], PERIODS["may"]]


RH = 60  # 1行の高さ。項目名（＋補足）と数字はこの中で上下中央


def r2(label, fn, sub=None, bold=False):
    global y
    tb = text(s, cx2[0], y, 280, RH, label, size=18, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    if sub:
        p_ = tb.text_frame.add_paragraph()
        p_.line_spacing = 1.0
        p_.space_before = Emu(int(pt(4) * 12700))
        r_ = p_.add_run()
        r_.text = sub
        _set_font(r_, 12, SECONDARY, False)
    vals = []
    for b_ in ("ap", "af"):
        for P in SEQ:
            vals.append(fn(b_, P[b_]))
    for j, v in enumerate(vals):
        text(s, cx2[1 + j], y, CW2, RH, v, size=18, bold=bold, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE,
             spacing=1.0, color=STRONG if v.startswith("▲") else MOSS)
    y += RH
    hline(s, 56, y, 1016)


r2("売上（百万円）", lambda b, e: f"{e['S']:.1f}", "4〜6月は3か月の合計")
r2("原価率", lambda b, e: f"{e['COGS'] / e['S'] * 100:.0f}%", "原価・送料・資材・決済手数料を含む")
r2("全体ROAS", lambda b, e: f"{e['ROAS']:.0f}%", "売上÷広告費")
r2("広告費込み限界利益率", lambda b, e: f"{e['NET'] / e['S'] * 100:.1f}%", bold=True)
r2("直接固定費（百万円）", lambda b, e: f"{e['LABOR'] + e['OTHER']:.1f}",
   "人件費＋倉庫・光熱費")
r2("貢献利益（百万円）", lambda b, e: yen(e["CONTRIB"]), bold=True)
af_be = (af["NET"] - af["CONTRIB"]) / (af["NET"] / af["S"])
text(s, 56, y + 16, 1016, 70,
     [f"アンドフラワーの損益分岐は、4〜6月の利益率・固定費（月平均）で月商 約[[{af_be:.0f}百万円]]。",
      f"5月は月商{PERIODS['may']['af']['S']:.0f}百万円で、貢献利益は{yen(PERIODS['may']['af']['CONTRIB'])}百万円と"
      f"{'ほぼ損益分岐' if abs(PERIODS['may']['af']['CONTRIB']) < 0.5 else ('黒字' if PERIODS['may']['af']['CONTRIB'] > 0 else '赤字')}"], size=19, bold=True,
     spacing=1.45)
footnote(s, "※ 損益分岐＝直接固定費÷広告費込み限界利益率。固定費が売上に比例して増えない前提の概算")

# ---- 広告投資①：月次の広告費・売上・ROAS（アンドプランツ、24年10月〜26年9月）
s = content_slide("広告投資①：26年1月から意図して広告費を絞った",
                  "アンドプランツの月次の売上・広告費・ROAS（24年10月〜26年9月）　単位：百万円")
i0 = 24
n_ = 48 - i0
x0, x1 = 120, 1040
slot = (x1 - x0) / n_
cx = lambda i: x0 + (i - i0) * slot + slot / 2
top, base = 190, 470
sy = lambda v: base - (base - top) * v / 70
for v in range(0, 71, 10):
    hline(s, x0 - 4, sy(v), x1 - x0 + 4, BORDER_LIGHT if v == 0 else WATERMARK)
    text(s, 60, sy(v) - 11, 50, 22, str(v), size=12, color=MUTED, align=PP_ALIGN.RIGHT, en=True)
for i in range(i0, 48):
    bw_ = slot * 0.62
    rect(s, cx(i) - bw_ / 2, sy(AP_S[i]), bw_, base - sy(AP_S[i]), AP_GREEN)
polyline(s, [(cx(i), sy(AP_AD[i])) for i in range(i0, 48)], STRONG, 3.0)
for i in range(i0, 48):
    rect(s, cx(i) - 4, sy(AP_AD[i]) - 4, 8, 8, STRONG, shape=MSO_SHAPE.OVAL)
# ROAS（下段）
rt, rb = 520, 640
ry = lambda v: rb - (rb - rt) * v / 1400
text(s, 56, rt - 30, 300, 22, "ROAS（売上÷広告費）", size=13, color=SECONDARY, bold=True)
for v in (0, 500, 1000):
    hline(s, x0 - 4, ry(v), x1 - x0 + 4, BORDER_LIGHT if v == 0 else WATERMARK)
    text(s, 50, ry(v) - 10, 60, 20, f"{v}%", size=11, color=MUTED, align=PP_ALIGN.RIGHT, en=True)
roas_ = [AP_S[i] / AP_AD[i] * 100 for i in range(48)]
polyline(s, [(cx(i), ry(roas_[i])) for i in range(i0, 48)], MOSS, 2.5)
for i in range(i0, 48):
    text(s, cx(i) - 20, rb + 4, 40, 18, f"{YM[i][1]}", size=11, color=MUTED, align=PP_ALIGN.CENTER, en=True)
    if roas_[i] >= 900:
        text(s, cx(i) - 30, ry(roas_[i]) - 22, 60, 18, f"{roas_[i]:,.0f}%", size=11, bold=True,
             align=PP_ALIGN.CENTER, en=True)
for lab, i in (("25年9月期", 24), ("26年9月期", 36)):
    text(s, cx(i) - slot / 2, rb + 22, 12 * slot, 20, lab, size=13, color=SECONDARY, bold=True, align=PP_ALIGN.CENTER)
vline(s, cx(36) - slot / 2, top - 10, rb - top + 36, BORDER_LIGHT, 1.0, dash=True)
# 26年1月の線
xl = cx(39) - slot / 2
vline(s, xl, top - 24, rb - top + 24, STRONG, 2.0)
text(s, xl + 6, top - 30, 260, 22, "26年1月〜 広告費を絞る", size=14, bold=True, color=STRONG)
# 凡例
rect(s, 120, 150, 16, 16, AP_GREEN)
text(s, 142, 146, 80, 24, "売上", size=14, color=SECONDARY)
rect(s, 206, 156, 28, 4, STRONG)
text(s, 240, 146, 80, 24, "広告費", size=14, color=SECONDARY)
rect(s, 310, 156, 28, 4, MOSS)
text(s, 344, 146, 80, 24, "ROAS", size=14, color=SECONDARY)
jm_ad = (sum(AP_AD[39:42]), sum(AP_AD[27:30]))
jm_s = (sum(AP_S[39:42]), sum(AP_S[27:30]))
text(s, 56, 692, 1016, 60,
     [f"26年1〜3月は、広告費を前年同期の{jm_ad[1]:.1f}→{jm_ad[0]:.1f}百万円（{(jm_ad[0] / jm_ad[1] - 1) * 100:.0f}%）に絞っても、"
      f"売上は{jm_s[1]:.0f}→{jm_s[0]:.0f}百万円（{(jm_s[0] / jm_s[1] - 1) * 100:.0f}%）。",
      "ファイナンス環境の変化を受け、トップラインより健全性を優先した[[経営判断]]であり、広告効率の悪化ではない"],
     size=18, bold=True, spacing=1.45)
footnote(s, "※ 売上・広告費とも自社EC＋モール（楽天・Amazon・Yahoo!）。モール広告費は社内集計のない月は推計（推移ページの注記を参照）")

# ---- 広告投資②：アンドフラワーの月次の広告費・売上・ROAS（24年10月〜26年9月）
s = content_slide("広告投資②：アンドフラワーも広告費を絞った",
                  "アンドフラワーの月次の売上・広告費・ROAS（24年10月〜26年9月）　単位：百万円")
i0 = 24
n_ = 48 - i0
x0, x1 = 120, 1040
slot = (x1 - x0) / n_
cx = lambda i: x0 + (i - i0) * slot + slot / 2
top, base = 190, 412
sy = lambda v: base - (base - top) * v / 35
for v in range(0, 36, 5):
    hline(s, x0 - 4, sy(v), x1 - x0 + 4, BORDER_LIGHT if v == 0 else WATERMARK)
    text(s, 60, sy(v) - 11, 50, 22, str(v), size=12, color=MUTED, align=PP_ALIGN.RIGHT, en=True)
for i in range(i0, 48):
    bw_ = slot * 0.62
    rect(s, cx(i) - bw_ / 2, sy(AF_S[i]), bw_, base - sy(AF_S[i]), FLOWER)
polyline(s, [(cx(i), sy(AF_AD[i])) for i in range(i0, 48)], MOSS, 3.0)
for i in range(i0, 48):
    rect(s, cx(i) - 4, sy(AF_AD[i]) - 4, 8, 8, MOSS, shape=MSO_SHAPE.OVAL)
rt, rb = 456, 548
ry = lambda v: rb - (rb - rt) * v / 800
text(s, 56, rt - 28, 300, 22, "ROAS（売上÷広告費）", size=13, color=SECONDARY, bold=True)
for v in (0, 400, 800):
    hline(s, x0 - 4, ry(v), x1 - x0 + 4, BORDER_LIGHT if v == 0 else WATERMARK)
    text(s, 50, ry(v) - 10, 60, 20, f"{v}%", size=11, color=MUTED, align=PP_ALIGN.RIGHT, en=True)
af_roas = [AF_S[i] / AF_AD[i] * 100 for i in range(48)]
polyline(s, [(cx(i), ry(af_roas[i])) for i in range(i0, 48)], STRONG, 2.5)
for i in range(i0, 48):
    text(s, cx(i) - 20, rb + 4, 40, 18, f"{YM[i][1]}", size=11, color=MUTED, align=PP_ALIGN.CENTER, en=True)
for lab, i in (("25年9月期", 24), ("26年9月期", 36)):
    text(s, cx(i) - slot / 2, rb + 22, 12 * slot, 20, lab, size=13, color=SECONDARY, bold=True, align=PP_ALIGN.CENTER)
vline(s, cx(36) - slot / 2, top - 10, rb - top + 36, BORDER_LIGHT, 1.0, dash=True)
xl = cx(44) - slot / 2
vline(s, xl, top - 24, rb - top + 24, STRONG, 2.0)
text(s, xl - 266, top - 30, 260, 22, "26年6月〜 広告費をさらに絞る", size=14, bold=True, color=STRONG, align=PP_ALIGN.RIGHT)
rect(s, 120, 150, 16, 16, FLOWER)
text(s, 142, 146, 80, 24, "売上", size=14, color=SECONDARY)
rect(s, 206, 156, 28, 4, MOSS)
text(s, 240, 146, 80, 24, "広告費", size=14, color=SECONDARY)
rect(s, 310, 156, 28, 4, STRONG)
text(s, 344, 146, 80, 24, "ROAS", size=14, color=SECONDARY)
# 前年比較（年間と6〜9月）
cmp_rows = [
    ("広告費", (af_fy_ad[2], af_fy_ad[3]), AF69["ad"]),
    ("売上", (af_fy_s[2], af_fy_s[3]), AF69["s"]),
    ("広告費込み限界利益", (af_fy_net[2], af_fy_net[3]), AF69["net"]),
]
y = 608
hline(s, 56, y - 8, 1016)
for j, h in enumerate(["年間（25年9月期→26年9月期）", "6〜9月（25年→26年）"]):
    text(s, 330 + j * 370, y, 360, 24, h, size=13, bold=True, color=SECONDARY)
y += 26
for lab, (a1, a2), (b1, b2) in cmp_rows:
    text(s, 56, y, 260, 26, lab, size=15, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    for j, (u, v) in enumerate(((a1, a2), (b1, b2))):
        ch = (v / u - 1) * 100
        tag = f"（約{v / u:.1f}倍）" if v / u >= 2 else f"（{ch:+.0f}%）"
        text(s, 330 + j * 370, y, 360, 26, f"{u:.1f} → {v:.1f}百万円{tag}", size=16, bold=(lab != "売上"),
             color=MOSS, anchor=MSO_ANCHOR.MIDDLE)
    y += 28
footnote(s, "※ 自社EC＋モール（花のモール売上は微小）。母の日の4〜5月は需要が大きく、広告費を絞ってもROASが高く出る")

# ---- LTV/CAC：自社EC（Shopify）の受注を顧客単位で集計（BigQuery and-plants.datawarehouse.sales_profit_by_items）
# LTV = 初回購入から12か月の限界利益（広告費控除前）の1人あたり平均。初回購入が25年9月期の顧客（12か月を追える最新の年度）。
# CAC = その年度のWeb広告費（モール広告費を除く）÷ 新規顧客数（広告費はすべて新規獲得にかかったとみなす）
LTV = {  # 25年9月期に初回購入した顧客の12か月
    "AP": dict(new25=28625, aov=11156, orders=1.39, sales12=14802, mp12=7186, rep12=22.0, rep3=14.3),
    "AF": dict(new25=17438, aov=7479, orders=1.24, sales12=8955, mp12=4182, rep12=14.1, rep3=7.7),
}
NEW26 = {"AP": 24472, "AF": 16864}
AOV26 = {"AP": 11444, "AF": 7398}  # 26年9月期に初回購入した顧客の初回の購入単価
MP_FIRST26 = {"AP": 5615, "AF": 3653}  # 同じ顧客の初回購入の限界利益（広告費控除前）
REPEAT_SHARE = {"AP": (29.5, 34.7), "AF": (19.2, 27.3)}  # リピート顧客の売上比率（25年9月期, 26年9月期）
AD26 = {"AP": fy_sum(WEB_AP_AD)[3], "AF": fy_sum(WEB_AF_AD)[3]}  # 自社ECの新規獲得なので、モール広告費は除く
AD25 = {"AP": fy_sum(WEB_AP_AD)[2], "AF": fy_sum(WEB_AF_AD)[2]}

s = content_slide("LTV/CAC：観葉植物と花", "自社ECの新規顧客1人あたり　※税抜")
for k, (b_, name, col) in enumerate([("AP", "アンドプランツ（観葉植物）", MOSS), ("AF", "アンドフラワー（花）", FLOWER)]):
    x = 56 + k * 528
    w = 488
    L = LTV[b_]
    cac26 = AD26[b_] * 1e6 / NEW26[b_]
    cac25 = AD25[b_] * 1e6 / L["new25"]
    ratio = L["mp12"] / cac26
    rect(s, x, 150, w, 6, AP_GREEN if b_ == "AP" else FLOWER)
    text(s, x, 172, w, 34, name, size=23, bold=True, color=col)
    ratio_s = L["sales12"] / cac26
    # 左：限界利益ベース（主）、右：売上ベース（参考）を横に並べる
    text(s, x, 214, 230, 22, "LTV/CAC（限界利益ベース）", size=13, color=SECONDARY, bold=True)
    tb = text(s, x, 236, 230, 66, f"{ratio:.1f}", size=56, bold=True, color=col, en=True, spacing=1.0,
              anchor=MSO_ANCHOR.BOTTOM)
    r = tb.text_frame.paragraphs[0].add_run()
    r.text = "倍"
    _set_font(r, 22, col, True, en=False)
    text(s, x + 236, 214, w - 236, 22, "売上ベース", size=13, color=SECONDARY, bold=True)
    # 文字の下の余白（ディセント）は字の大きさに比例するので、箱を少し短くしてベースラインを 2.0 倍とそろえる
    tb = text(s, x + 236, 236, w - 236, 66 - 6, f"{ratio_s:.1f}", size=30, bold=True, color=SECONDARY, en=True,
              spacing=1.0, anchor=MSO_ANCHOR.BOTTOM)
    r = tb.text_frame.paragraphs[0].add_run()
    r.text = "倍"
    _set_font(r, 14, SECONDARY, True, en=False)
    text(s, x, 300, w, 22, f"LTV {L['mp12']:,}円 ÷ CAC {cac26:,.0f}円　／　売上ベースは12か月の売上{L['sales12']:,}円 ÷ CAC",
         size=12, color=SECONDARY)
    rows_ = [
        ("CAC（Web広告費÷新規）", f"{cac25:,.0f}円", f"{cac26:,.0f}円"),
        ("初回の購入単価", f"{L['aov']:,}円", f"{AOV26[b_]:,}円"),
        ("12か月の購入回数", f"{L['orders']:.2f}回", "—"),
        ("12か月の売上（LTV・売上）", f"{L['sales12']:,}円", "—"),
        ("12か月の限界利益（LTV）", f"{L['mp12']:,}円", "—"),
        ("リピート率（3か月以内）", f"{L['rep3']:.1f}%", "—"),
        ("リピート率（12か月以内）", f"{L['rep12']:.1f}%", "—"),
        ("売上に占めるリピート顧客", f"{REPEAT_SHARE[b_][0]:.1f}%", f"{REPEAT_SHARE[b_][1]:.1f}%"),
    ]
    yy = 334
    text(s, x + w - 250, yy, 120, 24, "25年9月期", size=14, color=SECONDARY, bold=True, align=PP_ALIGN.RIGHT)
    text(s, x + w - 120, yy, 120, 24, "26年9月期", size=14, color=SECONDARY, bold=True, align=PP_ALIGN.RIGHT)
    hline(s, x, yy + 30, w, MOSS, 1.5)
    yy += 38
    for lab, v1, v2 in rows_:
        bold_ = lab.startswith("12か月の限界利益") or lab.startswith("CAC")
        text(s, x, yy, w - 250, 30, lab, size=15, bold=bold_)
        text(s, x + w - 250, yy, 120, 30, v1, size=16, bold=bold_, align=PP_ALIGN.RIGHT,
             color=MUTED if v1 == "—" else MOSS)
        text(s, x + w - 120, yy, 120, 30, v2, size=16, bold=bold_, align=PP_ALIGN.RIGHT,
             color=MUTED if v2 == "—" else MOSS)
        yy += 37
        hline(s, x, yy - 8, w)
vline(s, 564, 150, 550)
cac_ap = AD26["AP"] * 1e6 / NEW26["AP"]
cac_af = AD26["AF"] * 1e6 / NEW26["AF"]
text(s, 56, 694, 1016, 60,
     [f"アンドプランツは初回購入の限界利益（{MP_FIRST26['AP']:,}円）でCAC（{cac_ap:,.0f}円）を[[初回で回収済み]]。",
      f"アンドフラワーも初回の限界利益{MP_FIRST26['AF']:,}円 ＞ CAC{cac_af:,.0f}円"],
     size=16, bold=True, spacing=1.45)
footnote(s, "※ 自社EC（Shopify）を顧客単位で集計。LTVは25年9月期に初回購入した顧客の初回から12か月の平均。CACは広告費をすべて"
            "新規獲得にかかったとみなした値（自社ECのWeb広告費で、モール広告費は除く）。LTV/CACは26年9月期のCACで計算")

# ---- 月次でいくら売り上げればよいか
s = content_slide("損益分岐に必要な月商", "貢献利益が0になる月商と、26年9月期の月平均の売上　単位：百万円/月")
need = {}
for b_, e in (("AP", ap), ("AF", af)):
    fixed_m = e["LABOR"] + e["OTHER"]
    need[b_] = (fixed_m, e["NET"] / e["S"], fixed_m / (e["NET"] / e["S"]))
act = {"AP": ap_fy_s[3] / 12, "AF": af_fy_s[3] / 12}
peak = {"AP": max(AP_S[36:48]), "AF": max(AF_S[36:48])}
bx0, bwid = 300, 620
vmax_ = 70
for k, (b_, name, col) in enumerate([("AP", "アンドプランツ", AP_GREEN), ("AF", "アンドフラワー", FLOWER)]):
    y0 = 168 + k * 214
    fixed_m, m_, be = need[b_]
    text(s, 56, y0, 300, 36, name, size=24, bold=True, color=MOSS if b_ == "AP" else FLOWER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 330, y0, 742, 36, f"直接固定費 {fixed_m:.1f}百万円/月　広告費込み限界利益率 {m_ * 100:.1f}%", size=15,
         color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE)
    for j, (lab, v, c_) in enumerate([("損益分岐の月商", be, MOSS if b_ == "AP" else FLOWER),
                                      ("26年9月期の月平均", act[b_], col if b_ == "AP" else FLOWER_LIGHT),
                                      ("26年9月期の最高月", peak[b_], BG_GRAY)]):
        yy = y0 + 48 + j * 44
        text(s, 56, yy, 230, 36, lab, size=16, color=SECONDARY, bold=(j == 0), anchor=MSO_ANCHOR.MIDDLE)
        rect(s, bx0, yy + 10, bwid * v / vmax_, 24, c_)
        text(s, bx0 + bwid * v / vmax_ + 10, yy, 120, 36, f"{v:.1f}", size=17, bold=True, en=True,
             anchor=MSO_ANCHOR.MIDDLE)
    hline(s, 56, y0 + 192, 1016)
ap_new_need = None
af_fixed, af_m, af_need = need["AF"]
rs = REPEAT_SHARE["AF"][1] / 100
new_need = af_need * 1e6 * (1 - rs) / LTV["AF"]["aov"]
text(s, 56, 618, 1016, 120,
     [f"アンドプランツは月平均{act['AP']:.0f}百万円で、損益分岐（{need['AP'][2]:.0f}百万円）を[[大きく上回っている]]。",
      f"アンドフラワーの損益分岐は月商 約{af_need:.0f}百万円で、母の日の4〜5月に届く水準。",
      f"平常月に届かせるには、リピート売上比率{rs * 100:.0f}%のままなら新規顧客 月約{new_need:,.0f}人が必要"
      f"（26年9月期は月平均{NEW26['AF'] / 12:,.0f}人）"],
     size=18, bold=True, spacing=1.5)
footnote(s, "※ 損益分岐＝直接固定費（人件費＋倉庫・光熱費、26年4〜6月の月平均）÷ 広告費込み限界利益率（同期間）。"
            "必要な新規顧客数＝損益分岐の月商×（1−リピート売上比率）÷初回の購入単価。売上はモールを含む")

AF_MPR26 = fy_sum(AF_MP)[3] / af_fy_s[3]

# ---- 要約（本資料の主張。数字が出そろってから、前に作っておいたページに描く）
def draw_claims(s, claims, y=140, color=LIGHT):
    for n, head, lines_ in claims:
        text(s, 56, y, 60, 50, n, size=42, color=color, bold=True, en=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        text(s, 120, y, 952, 50, head, size=24, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.2)
        y += 62
        for ln_ in lines_:
            rect(s, 124, y + 16, 8, 8, color)  # 行間の余白は文字の上に付くので、1行目の文字の中心に合わせて下げる
            text(s, 142, y, 930, 70, ln_, size=19, spacing=1.45)
            vis = sum(1.0 if ord(ch) > 0x7F else 0.55 for ch in ln_)  # 全角1・半角0.55で幅を見積もる
            y += 64 if vis > 47 else 38
        y += 30
    return y


apq = PERIODS["q"]["ap"]
draw_claims(summary_slide, [
    ("1", "トップラインの成長率鈍化は意図した結果であり、収益性は改善", [
        f"26年1月以降、広告費を意図的に削減（年間{ap_fy_ad[2]:.0f}→{ap_fy_ad[3]:.0f}百万円。月次ではより大きく絞った）",
        f"それでも売上は前期並み（{ap_fy_s[2]:.0f}→{ap_fy_s[3]:.0f}百万円）を維持し、ROASは"
        f"{ap_fy_s[2] / ap_fy_ad[2] * 100:.0f}→{ap_fy_s[3] / ap_fy_ad[3] * 100:.0f}%に改善",
        f"広告費込み限界利益は{ap_fy_net[2]:.1f}→{ap_fy_net[3]:.1f}百万円（+{(ap_fy_net[3] / ap_fy_net[2] - 1) * 100:.0f}%）、"
        f"同率{ap_fy_net[2] / ap_fy_s[2] * 100:.1f}→{ap_fy_net[3] / ap_fy_s[3] * 100:.1f}%",
        "ファイナンス環境の変化を受け、トップラインより健全性を優先した経営判断であり、広告効率の悪化ではない"]),
    ("2", "アンドプランツは、採算が合った状態で広告を踏める", [
        f"CAC {cac_ap:,.0f}円に対し、12か月LTV（限界利益ベース）は{LTV['AP']['mp12']:,}円で、"
        f"LTV/CAC {LTV['AP']['mp12'] / cac_ap:.1f}倍。12か月以内に回収が完結している",
        f"12か月リピート率{LTV['AP']['rep12']:.0f}%。売上に占めるリピート顧客は{REPEAT_SHARE['AP'][1]:.1f}%",
        f"月商{need['AP'][2]:.1f}百万円で損益分岐（貢献利益ベース）。26年9月期は月平均{act['AP']:.1f}百万円で大きく上回る",
        "貢献利益の黒字を保ったまま、売上を積める余地がある"]),
])
footnote(summary_slide, "※ 数値は税抜。用語の定義と集計の前提は最終ページ")
y_ = draw_claims(summary_slide2, [
    ("3", "アンドフラワーは損益分岐を超える売上規模の確保が収益化の鍵", [
        f"限界利益率{AF_MPR26 * 100:.1f}%、LTV/CAC {LTV['AF']['mp12'] / cac_af:.1f}倍と、1人あたりの採算は成立",
        f"損益分岐は月商{need['AF'][2]:.0f}百万円（貢献利益ベース）。26年9月期の平均は{act['AF']:.1f}百万円（母の日の月は{peak['AF']:.0f}百万円超）",
        "今後、複数の売上・トップライン向上施策により、この分岐を超える販売数を担保する"]),
], color=FLOWER)
footnote(summary_slide2, "※ 数値は税抜。用語の定義と集計の前提は最終ページ")

# ---- 用語と集計の前提（最終ページ）
terms = content_slide("用語と集計の前提")
TERMS = [
    ("期", "9月決算。「26年9月期」＝2025年10月〜2026年9月"),
    ("売上", "税抜・注文日ベース。自社EC＋モール（楽天・Amazon・Yahoo!）"),
    ("限界利益", "売上 − 原価・送料・資材・決済手数料"),
    ("広告費", "Web広告（Google・Meta・Yahoo!など）＋モール広告（Amazon・楽天）。母の日の広告は花に計上し、そのほかの共通広告（指名検索など）は自社ECの売上比で配賦。モール広告費は社内集計のない月は推計"),
    ("広告費込み限界利益", "限界利益 − 広告費"),
    ("全体ROAS", "売上 ÷ 広告費（モールを含む）。LTV/CACのCACは自社ECのWeb広告費で計算"),
    ("直接固定費", "事業に直接かかる人件費（社員・アルバイト・スポット・CS按分・外部加工）と、倉庫・光熱費（倉庫の賃借料・家賃、水道光熱費）"),
    ("貢献利益", "広告費込み限界利益 − 直接固定費。車両・修繕・消耗品・通信費、本社の人件費・共通費は含まない"),
    ("出典", "受注データ（BigQuery）と社内の貢献利益集計（速報値を含む）。試算表とは集計基準が異なる"),
]
y = 150
hline(terms, 56, y, 1016)
for k_, v_ in TERMS:
    # 説明が3行になる行（広告費）だけ高くし、項目名と説明を上下中央に置く
    rh_ = 96 if k_ == "広告費" else 68
    text(terms, 56, y, 236, rh_, k_, size=19, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(terms, 300, y, 772, rh_, v_, size=17, color=SECONDARY, spacing=1.35, anchor=MSO_ANCHOR.MIDDLE)
    y += rh_
    hline(terms, 56, y, 1016)

prs.save("giftee_economics_2026-10.pptx")  # PDF は soffice で書き出す
print("saved", len(prs.slides._sldIdLst), "slides")
for name, fs, fa, fn in [("AP", ap_fy_s, ap_fy_ad, ap_fy_net), ("AF", af_fy_s, af_fy_ad, af_fy_net)]:
    print(name, [round(v, 1) for v in fs], [round(v, 1) for v in fa], [round(v, 1) for v in fn])
print({p_: {b_: {kk: round(vv, 2) for kk, vv in PERIODS[p_][b_].items()} for b_ in ("ap", "af")} for p_ in PERIODS})
