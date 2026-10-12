"""Domuz デザインシステム「発表スライド」型の共通部品（python-pptx）。ギフティ向け資料・ハナイチ資料で共用。"""
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


def content_slide(title=None, sub=None, accent=None):
    """白背景＋左端ライトグリーン縦帯8px＋左上タイトル＋右下ページ番号。"""
    global page_no
    page_no += 1
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, 8, H_PX, accent or LIGHT)
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
def new_slide():
    """白紙スライドを追加してページ番号を進める（表紙など、content_slide を使わないページ用）。"""
    global page_no
    page_no += 1
    return prs.slides.add_slide(BLANK)


def yen(v):
    return f"▲{-v:.1f}" if v <= -0.05 else f"{abs(v):.1f}"



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

