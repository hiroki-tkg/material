"""Domuz デザインシステム「発表スライド」型の共通部品（python-pptx）。

使い方:
    import sys; sys.path.insert(0, "<skillの scripts ディレクトリ>")
    from deck_lib import *
    use_theme("hanaichi")          # "ap" / "af" / "hanaichi" / "domuz"
    s = content_slide("タイトル", "サブタイトル")
    ...
    save("out.pptx")

座標はすべて px（1128×846 のキャンバス、10in 幅）。色・フォントは design-system の値。
"""
import re

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu

# ---- 共通トークン（どのテーマでも同じ） ----
MOSS = RGBColor(0x00, 0x43, 0x47)        # 本文・見出しの文字色（--brand-primary / --text-primary）
SECONDARY = RGBColor(0x62, 0x62, 0x62)   # 補足の文字色
STRONG = RGBColor(0xE1, 0x64, 0x64)      # 強調・マイナス（赤）
MUTED = RGBColor(0x99, 0x99, 0x99)       # 軸ラベル・ページ番号
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BG_GRAY = RGBColor(0xCB, 0xD0, 0xD3)     # 控除の棒（ウォーターフォール）
BORDER_LIGHT = RGBColor(0xC9, 0xCF, 0xCF)  # 罫線
WATERMARK = RGBColor(0xEC, 0xEE, 0xEE)   # グラフの補助線
PALE = RGBColor(0xE4, 0xE8, 0xE9)        # 売上の棒（背景寄りのグレー）

# ---- ブランド色（テーマで切り替える） ----
LIGHT = RGBColor(0x00, 0xD7, 0x9C)       # アンドプランツ／Domuz 共通のライトグリーン（--brand-secondary）
FLOWER = RGBColor(0xEF, 0x66, 0x7D)      # アンドフラワーのピンク（--brand-flower）
FLOWER_LIGHT = RGBColor(0xF7, 0xB3, 0xBE)
HANA = RGBColor(0xF5, 0xB7, 0x00)        # ハナイチの黄
HANA_LIGHT = RGBColor(0xFB, 0xE3, 0x8C)
HANA_DARK = RGBColor(0xA6, 0x7C, 0x00)   # 黄は白地で線が読みにくいので、線・数字はこちら

THEMES = {
    # accent: 左端の帯・章番号・主張番号・主役の棒。light: 2番目の系列・薄い帯。dark: 線・数字の強調。
    # divider_bg / divider_fg: 章扉の地色と文字色
    "domuz":    dict(accent=LIGHT,  light=PALE,         dark=MOSS,      divider_bg=MOSS,   divider_fg=WHITE),
    "ap":       dict(accent=LIGHT,  light=PALE,         dark=MOSS,      divider_bg=MOSS,   divider_fg=WHITE),
    "af":       dict(accent=FLOWER, light=FLOWER_LIGHT, dark=FLOWER,    divider_bg=FLOWER, divider_fg=WHITE),
    "hanaichi": dict(accent=HANA,   light=HANA_LIGHT,   dark=HANA_DARK, divider_bg=HANA,   divider_fg=MOSS),
}
THEME_ALIASES = {"andplants": "ap", "アンドプランツ": "ap", "andflower": "af", "アンドフラワー": "af",
                 "ハナイチ": "hanaichi", "hana-ichi": "hanaichi", "internal": "domuz", "社内": "domuz"}


class _Theme:
    name = "domuz"
    accent = LIGHT
    light = PALE
    dark = MOSS
    divider_bg = MOSS
    divider_fg = WHITE


T = _Theme()


def use_theme(name):
    """資料全体のテーマ色を決める。表紙・章扉・主張番号・グラフの主役の色がまとめて切り替わる。"""
    key = THEME_ALIASES.get(name, name)
    if key not in THEMES:
        raise ValueError(f"unknown theme {name!r}; choose from {list(THEMES)}")
    T.name = key
    for k, v in THEMES[key].items():
        setattr(T, k, v)
    return T


FONT_EN = "Montserrat"
FONT_JA = "Zen Kaku Gothic New"  # 和文。Montserrat にない文字を補う

W_PX, H_PX = 1128, 846
EMU_PER_PX = 9144000 / W_PX  # 10in 幅
MARGIN = 56                   # 左右の余白
CONTENT_W = W_PX - 2 * MARGIN  # 1016


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


def save(path):
    prs.save(path)
    print("saved", len(prs.slides._sldIdLst), "slides ->", path)


def _set_font(run, size_px, color, bold, en=None):
    """英数字は Montserrat、和文は Zen Kaku Gothic New（1つのランの中でも文字ごとに使い分けられる）。"""
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
    """lines: 文字列 or 文字列のリスト（1要素＝1段落）。
    インライン装飾: [[語]] はテーマのアクセント色で太字、!!語!! は赤で太字、**語** は太字。"""
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
                part, c, b = part[2:-2], T.dark, True
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


def badge(slide, x, y, n, color=None, d=22):
    """番号の丸（中心座標で指定）。"""
    rect(slide, x - d / 2, y - d / 2, d, d, color or T.accent, shape=MSO_SHAPE.OVAL)
    text(slide, x - d / 2, y - d / 2, d, d, str(n), size=13, color=WHITE, bold=True, en=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)


def legend(slide, x, y, items, line=False):
    """凡例を横に並べる。items: [(ラベル, 色)]。line=True なら線の凡例。x を返す（続けて置けるように）。"""
    for lab, col in items:
        if line:
            rect(slide, x, y + 10, 20, 3, col)
            x += 24
        else:
            rect(slide, x, y + 6, 10, 10, col)
            x += 14
        tb = text(slide, x, y, 200, 22, lab, size=10, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        x += int(sum(1.0 if ord(ch) > 0x7F else 0.6 for ch in lab) * 10) + 18
    return x


# =====================================================================
# ページの型
# =====================================================================
def new_slide():
    """白紙スライド（表紙など content_slide を使わないページ用）。ページ番号は進める。"""
    global page_no
    page_no += 1
    return prs.slides.add_slide(BLANK)


def cover(label, title_lines, sub, meta_lines):
    """表紙: 左端にテーマ色の帯、宛先ラベル、大きなタイトル（2行まで）、サブ、右下に日付・社名・氏名。"""
    s = new_slide()
    rect(s, 0, 0, 8, H_PX, T.accent)
    text(s, 96, 220, 960, 40, label, size=26, color=SECONDARY)
    text(s, 96, 290, 980, 180, title_lines, size=56, bold=True, spacing=1.3)
    text(s, 96, 480, 960, 40, sub, size=24, color=SECONDARY)
    text(s, 96, 640, 900, 120, meta_lines, size=22, color=SECONDARY, spacing=1.5)
    return s


def content_slide(title=None, sub=None, accent=None):
    """白背景＋左端のテーマ色の帯8px＋左上タイトル＋右下ページ番号。accent で1ページだけ色を変えられる。"""
    global page_no
    page_no += 1
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, 8, H_PX, accent or T.accent)
    if title:
        text(s, MARGIN, 44, 1000, 56, title, size=38, bold=True)
    if sub:
        text(s, MARGIN, 104, 1000, 36, sub, size=20, color=SECONDARY)
    text(s, W_PX - 120, H_PX - 44, 80, 24, str(page_no), size=14, color=MUTED,
         align=PP_ALIGN.RIGHT, en=True)
    return s


def footnote(s, body):
    """ページ最下部の注記（※で始める）。2行までに収める。"""
    text(s, MARGIN, H_PX - 84, 960, 40, body, size=13, color=SECONDARY, spacing=1.3)


def message(s, body, y=104):
    """タイトル直下の結論1行（太字）。サブタイトルの代わりに置く。"""
    text(s, MARGIN, y, CONTENT_W, 36, body, size=21, bold=True)


def divider(num, en_label, title, sub="", bg=None, fg=None):
    """章扉: 全面テーマ色＋アウトラインの章番号＋英字ラベル＋和文タイトル。"""
    global page_no
    page_no += 1
    bg = bg or T.divider_bg
    fg = fg or T.divider_fg
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = bg
    tb = text(s, 80, 240, 400, 150, num, size=120, color=fg, en=True, spacing=1.0)
    rpr = tb.text_frame.paragraphs[0].runs[0].font._rPr
    for el in rpr.findall(qn("a:solidFill")):
        rpr.remove(el)
    ln = rpr.makeelement(qn("a:ln"), {"w": "19050"})
    sf = ln.makeelement(qn("a:solidFill"), {})
    sf.append(sf.makeelement(qn("a:srgbClr"), {"val": str(fg)}))
    ln.append(sf)
    rpr.insert(0, ln)
    rpr.insert(1, rpr.makeelement(qn("a:noFill"), {}))
    text(s, 80, 416, 900, 32, en_label, size=22, color=fg, en=True, letter=6)
    text(s, 80, 460, 960, 64, title, size=46, color=fg, bold=True)
    if sub:
        text(s, 80, 544, 960, 36, sub, size=22, color=fg)
    return s


def agenda(title, items, note=None):
    """本資料の構成: 大きな番号＋見出し＋説明を3〜4項目。items: [(番号, 見出し, 説明)]。"""
    s = content_slide(title)
    y = 220 if len(items) <= 3 else 190
    step = 150 if len(items) <= 3 else 130
    for i, (n, label, sub) in enumerate(items):
        text(s, 96, y + 16, 80, 64, n, size=60, color=T.accent, bold=True, en=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        text(s, 190, y + 16, 870, 64, label, size=34, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        text(s, 190, y + 84, 870, 30, sub, size=20, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        if i < len(items) - 1:
            hline(s, 96, y + step - 22, 936)
        y += step
    if note:
        footnote(s, note)
    return s


def draw_claims(s, claims, y=124, color=None):
    """要約ページ: 番号＋主張（太字1行）＋根拠の箇条書き2〜3行。claims: [(番号, 主張, [根拠, ...])]。
    根拠は1行に収める（全角47字相当まで）。超えると2行分の高さを取る。"""
    color = color or T.accent
    for n, head, lines_ in claims:
        text(s, MARGIN, y, 60, 50, n, size=42, color=color, bold=True, en=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        text(s, 120, y, 952, 50, head, size=24, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.2)
        y += 62
        for ln_ in lines_:
            rect(s, 124, y + 16, 8, 8, color)
            text(s, 142, y, 930, 70, ln_, size=19, spacing=1.45)
            vis = sum(1.0 if ord(ch) > 0x7F else 0.55 for ch in ln_)
            y += 64 if vis > 47 else 38
        y += 30
    return y


def terms_page(title, rows, row_h=None):
    """用語と集計の前提: 左に用語（太字）、右に定義。rows: [(用語, 定義)]。10行前後まで。"""
    s = content_slide(title)
    rh = row_h or (60 if len(rows) > 10 else 64)
    y = 150
    hline(s, MARGIN, y, CONTENT_W)
    for k_, v_ in rows:
        text(s, MARGIN, y, 236, rh, k_, size=19, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        text(s, 300, y, 772, rh, v_, size=16, color=SECONDARY, spacing=1.35, anchor=MSO_ANCHOR.MIDDLE)
        y += rh
        hline(s, MARGIN, y, CONTENT_W)
    return s


# =====================================================================
# グラフ・表
# =====================================================================
def yen(v):
    """百万円の表示。マイナスは ▲。"""
    return f"▲{-v:.1f}" if v <= -0.05 else f"{abs(v):.1f}"


def waterfall(s, x, name, steps, end_label, end_val, sales, color=None, lo=-40, unit="", bar=None):
    """売上を100とした控除のウォーターフォール（1ページに2〜3本並べる想定、幅は約330px）。
    steps: [(項目名, 金額)] を売上から順に引く。end_label は最後の棒の名前（改行可）。縦軸は 100〜lo（%）。"""
    color = color or MOSS
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
    col = (bar or T.accent) if endp >= 0 else (MUTED if abs(endp) < 0.05 else STRONG)
    y0, y1 = sorted((yv(0), yv(endp)))
    rect(s, bx, y0, bw, max(y1 - y0, 2), col)
    ly = y0 - 24 if endp >= 0 else y1 + 3
    text(s, bx - 12, ly, bw + 24, 22, f"{(0.0 if abs(endp) < 0.05 else endp):.1f}", size=14, bold=True, color=col,
         align=PP_ALIGN.CENTER, en=True)
    labels.append((bx, end_label, MOSS, True))
    hline(s, x - 6, yv(0), bx + bw + 12 - x, MUTED)
    ly_ = yv(min(0.0, endp)) + 10 + (0 if endp >= 0 else 20)  # 0の線（赤字なら棒の下）のすぐ下に項目名
    for lx, lab, c, b in labels:
        text(s, lx - 10, ly_, bw + 20, 44, lab.split("\n"), size=12, color=c, bold=b, align=PP_ALIGN.CENTER, spacing=1.2)
    return s


def bar_chart(s, x, y, w, h, labels, series, vmax=None, ticks=None, stacked=False, colors=None,
              value_labels=False, label_every=1, unit=""):
    """縦棒グラフ。series: [(名前, [値...])]。stacked=True で積み上げ、False で棒を並べる。
    棒の上の数値は value_labels=True のとき。横軸ラベルは label_every ごとに描く（月次が長いときは 3 など）。
    戻り値: (slot_w, yv) で、線や注釈を重ねるときに使う。"""
    n = len(labels)
    colors = colors or [T.accent, T.light, BG_GRAY, PALE]
    if vmax is None:
        tops = [sum(v[i] for _, v in series) for i in range(n)] if stacked else [max(v[i] for _, v in series) for i in range(n)]
        vmax = max(tops) * 1.18
    cx0, cx1 = x + 36, x + w - 10
    top_, base_ = y + 20, y + h - 30
    slot = (cx1 - cx0) / n
    yv = lambda v: base_ - (base_ - top_) * v / vmax
    for v in (ticks or []):
        hline(s, cx0, yv(v), cx1 - cx0, BORDER_LIGHT if v == 0 else WATERMARK)
        text(s, x, yv(v) - 8, 32, 16, f"{v:g}", size=9, color=MUTED, align=PP_ALIGN.RIGHT, en=True)
    if not ticks:
        hline(s, cx0, base_, cx1 - cx0, BORDER_LIGHT)
    k = len(series)
    for i in range(n):
        if stacked:
            bx, bw = cx0 + i * slot + slot * 0.2, slot * 0.6
            cum = 0.0
            for (name, vals), col in zip(series, colors):
                v = vals[i]
                rect(s, bx, yv(cum + v), bw, yv(cum) - yv(cum + v), col)
                cum += v
            if value_labels:
                text(s, bx - 16, yv(cum) - 18, bw + 32, 16, f"{cum:,.{0 if cum >= 100 else 1}f}{unit}", size=10, bold=True,
                     align=PP_ALIGN.CENTER, en=True)
        else:
            bw = slot * 0.7 / k
            for j, ((name, vals), col) in enumerate(zip(series, colors)):
                bx = cx0 + i * slot + slot * 0.15 + j * bw
                v = vals[i]
                rect(s, bx, yv(v), bw - 3, base_ - yv(v), col)
                if value_labels:
                    text(s, bx - 12, yv(v) - 16, bw + 20, 14, f"{v:,.{0 if v >= 100 else 1}f}{unit}", size=9, bold=True,
                         color=MOSS if j == 0 else SECONDARY, align=PP_ALIGN.CENTER, en=True)
        if i % label_every == 0:
            text(s, cx0 + i * slot - 10, base_ + 4, slot + 20, 30, labels[i].split("\n"), size=9, color=MUTED, align=PP_ALIGN.CENTER, spacing=1.2)
    return slot, yv


def kpi_table(s, x, y, w, header, rows, col_w=None, bold_rows=(), row_h=34, num_color=None):
    """主要指標の表。header: 列見出しのリスト（先頭は空でよい）。rows: [[ラベル, 値1, 値2, ...]]。
    値の列は右寄せ。bold_rows に入れた行番号は太字。"""
    ncol = len(header)
    col_w = col_w or [w - 120 * (ncol - 1)] + [120] * (ncol - 1)
    xs = [x]
    for cw in col_w[:-1]:
        xs.append(xs[-1] + cw)
    for j, hd in enumerate(header):
        text(s, xs[j], y, col_w[j], 24, hd, size=14, color=SECONDARY, bold=True,
             align=PP_ALIGN.LEFT if j == 0 else PP_ALIGN.RIGHT)
    hline(s, x, y + 30, w, MOSS, 1.5)
    y += 38
    for i, row in enumerate(rows):
        b = i in bold_rows
        for j, v in enumerate(row):
            text(s, xs[j], y, col_w[j], row_h - 4, v, size=15 if j == 0 else 16, bold=b,
                 align=PP_ALIGN.LEFT if j == 0 else PP_ALIGN.RIGHT,
                 color=MOSS if j == 0 or v != "—" else MUTED)
        y += row_h
        hline(s, x, y - 8, w)
    return y


def ranked_bars(s, x, y, w, rows, ref=1.0, vmax=None, unit="倍", row_h=38, cols=()):
    """横棒のランキング（LTV/CAC など基準線つき）。rows: [(名前, 値, [追加列の文字列...])]。
    値 >= ref の行はアクセント色＋太字、未満は薄い色＋赤字の数値。cols: 追加列の見出し。"""
    vmax = vmax or max(max(r[1] for r in rows) * 1.2, ref * 1.3)
    name_w, bar_w = 164, 190
    extra_w = (w - name_w - bar_w) / max(len(cols), 1)
    ty = y
    text(s, x, ty, name_w, 22, "項目", size=11, color=SECONDARY, bold=True)
    text(s, x + name_w, ty, bar_w, 22, "値", size=11, color=SECONDARY, bold=True)
    for j, c in enumerate(cols):
        text(s, x + name_w + bar_w + j * extra_w, ty, extra_w, 22, c, size=11, color=SECONDARY, bold=True, align=PP_ALIGN.RIGHT)
    hline(s, x, ty + 26, w, MOSS, 1.5)
    ry0 = ty + 32
    ref_x = x + name_w + bar_w * ref / vmax
    for i, (name, v, extra) in enumerate(rows):
        ry = ry0 + i * row_h
        ok = v >= ref
        text(s, x, ry, name_w - 4, row_h, name, size=13, bold=ok, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        bw = bar_w * min(v, vmax) / vmax
        rect(s, x + name_w, ry + 9, bw, row_h - 18, T.accent if ok else T.light)
        text(s, x + name_w + bw + 6, ry, 60, row_h, f"{v:.1f}{unit}", size=12, bold=True, color=MOSS if ok else STRONG,
             anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        for j, e in enumerate(extra):
            text(s, x + name_w + bar_w + j * extra_w, ry, extra_w, row_h, e, size=13, align=PP_ALIGN.RIGHT,
                 anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        hline(s, x, ry + row_h, w, BORDER_LIGHT, 0.75)
    vline(s, ref_x, ry0 - 4, row_h * len(rows) + 8, STRONG, 1.25, dash=True)
    return ry0 + row_h * len(rows)


def big_number(s, x, y, label, value, unit="", color=None, size=56, w=230):
    """大きな数字＋単位（KPIの見せ場）。label は上の小見出し。"""
    text(s, x, y, w, 22, label, size=13, color=SECONDARY, bold=True)
    tb = text(s, x, y + 22, w, 66, value, size=size, bold=True, color=color or MOSS, en=True, spacing=1.0, anchor=MSO_ANCHOR.BOTTOM)
    if unit:
        r = tb.text_frame.paragraphs[0].add_run()
        r.text = unit
        _set_font(r, int(size * 0.4), color or MOSS, True, en=False)
    return tb
