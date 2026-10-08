"""1day合宿 2026.10.09 全社パート（髙木）— Domuz デザインシステム v2.1「発表スライド」型で .pptx を生成する。

Google スライドへは Drive の pptx 変換で取り込む。
サイズは 4:3・1128×846px 基準。px 指定は EMU に換算する（Google Slides 24pt ≒ 38px）。
"""
import os
import re
import sys

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
SECONDARY = RGBColor(0x62, 0x62, 0x62)   # --text-secondary
STRONG = RGBColor(0xE1, 0x64, 0x64)      # --text-strong
MUTED = RGBColor(0x99, 0x99, 0x99)       # --text-muted
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BG_GRAY = RGBColor(0xCB, 0xD0, 0xD3)     # --bg-gray（前年）
BORDER_LIGHT = RGBColor(0xC9, 0xCF, 0xCF)

FONT_EN = "Outfit"
FONT_JA = "Zen Kaku Gothic New"

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
    text = run.text
    is_en = en if en is not None else bool(re.fullmatch(r"[\x00-\x7F¥×→▲％%]*", text))
    face = FONT_EN if is_en else FONT_JA
    f = run.font
    f.size = Emu(int(pt(size_px) * 12700))
    f.bold = bold
    f.color.rgb = color
    f.name = face
    rpr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        el = rpr.find(qn(tag))
        if el is None:
            el = rpr.makeelement(qn(tag), {})
            rpr.append(el)
        el.set("typeface", face)


def set_face(run, face):
    run.font.name = face
    rpr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        rpr.find(qn(tag)).set("typeface", face)


def text(slide, x, y, w, h, lines, size=25, color=MOSS, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, spacing=1.5, en=None, letter=None, para_gap=0):
    """lines: 文字列 or 文字列のリスト。[[語]] はライトグリーン、**語** は太字。"""
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
        for part in re.split(r"(\[\[.*?\]\]|\*\*.*?\*\*)", line):
            if not part:
                continue
            c, b = color, bold
            if part.startswith("[["):
                part, c, b = part[2:-2], LIGHT, True
            elif part.startswith("**"):
                part, b = part[2:-2], True
            r = p.add_run()
            r.text = part
            _set_font(r, size, c, b, en)
            if letter:
                r.font._rPr.set("spc", str(int(letter * 100)))
    return tb


def _drop_style(shape):
    """テーマ由来の影（effectRef）を出さないよう、図形の p:style を外す。塗り・線は個別に指定済み。"""
    st = shape._element.find(qn("p:style"))
    if st is not None:
        shape._element.remove(st)


def rect(slide, x, y, w, h, fill, line=None, dash=False, shape=MSO_SHAPE.RECTANGLE):
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
        s.line.width = Emu(int(1.5 * 12700))
        if dash:
            s.line.dash_style = 4  # dash
    s.shadow.inherit = False
    _drop_style(s)
    return s


def arrow(slide, x, y, w, h):
    """右向きの三角（文字の▶は絵文字で描画されることがあるため図形で描く）。"""
    return rect(slide, x, y, w, h, LIGHT, shape=MSO_SHAPE.ISOSCELES_TRIANGLE).__setattr__("rotation", 90.0)


def hline(slide, x, y, w, color=BORDER_LIGHT, weight=1.0):
    ln = slide.shapes.add_connector(1, px(x), px(y), px(x + w), px(y))
    ln.line.color.rgb = color
    ln.line.width = Emu(int(weight * 12700))
    _drop_style(ln)
    return ln


TALK = []  # スピーカーノートは talk_script.md に書き出す（pptx を軽くして Drive に載せるため）


def notes(slide, body):
    TALK.append((len(prs.slides), body.strip()))


def content_slide(title=None, sub=None):
    """白背景＋左端ライトグリーン縦帯8px＋左上タイトル＋右下ページ番号。"""
    global page_no
    page_no += 1
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, 8, H_PX, LIGHT)
    if title:
        text(s, 56, 44, 1000, 56, title, size=38, bold=True)
    if sub:
        text(s, 56, 104, 1000, 36, sub, size=22, color=SECONDARY)
    text(s, W_PX - 120, H_PX - 44, 80, 24, str(page_no), size=14, color=MUTED,
         align=PP_ALIGN.RIGHT, en=True)
    return s


def dark_slide():
    global page_no
    page_no += 1
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = MOSS
    return s


def divider(num, en_label, title, sub):
    """P-3 章扉: Moss 全面＋アウトライン章番号＋英字 ALL CAPS＋和文タイトル。ページ番号は出さない。"""
    s = dark_slide()
    tb = text(s, 80, 240, 400, 150, num, size=120, color=WHITE, en=True, spacing=1.0)
    r = tb.text_frame.paragraphs[0].runs[0]
    rpr = r.font._rPr
    # 塗りなし＋白アウトライン
    for el in rpr.findall(qn("a:solidFill")):
        rpr.remove(el)
    ln = rpr.makeelement(qn("a:ln"), {"w": "19050"})
    sf = ln.makeelement(qn("a:solidFill"), {})
    clr = sf.makeelement(qn("a:srgbClr"), {"val": "FFFFFF"})
    sf.append(clr)
    ln.append(sf)
    rpr.insert(0, ln)
    nf = rpr.makeelement(qn("a:noFill"), {})
    rpr.insert(1, nf)
    text(s, 80, 416, 800, 32, en_label, size=22, color=WHITE, en=True, letter=6)
    text(s, 80, 460, 900, 64, title, size=46, color=WHITE, bold=True)
    text(s, 80, 544, 900, 36, sub, size=22, color=WHITE)
    return s


# =====================================================================
# 1. 表紙（P-1）
# =====================================================================
page_no += 1
s = prs.slides.add_slide(BLANK)
# 背景の透かし: 極太の "Domuz" を3段、薄いグレーで全面に
WATERMARK = RGBColor(0xEC, 0xEE, 0xEE)  # --watermark
BLACK = RGBColor(0x00, 0x00, 0x00)  # 表紙タイトルのみ黒（依頼者指定）
for row in range(3):
    tb = text(s, -20, -40 + row * 282, W_PX + 40, 300, "Domuz", size=330, color=WATERMARK, bold=True,
              en=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=0.8)
    for r in tb.text_frame.paragraphs[0].runs:
        set_face(r, "Google Sans")
tb = text(s, 0, 236, W_PX, 200, "Domuz", size=170, color=BLACK, bold=True, en=True, align=PP_ALIGN.CENTER,
          anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
set_face(tb.text_frame.paragraphs[0].runs[0], "Google Sans")
tb = text(s, 0, 430, W_PX, 160, "1day", size=120, color=BLACK, bold=True, en=True, align=PP_ALIGN.CENTER,
          anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
set_face(tb.text_frame.paragraphs[0].runs[0], "Google Sans")
r = tb.text_frame.paragraphs[0].add_run()
r.text = "合宿"
_set_font(r, 120, BLACK, True, en=False)
tb = text(s, 0, 640, W_PX, 40, "2026.10.09", size=28, color=SECONDARY, en=True, align=PP_ALIGN.CENTER,
          letter=4)
set_face(tb.text_frame.paragraphs[0].runs[0], "Google Sans")
notes(s, """
おはようございます。今日は一日よろしくお願いします。
（会場の雰囲気づくり：横浜まで来てくれてありがとう、など一言）
""")

# =====================================================================
# 2. 合宿の目的（3つを一覧）— P-11 番号付きリスト
# =====================================================================
items = [("1", "目線を上げる"), ("2", "チーム感を高める"), ("3", "今後の方針のシェア")]


def purpose_list():
    s = content_slide("今日の合宿の目的")
    y = 236
    for n, label in items:
        text(s, 96, y, 80, 80, n, size=64, color=LIGHT, bold=True, en=True)
        text(s, 200, y + 12, 800, 64, label, size=46, bold=True)
        if n != "3":
            hline(s, 96, y + 116, 936)
        y += 148
    return s


s = purpose_list()
notes(s, """
今日の目的は3つです。
1つずつ、なぜこれをやりたいのかを話します。
""")

# =====================================================================
# 3〜5. 目的を1つずつ（P-2 主張文）
# =====================================================================
purpose_notes = {
    "1": "目線を上げる：（口頭）普段の業務から一歩引いて、会社として何を目指しているかを見る日にしたい。",
    "2": "チーム感を高める：（口頭）普段話さない人とも話して、「この人こんなこと考えてたんだ」を持ち帰ってほしい。",
    "3": "今後の方針のシェア：（口頭）27年9月期にどこへ向かうのか、なぜそれをやるのかを全員で揃えたい。",
}
for n, label in items:
    s = content_slide()
    text(s, 56, 323, 1016, 200, label, size=64, bold=True, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE)
    notes(s, purpose_notes[n])

# 目的3つをもう一度（まとめ）
s = purpose_list()
notes(s, "改めて、今日の目的はこの3つです。")

# =====================================================================
# 6. 第8期 お疲れ様でした（キーメッセージ・Moss 全面）
# =====================================================================
s = content_slide()
text(s, 56, 300, 1016, 200, "26年9月期、大変お疲れ様でした！", size=64, bold=True,
     align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
notes(s, """
まずは26年9月期、本当にお疲れ様でした。
（ここは自由に：大変だったこと、ありがとうを伝えたい場面など）
""")

# =====================================================================
# 7. 章扉 01
# =====================================================================
s = divider("01", "FY2026 REVIEW", "26年9月期の振り返り", "")

# =====================================================================
# 8. 全社の数字（P-6 単系列＋強調：左に主要数字、右に月次売上）
# =====================================================================
s = content_slide("全社の数字", "26年9月期（2025年10月〜2026年9月）　※税抜")
kpis = [
    ("売上高", "8.34", "億円", MOSS),
    ("売上総利益", "5.02", "億円", MOSS),
]
y = 196
for lab, val, unit, col in kpis:
    text(s, 56, y, 340, 30, lab, size=22, color=SECONDARY)
    tb = text(s, 56, y + 32, 340, 84, val, size=72, color=col, bold=True, en=True, spacing=1.0)
    r = tb.text_frame.paragraphs[0].add_run()
    r.text = unit
    _set_font(r, 25, col, True, en=False)
    y += 170
text(s, 56, y, 340, 30, "粗利率 60%", size=22, color=SECONDARY)
# 月次売上（百万円）。最高の5月だけライトグリーン
months = ["10", "11", "12", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
sales = [59.2, 59.8, 59.8, 79.3, 54.8, 67.5, 98.4, 111.5, 62.0, 61.6, 58.7, 65.7]
cx0, cw, cg = 432, 40, 14
base_y, max_h = 600, 330
text(s, cx0, 168, 400, 24, "月次売上　単位：百万円", size=16, color=SECONDARY)
for i, (m, v) in enumerate(zip(months, sales)):
    x = cx0 + i * (cw + cg)
    h = max_h * v / max(sales)
    col = LIGHT if v == max(sales) else MOSS
    rect(s, x, base_y - h, cw, h, col)
    text(s, x - 10, base_y - h - 28, cw + 20, 24, f"{v:.0f}", size=15, bold=True,
         align=PP_ALIGN.CENTER, en=True)
    text(s, x - 10, base_y + 8, cw + 20, 24, f"{m}月", size=15, color=SECONDARY,
         align=PP_ALIGN.CENTER)
hline(s, cx0 - 8, base_y, 12 * (cw + cg))
text(s, 56, 680, 1016, 44, "5月に、創業以来はじめて[[月商1億円]]を超えた。", size=28,
     bold=True)
text(s, 56, H_PX - 76, 960, 24,
     "※ 試算表（2026/10/8時点）の暫定値・決算整理前。9月は棚卸未反映。売上高は決算整理▲404万円を含む",
     size=14, color=SECONDARY)
notes(s, """
全社の26年9月期は、売上高8.34億円、売上総利益5.02億円（試算表ベースの暫定値）。
5月は母の日で月商1.1億円。創業以来はじめて月商1億を超えた。
""")

# =====================================================================
# 8-2. サービス開始からの推移（四半期・事業別の積み上げ）
# =====================================================================
s = content_slide("サービス開始からの推移", "四半期の売上（事業別）　単位：百万円　※税抜")
# 事業別 四半期エコノミクス（FY=10月〜9月、FY2021=第3期）。2021年4-6月から
# 第8期の4四半期は、試算表の四半期売上高に合うよう事業別の比率で按分（9月に決算整理▲4.04百万円を含める）
q_ap = [2.3, 9.0, 17.6, 22.8, 25.1, 28.2, 32.3, 41.5, 58.0, 62.4, 65.0, 90.6, 117.7, 119.6,
        110.0, 145.5, 171.0, 128.2]
q_af = [0.0, 0.0, 0.3, 2.2, 7.1, 2.8, 4.1, 6.1, 16.9, 8.2, 10.8, 20.1, 41.5, 27.1,
        33.1, 36.5, 56.3, 35.7]
q_ha = [0.0] * 11 + [0.6, 4.1, 7.3, 2.9, 5.7, 10.8, 11.0]
fy8 = {"ap": [118.2, 141.3, 172.0, 131.7], "af": [41.1, 37.1, 66.5, 27.8], "ha": [7.4, 9.9, 13.9, 15.7]}
tb_q = [178.737, 201.722, 271.903, 186.077 - 4.041]  # 試算表 売上高（百万円）
for i, t in enumerate(tb_q):
    k = t / (fy8["ap"][i] + fy8["af"][i] + fy8["ha"][i])
    q_ap.append(fy8["ap"][i] * k)
    q_af.append(fy8["af"][i] * k)
    q_ha.append(fy8["ha"][i] * k)
periods = [("21年9月期", 2), ("22年9月期", 4), ("23年9月期", 4), ("24年9月期", 4), ("25年9月期", 4), ("26年9月期", 4)]
series = [(q_ap, LIGHT, "アンドプランツ"), (q_af, FLOWER, "アンドフラワー"), (q_ha, MOSS, "ハナイチ")]
totals = [a + b + c for a, b, c in zip(q_ap, q_af, q_ha)]
slot, bw = 36, 24
gx0 = (W_PX - (slot * 21 + bw)) // 2  # グラフを横中央に
base_y, max_h = 610, 340
scale = max_h / max(totals)
# 凡例
lx = gx0
for vals, col, name in series:
    rect(s, lx, 160, 16, 16, col)
    text(s, lx + 24, 154, 160, 28, name, size=16, color=SECONDARY, en=(name != "ハナイチ"))
    lx += 150
for i in range(len(totals)):
    x = gx0 + i * slot
    y = base_y
    for vals, col, _ in series:
        h = vals[i] * scale
        if h > 0:
            rect(s, x, y - h, bw, h, col)
            y -= h
    text(s, x - 10, y - 26, bw + 20, 22, f"{totals[i]:.0f}", size=15, bold=True,
         align=PP_ALIGN.CENTER, en=True)
hline(s, gx0 - 8, base_y, slot * len(totals) + 2)
# 期のラベルと区切り
i0 = 0
for name, n in periods:
    x = gx0 + i0 * slot - 7
    w = n * slot
    if i0 > 0:
        ln = s.shapes.add_connector(1, px(x), px(base_y + 4), px(x), px(base_y + 40))
        ln.line.color.rgb = BORDER_LIGHT
        _drop_style(ln)
    text(s, x - 12, base_y + 14, w + 24, 26, name, size=15, color=SECONDARY, align=PP_ALIGN.CENTER)
    i0 += n
text(s, 56, 680, 1016, 44, "リリースから5年で、[[四半期2.7億円]]の規模になった", size=28, bold=True)
text(s, 56, H_PX - 76, 960, 24,
     "※ 21〜25年9月期は事業別の集計（注文日ベース・税抜）。26年9月期は試算表の売上高を事業別の比率で按分（イネイブラー等を含む）",
     size=14, color=SECONDARY)
notes(s, """
2021年5月のリリースから、四半期ごとの売上の推移。
アンドプランツから始まり、アンドフラワー、ハナイチと事業が増えてきた。
26年9月期の4-6月（母の日の四半期）は2.7億円。最初の四半期と比べると、ここまで来た。
""")

# =====================================================================
# 9. 事業別の数字（P-9 3項目の成長）
# =====================================================================
s = content_slide("事業別の数字", "25年9月期 → 26年9月期（前年比）　※税抜")
cols = [
    ("アンドプランツ/アンドフラワー", "売上", 7.2, 7.4, "億円", "+2%", "7.2億 → 7.4億"),
    ("アンドプランツ/アンドフラワー", "広告費込み限界利益", 1.5, 2.2, "億円", "+47%", "1.5億 → 2.2億"),
    ("ハナイチ", "売上", 45.4, 54.0, "百万円", "+19%", "45.4百万 → 54.0百万"),
]
x0, colw = 56, 320
to_oku = lambda v, u: v if u == "億円" else v / 100  # 3列とも同じ目盛り（億円換算）
top = max(to_oku(c[3], c[4]) for c in cols + [(0, 0, c[2], c[2], c[4]) for c in cols])
col_x = [56, 392, 760]  # 2列目と3列目の間に縦線＋余白
for i, (biz, metric, prev, cur, unit, yoy, cap) in enumerate(cols):
    x = col_x[i]
    text(s, x, 172, colw, 28, biz, size=18, color=SECONDARY, en=False)
    text(s, x, 204, colw, 40, metric, size=28, bold=True)
    text(s, x, 250, colw, 72, yoy, size=56, color=STRONG if yoy.startswith("-") else LIGHT, bold=True,
         en=True, spacing=1.0)
    # 小さな前年比較棒
    base_y, max_h = 620, 220
    for j, (val, col, lab) in enumerate([(prev, BG_GRAY, "25年9月期"), (cur, MOSS, "26年9月期")]):
        h = max(max_h * to_oku(val, unit) / top, 3)
        bx = x + 48 + j * 136
        rect(s, bx, base_y - h, 96, h, col)
        vtxt = f"{val}"
        text(s, bx - 20, base_y - h - 36, 136, 30, vtxt, size=22, bold=True,
             align=PP_ALIGN.CENTER, en=True)
        text(s, bx - 20, base_y + 10, 136, 28, lab, size=18, color=SECONDARY,
             align=PP_ALIGN.CENTER)
    hline(s, x + 24, base_y, colw - 48, BORDER_LIGHT)
    text(s, x, 332, colw, 24, f"単位：{unit}", size=16, color=SECONDARY)
vl = s.shapes.add_connector(1, px(736), px(168), px(736), px(650))
vl.line.color.rgb = BORDER_LIGHT
vl.line.width = Emu(12700)
_drop_style(vl)
text(s, 56, 690, 1000, 44, "広告を絞っても売上は落とさず、[[広告費込み限界利益が大きく残る形]]に変わった", size=28,
     bold=True)
text(s, 56, H_PX - 76, 960, 24,
     "※ アンドプランツ/アンドフラワーは自社EC＋モール、税抜（小松資料）。ハナイチの26年9月期は54.0百万円・25年9月期は比須田資料",
     size=14, color=SECONDARY)
notes(s, """
アンドプランツ/アンドフラワー：売上は+2%とほぼ横ばいだけど、広告費込み限界利益は+47%。広告費を3割減らして利益を1.5倍にした。
ハナイチ：売上+19%、注文数は2.3倍。生花は1本売れば利益が残る形になった。
詳細はこのあと各事業の発表で。
""")

# =====================================================================
# 11. 第8期にやったこと（一覧 → 1トピック1枚・写真）
# =====================================================================
TOPICS = [
    "花アプリ公開",
    "三和園芸さんとの委託発送開始",
    "観葉イネイブラー始動",
    "花イネイブラー本格始動",
    "アンドフラワーのブランド分割",
    "植物ケアアプリ公開",
    "マルシェ開催",
    "全社AI活用・MCP整備",
    "みずほ銀行の融資",
    "ギフティ社から追加で3億円の出資",
    "新城の解散",
    "ハナイチの各種施策進行",
]
TOPIC_SUB = {
}
s = content_slide()
text(s, 56, 323, 1016, 200, "8期もいろいろありましたね（しみじみ", size=56, bold=True, align=PP_ALIGN.CENTER,
     anchor=MSO_ANCHOR.MIDDLE)
notes(s, "26年9月期にやったことを、写真と一緒に1つずつ振り返ります。")

PHOTO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "photos")


def photos_for(n):
    """photos/ 配下の「NN_」で始まる画像（NN=トピック番号）を名前順に返す。"""
    if not os.path.isdir(PHOTO_DIR):
        return []
    pre = f"{n:02d}_"
    return sorted(os.path.join(PHOTO_DIR, f) for f in os.listdir(PHOTO_DIR)
                  if f.startswith(pre) and f.lower().endswith((".jpg", ".jpeg", ".png")))


def _sizes(files):
    from PIL import Image
    out = []
    for f in files:
        with Image.open(f) as im:
            out.append(im.size)
    return out


def _fit(iw, ih, w, h):
    return min(w / iw, h / ih) ** 2 * iw * ih


def feature_area(files, w, h, gap):
    sizes = _sizes(files)
    lw = w * 0.62
    rh = (h - gap * (len(files) - 2)) / (len(files) - 1)
    return _fit(*sizes[0], lw, h) + sum(_fit(iw, ih, w - lw - gap, rh) for iw, ih in sizes[1:])


def grid_area(files, w, h, gap):
    sizes = _sizes(files)
    cols = best_cols(files, w, h, gap)
    rows = (len(files) + cols - 1) // cols
    cw = (w - gap * (cols - 1)) / cols
    ch = (h - gap * (rows - 1)) / rows
    return sum(_fit(iw, ih, cw, ch) for iw, ih in sizes)


def best_cols(files, w, h, gap):
    """写真が合計で最も大きく見える列数を選ぶ（横長2枚なら縦積み、など）。"""
    from PIL import Image
    sizes = []
    for f in files:
        with Image.open(f) as im:
            sizes.append(im.size)
    best, best_area = 1, -1
    for cols in range(1, len(files) + 1):
        rows = (len(files) + cols - 1) // cols
        cw = (w - gap * (cols - 1)) / cols
        ch = (h - gap * (rows - 1)) / rows
        area = sum(min(cw / iw, ch / ih) ** 2 * iw * ih for iw, ih in sizes)
        if area > best_area:
            best, best_area = cols, area
    return best


def place_contain(slide, path, x, y, w, h):
    from PIL import Image, ImageOps
    # 容量を抑えるため長辺1600pxに縮小したコピーを使う
    cache = os.path.join(PHOTO_DIR, ".cache")
    os.makedirs(cache, exist_ok=True)
    small = os.path.join(cache, os.path.splitext(os.path.basename(path))[0] + ".jpg")
    if not os.path.exists(small):
        with Image.open(path) as im:
            im = ImageOps.exif_transpose(im)
            if im.mode in ("RGBA", "LA", "P"):
                im = im.convert("RGBA")
                bg = Image.new("RGB", im.size, (255, 255, 255))
                bg.paste(im, mask=im.split()[-1])
                im = bg
            im = im.convert("RGB")
            im.thumbnail((1600, 1600))
            im.save(small, quality=85)
    path = small
    with Image.open(path) as im:
        iw, ih = im.size
    k = min(w / iw, h / ih)
    pw, ph = iw * k, ih * k
    slide.shapes.add_picture(path, px(x + (w - pw) / 2), px(y + (h - ph) / 2), px(pw), px(ph))


for i, t in enumerate(TOPICS):
    n = i + 1
    s = content_slide(t, TOPIC_SUB.get(n))
    area_x, area_y, area_w, area_h = 56, 160, 1016, 620
    files = photos_for(n)
    if files and len(files) >= 3 and feature_area(files, area_w, area_h, 16) > grid_area(files, area_w, area_h, 16):
        # 1枚目を左に大きく、残りを右に縦積み
        gap = 16
        lw = area_w * 0.62
        place_contain(s, files[0], area_x, area_y, lw, area_h)
        rh = (area_h - gap * (len(files) - 2)) / (len(files) - 1)
        for j, f in enumerate(files[1:]):
            place_contain(s, f, area_x + lw + gap, area_y + j * (rh + gap), area_w - lw - gap, rh)
    elif files:
        gap = 16
        cols = best_cols(files, area_w, area_h, gap)
        rows = (len(files) + cols - 1) // cols
        cw = (area_w - gap * (cols - 1)) / cols
        ch = (area_h - gap * (rows - 1)) / rows
        for j, f in enumerate(files):
            r, c = divmod(j, cols)
            place_contain(s, f, area_x + c * (cw + gap), area_y + r * (ch + gap), cw, ch)
    else:
        rect(s, area_x, area_y, area_w, area_h, None, line=BORDER_LIGHT, dash=True)
        text(s, area_x, area_y, area_w, area_h, "写真（届き次第差し替え）", size=25, color=SECONDARY,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    notes(s, f"{n}. {t}" + (f"（{TOPIC_SUB[n]}）" if n in TOPIC_SUB else "") + "：（口頭で）")
    if t.startswith("ハナイチ"):
        # 新しい仲間（入社月のみ）
        s = content_slide("新しい出会い（入社）もありました")
        joins = ["2025年10月", "2025年11月", "2025年12月", "2026年7月"]
        d, gap = 200, (1016 - 200 * 4) / 3
        for k, m in enumerate(joins):
            x = 56 + k * (d + gap)
            # 写真は入社が新しい順に届いたので逆順で当てる
            place_contain(s, os.path.join(PHOTO_DIR, "members", f"{4 - k}.png"), x, 300, d, d)
            text(s, x - 20, 524, d + 40, 36, m, size=25, bold=True, align=PP_ALIGN.CENTER)
        notes(s, "26年9月期は新しい仲間も増えました。（舘脇さん・頼政さん・川嶋さん・塚本さんを口頭で紹介）")
    if t.startswith("ギフティ"):
        # 出資の結果（累計調達額と時価総額）
        s = content_slide("資金調達の到達点")
        for j, (lab, val, unit) in enumerate([("累計資金調達額", "7.4", "億円"), ("会社の時価総額", "21", "億円")]):
            x = 56 + j * 520
            text(s, x, 150, 480, 30, lab, size=22, color=SECONDARY)
            tb = text(s, x, 184, 480, 96, val, size=84, bold=True, en=True, spacing=1.0)
            r = tb.text_frame.paragraphs[0].add_run()
            r.text = unit
            _set_font(r, 31, MOSS, True, en=False)
        hline(s, 56, 300, 1016)
        # 投資家ロゴ（VC・事業会社 7社 → エンジェル投資家）
        logo_dir = os.path.join(PHOTO_DIR, "logos")
        vc_rows = [["chiba-dojo", "new-commerce-ventures", "ffg", "pola-orbis-capital"],
                   ["value-chain-innovation-fund", "giftee", "seibu-holdings"]]
        for ri, row in enumerate(vc_rows):
            cw = 1016 / 4
            x0 = 56 + (1016 - cw * len(row)) / 2
            for ci, name in enumerate(row):
                place_contain(s, os.path.join(logo_dir, name + ".png"), x0 + ci * cw + 28, 334 + ri * 112, cw - 56, 64)
        text(s, 56, 548, 1016, 28, "エンジェル投資家 ほか5名", size=18, color=SECONDARY, align=PP_ALIGN.RIGHT)
        hline(s, 56, 588, 1016)
        text(s, 56, 616, 1016, 140, ["累計資金調達額は[[7.4億円]]に到達、", "会社の時価総額は[[21億円]]に。"],
             size=38, bold=True, spacing=1.45)
        notes(s, "ギフティからの出資で、累計資金調達額は7.4億円に到達。会社の時価総額は21億円になった。")

# =====================================================================
# 11-2. みなさん、お疲れ様でした（キーメッセージ・Moss 全面）
# =====================================================================
s = content_slide()
text(s, 56, 300, 1016, 200, "みなさん、大変お疲れ様でした〜👏", size=60, bold=True,
     align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
notes(s, "26年9月期の振り返りはここまで。みなさん、大変お疲れ様でした！")

# =====================================================================
# 12. 章扉 02
# =====================================================================
s = divider("02", "FY2027 DIRECTION", "27年9月期に向けて", "")

# =====================================================================
# 13. 第9期の数字（P-10 実績 vs 計画）
# =====================================================================
s = content_slide("27年9月期の計画", "26年9月期 実績 → 27年9月期 計画（売上）　※税抜")
plans = [
    ("アンドプランツ/アンドフラワー", 7.4, 12.4, "+68%"),
    ("イネイブラー", 0.1, 1.9, "19倍"),
    ("ハナイチ", 0.54, 2.7, "5.0倍"),
]
top = max(p[2] for p in plans)
for i, (lab, cur, plan, g) in enumerate(plans):
    x = 56 + i * 344
    text(s, x, 172, 336, 36, lab, size=20, bold=True)
    text(s, x, 206, 320, 24, "単位：億円", size=16, color=SECONDARY)
    base_y, max_h = 560, 260
    for j, (val, col, cap) in enumerate([(cur, BG_GRAY, "26年9月期 実績"), (plan, MOSS, "27年9月期 計画")]):
        h = max(max_h * val / top, 3)  # 3事業とも同じ目盛り（規模の差が見えるように）
        bx = x + 40 + j * 136
        rect(s, bx, base_y - h, 96, h, col)
        text(s, bx - 20, base_y - h - 36, 136, 30, f"{val:g}億", size=22, bold=True,
             align=PP_ALIGN.CENTER)
        text(s, bx - 30, base_y + 10, 156, 28, cap, size=16, color=SECONDARY,
             align=PP_ALIGN.CENTER)
    hline(s, x + 16, base_y, 300)
    text(s, x, 610, 320, 70, g, size=48, color=LIGHT, bold=True, en=(g.startswith("+")))
text(s, 56, H_PX - 76, 960, 24,
     "※ ハナイチの26年9月期実績は54.0百万円", size=14,
     color=SECONDARY)
notes(s, """
27年9月期は前年比ではなく「計画に対してどうか」で見る。
売上の計画は、アンドプランツ/アンドフラワーが12.4億、イネイブラーが0.1億→1.9億、ハナイチが2.7億。
""")

# =====================================================================
# 14. 章扉 03
# =====================================================================
s = divider("03", "WHY WE DO THIS", "なぜ、僕らがこれをやるのか", "")
notes(s, "ここからは数字の話ではなく、なぜ自分たちがこれをやるのか、の話をします。")

# =====================================================================
# 15. 出発点：ミッション（P-2）
# =====================================================================
s = content_slide()
text(s, 56, 300, 900, 30, "- OUR MISSION -", size=20, color=SECONDARY, en=True, letter=4)
text(s, 56, 352, 1016, 150, ["ITとデザインで、", "[[みどりのある暮らし]]をもっと身近に。"], size=52,
     bold=True, spacing=1.35)
notes(s, """
Domuzのミッションは「ITとデザインでみどりのある暮らしをもっと身近に」。
根っこにあるのは、花や植物っていいよね、という気持ち。
植物を育てる楽しさや、花をもらったときのうれしさを、もっと多くの人に届けたい。
""")

# =====================================================================
# 16. 危機感（P-2）
# =====================================================================
s = content_slide()
text(s, 56, 323, 1016, 200, "今、業界で感じている危機感", size=56, bold=True, align=PP_ALIGN.CENTER,
     anchor=MSO_ANCHOR.MIDDLE)
notes(s, "ここからは、いま業界で感じている危機感の話。")

s = content_slide()
crisis = ["生産者の減少", "高齢化によるニーズの変化", "若者の花離れ", "ビジネスシーンの贈答文化の変化"]
for k, t in enumerate(crisis):
    col, row = k % 2, k // 2
    x, y = 80 + col * 504, 172 + row * 280
    text(s, x, y, 120, 80, f"0{k + 1}", size=64, color=LIGHT, bold=True, en=True, spacing=1.0)
    rect(s, x, y + 92, 48, 4, LIGHT)
    text(s, x, y + 120, 488, 100, t, size=30, bold=True, spacing=1.4)
notes(s, """
生産者の高齢化と減少。高齢化によるニーズの変化。若者の花離れ。ビジネスシーンの贈答文化の変化。
""")

s = content_slide()
text(s, 56, 293, 1016, 260,
     ["このままだと、花や植物を楽しむ文化が", "[[小さくなってしまう]]かもしれない。"], size=46, bold=True,
     spacing=1.4, anchor=MSO_ANCHOR.MIDDLE)
notes(s, """
一方で、生産者の減少や、花をつくる・売ることの難しさがある。
このままだと、植物を育てたり、花を贈ったり、楽しんだりする文化が小さくなってしまうかもしれない。
そこをDomuzが変えていきたい。
""")

# =====================================================================
# 17. 裾野を広げる（2カラム）
# =====================================================================
s = content_slide()
text(s, 56, 323, 1016, 200, "花/植物を楽しむ人の「[[裾野]]」を広げる", size=56, bold=True, align=PP_ALIGN.CENTER,
     anchor=MSO_ANCHOR.MIDDLE)
notes(s, "だから、花や植物を楽しむ人の裾野を広げる。")

s = content_slide()
for i, (head, body) in enumerate([
    ("植物なら", ["買うとき・育てるときの", "面倒や不安を減らす。", "気軽に育てられる土壌をつくる。"]),
    ("花なら", ["ほかの贈り物とセットで届けて、", "普段は花を買わない人にも", "受け取ってもらう。"]),
]):
    x = 56 + i * 520
    text(s, x, 196, 480, 50, head, size=34, bold=True, color=LIGHT)
    text(s, x, 260, 480, 180, body, size=27, spacing=1.6)
hline(s, 56, 480, 1016)
text(s, 56, 520, 1016, 200,
     ["「植物を育てるのっていいな」", "「花をもらうっていいな」", "「次は自分も[[贈ってみよう]]」"],
     size=34, bold=True, spacing=1.45)
notes(s, """
植物なら、買うときや育てるときの面倒や不安を減らす。もっと気軽に育てる土壌を作る。
花なら、ほかの贈り物とセットで届けることで、普段は花を買わない人にも受け取ってもらう。
「植物育てるのっていいな」「花をもらうっていいな」「次は自分も贈ってみよう」。
そんなきっかけを、いろんなシーンにつくっていきたい。
""")

# =====================================================================
# 18. 消費者が産業を支える（フロー図）
# =====================================================================
s = content_slide("産業を支えているのは、最後に楽しむ人")
chain = ["種苗", "生産者", "卸", "仲卸", "流通", "小売"]
cx, cy, cw, ch, gap = 56, 236, 118, 72, 28
for i, lab in enumerate(chain):
    x = cx + i * (cw + gap)
    rect(s, x, cy, cw, ch, None, line=MOSS)
    text(s, x, cy, cw, ch, lab, size=25, bold=True, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    arrow(s, x + cw + 8, cy + ch / 2 - 7, 12, 14)
x = cx + 6 * (cw + gap)
rect(s, x, cy - 12, 1072 - x, ch + 24, MOSS)
text(s, x, cy - 12, 1072 - x, ch + 24, ["買って", "楽しむ人"], size=22, color=WHITE, bold=True,
     align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.2)
text(s, 56, 400, 1016, 160,
     ["最後にお金を払って、花や植物を楽しむ人が", "いちばん大事。"], size=46, bold=True, spacing=1.4)
text(s, 56, 590, 1016, 100,
     ["買う・贈る・もらう・育てる機会を増やすことが、", "[[産業全体への貢献]]につながる。"], size=28,
     spacing=1.6)
notes(s, """
花き産業には、種苗、生産者、卸、仲卸、流通、小売など、多くの人が関わっている。
その産業を支えるのは、最後にお金を払って花や植物を買い、楽しむ人たち。最終消費者が最も大事。
買う・贈る・もらう・育てる機会を増やすことが、産業全体への貢献につながる。
""")

# =====================================================================
# 19. 各事業はミッションにつながっている（P-11）
# =====================================================================
s = content_slide("どの事業も、同じところにつながっている")
rows = [
    ("1", "アンドプランツ/アンドフラワー", "自分たちで花や植物を販売し、楽しむ人を増やす"),
    ("2", "イネイブラー", "いろんな事業者の商品と花をセットで届け、買う・贈る機会を増やす"),
    ("3", "ハナイチ", "花を売る人・教室や撮影で使う人が、もっと仕入れやすくする"),
]
y = 176
for n, biz, desc in rows:
    text(s, 56, y, 60, 64, n, size=48, color=LIGHT, bold=True, en=True)
    text(s, 128, y + 4, 940, 44, biz, size=31, bold=True)
    text(s, 128, y + 56, 940, 40, desc, size=25)
    hline(s, 56, y + 116, 1016)
    y += 136
flow = ["入口を広げる", "楽しむ人が増える", "産業が良くなる", "Domuzも成長する"]
fx, fw = 56, 238
for i, f in enumerate(flow):
    x = fx + i * (fw + 22)
    col = LIGHT if i == len(flow) - 1 else MOSS
    text(s, x, 610, fw, 44, f, size=25, bold=True, color=col, align=PP_ALIGN.CENTER)
    if i < len(flow) - 1:
        arrow(s, x + fw + 4, 622, 12, 16)
text(s, 56, 680, 1016, 40, "それぞれの事業で入口を広げ、利益を出して、また次の入口をつくる。", size=22,
     color=SECONDARY, align=PP_ALIGN.CENTER)
notes(s, """
・AP／AF：自分たちで花や植物を販売し、楽しむ人を増やす
・イネイブラー：いろんな事業者の商品と花をセットで届け、花を買う・贈る機会を増やす
・ハナイチ：花を販売する人や、教室・撮影などで使う人が、もっと仕入れやすくする
それぞれの事業で入口を広げ、花を楽しむ人、植物を育てる人を増やす。
その結果、産業がより良くなり、Domuzとしても利益を出して成長する。このつながりをつくりたい。
""")

# =====================================================================
# 20. 新規事業 × 届ける現場（川崎）
# =====================================================================
s = content_slide("新しい入口は、届ける現場から生まれる", "イネイブラー・高付加価値3PL")
text(s, 56, 196, 1016, 160,
     ["他社の贈り物と花をセットにして、", "きれいに、確実に届けられること。",
      "それ自体が、[[Domuzにしかない強み]]。"], size=36, bold=True, spacing=1.45)
hline(s, 56, 400, 1016)
text(s, 56, 424, 600, 32, "27年9月期に動き出すもの", size=22, color=SECONDARY)
news = [
    ("10月", "生花イネイブラー 2件スタート予定（PAPABUBBLE／フレッシュロースター）"),
    ("10月", "HAKUBA CRAFT：クラフトビールを冷蔵保管し、生花とセットで発送"),
    ("母の日", "卸モデルの導入先から追加発注（昨年+50%の希望も）"),
    ("進行中", "カインズ・ハンズとの連携、ギフティとの共同提案"),
]
y = 468
for tag, desc in news:
    text(s, 56, y, 120, 36, tag, size=22, bold=True, color=LIGHT)
    text(s, 184, y, 888, 36, desc, size=22)
    y += 48
text(s, 56, 684, 1016, 60,
     "案件が増えるほど、手が慣れるほど、利益は大きくなる。[[川崎の一箱一箱が、次の入口]]になる。", size=25,
     bold=True)
notes(s, """
（特に川崎デリバリーのみんなへ）
イネイブラーや3PLは、他社の商品と花をセットにして、きれいに、確実に届けられることが肝。
送料を先方のお客様負担にできるのも、花をセットにしてDomuzから発送するからこそ。
発送の固定費はロットが大きいほど効率化できるし、習熟度で効率は大きく変わる。
つまり、案件をたくさん取れば取るほど、現場が慣れるほど、利益率も額も上がっていく。
今期はPAPABUBBLE、フレッシュロースター、HAKUBA CRAFTのクラフトビール×生花など、新しい贈り物が川崎から出ていく。
普段は花を買わない人のところに、最初の一本を届けているのは、みんなの手。
""")

# =====================================================================
# 21. 5年後、10年後（P-2）
# =====================================================================
s = content_slide("5年後、10年後に言われたいこと")
text(s, 56, 260, 1016, 240,
     ["「Domuzというチームがいたから、", "花や植物を楽しむ文化が[[広がった]]よね」",
      "「贈り物の価値が、もっと[[高まった]]よね」"], size=44, bold=True, spacing=1.5)
notes(s, """
「Domuzというチームがいたから、花や植物を楽しむ文化が広がったよね」
「贈り物の価値がもっと高まったよね」と言われる会社にしたい。
""")

# =====================================================================
# 22. ラストメッセージ（P-14）
# =====================================================================
s = content_slide("最後に")
text(s, 56, 250, 1016, 240,
     ["花や植物を楽しむ人と機会を増やすことが、", "[[産業の未来]]にも、[[Domuzの成長]]にもつながる。"], size=42,
     bold=True, spacing=1.5)
text(s, 56, 470, 1000, 120,
     ["事業は違っても、向かっている先は同じ。", "一人ひとりの仕事が、誰かの「花っていいな」の入口になっている。"],
     size=25, spacing=1.7)
text(s, 56, 640, 1016, 60, "27年9月期も、みんなで[[楽しみながら]]やり切ろう。", size=40, bold=True)
notes(s, """
一番伝えたいのは、「花や植物を楽しむ人と機会を増やすことが、産業全体の未来にも、Domuzの成長にもつながる」ということ。
今日は一日、よろしくお願いします！
""")

# 使っていないレイアウトを削除してファイルを軽くする（Drive へのアップロード用）
layouts = prs.slide_master.slide_layouts
for layout in list(layouts):
    if layout is not BLANK:
        layouts.remove(layout)

out = sys.argv[1] if len(sys.argv) > 1 else "deck.pptx"
prs.save(out)
with open("talk_script.md", "w") as f:
    f.write("# 1day合宿 2026.10.09 全社パート — トーク台本（スライド番号つき）\n\n")
    for n, body in TALK:
        f.write(f"## {n}\n\n{body}\n\n")
print("saved", out, "slides:", len(prs.slides))
