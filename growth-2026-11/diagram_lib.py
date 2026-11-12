"""図解ページ用の小さな部品（矢印・箱・チップ）。deck_lib の上に載せて使う。"""
from deck_lib import *  # noqa: F401,F403
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR


def _head(s, cx, cy, rot, color, d=10):
    tri = rect(s, cx - d / 2, cy - d / 2, d, d, color, shape=MSO_SHAPE.ISOSCELES_TRIANGLE)
    tri.rotation = rot


def arrow_h(s, x1, x2, y, color, weight=1.5, dash=False):
    """横向きの矢印。x1 → x2 の向きに先端を付ける。"""
    hline(s, min(x1, x2), y, abs(x2 - x1) - 4, color, weight, dash=dash)
    _head(s, x2 - 5 if x2 > x1 else x2 + 5, y, 90 if x2 > x1 else 270, color)


def arrow_v(s, x, y1, y2, color, weight=1.5, dash=False):
    """縦向きの矢印。y1 → y2 の向きに先端を付ける。"""
    vline(s, x, min(y1, y2) + (0 if y2 > y1 else 4), abs(y2 - y1) - 4, color, weight, dash=dash)
    _head(s, x, y2 - 5 if y2 > y1 else y2 + 5, 180 if y2 > y1 else 0, color)


def box(s, x, y, w, h, line, fill=WHITE, weight=1.5, dash=False):
    return rect(s, x, y, w, h, fill, line=line, weight=weight, dash=dash)


def chip(s, x, y, w, h, body, size=12, fill=WHITE, line=BORDER_LIGHT, bold=False, color=MOSS, band=None,
         align=None):
    rect(s, x, y, w, h, fill, line=line, weight=1.0)
    if band:
        rect(s, x, y, w, 3, band)
    kw = {"align": align} if align is not None else {}
    text(s, x + 8, y, w - 16, h, body, size=size, color=color, bold=bold, anchor=MSO_ANCHOR.MIDDLE, spacing=1.3, **kw)
