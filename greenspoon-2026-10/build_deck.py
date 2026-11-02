"""GREEN SPOON 様向け オフィスグリーンレンタル ご提案資料（2026.10、1ページ）— Domuz「発表スライド」型で .pptx を生成する。

    python3 build_deck.py                      # out/greenspoon_green_rental.pptx
    bash render.sh out/greenspoon_green_rental.pptx "オフィスグリーンレンタルのご提案" "2026.10 株式会社Domuz"

数字の出所:
- レンタル費: 2026-10-30 小松さんが #sales で共有した料金表（Table 750 / S 1,500 / M 2,250 / L 3,750 / XL 5,250）。
  ギフティ向け概要資料（2026-08-06）と同額で、同資料では「月額・税抜」として掲載。
- 高さの目安: ギフティ向け概要資料 P7 のサイズ一覧。
- サービス内容: 2026-08-08 ギフティ向け提案メッセージ（週1目安の訪問ケア、枯れたら無料で同等品と交換、手乗り〜2m）と概要資料 P8。
写真: photos/sizes/*.jpg（概要資料 P7 のサイズ写真）。表紙と事例写真のページは 2026-11-02 の指示で外した。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from deck_lib import *  # noqa: E402,F401
from PIL import Image, ImageOps  # noqa: E402

use_theme("domuz")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "out", "greenspoon_green_rental.pptx")
PHOTO = os.path.join(HERE, "photos")

# ---- データ（円・月額・税抜） ----
CLIENT = "GREEN SPOON"
PRICES = [  # (サイズ, 高さの目安, 月額レンタル費, 写真)
    ("Table", "15 〜 45cm", 750, "table.jpg"),
    ("S", "45 〜 85cm", 1500, "s.jpg"),
    ("M", "85 〜 120cm", 2250, "m.jpg"),
    ("L", "120 〜 160cm", 3750, "l.jpg"),
    ("XL", "160cm 〜 2m", 5250, "xl.jpg"),
]
VISIT = "月2〜3回"  # 訪問頻度の目安（2026-10-30 髙木さん指示。ギフティ向けは週1目安だった）


def yen_(v):
    return f"¥{v:,}"


# ---- 写真 ----
def _small(path, longest=1600):
    """容量を抑えるため長辺 longest px に縮小したコピーを使う。"""
    cache = os.path.join(PHOTO, ".cache")
    os.makedirs(cache, exist_ok=True)
    small = os.path.join(cache, os.path.splitext(os.path.basename(path))[0] + f"_{longest}.jpg")
    if not os.path.exists(small):
        with Image.open(path) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            im.thumbnail((longest, longest))
            im.save(small, quality=85)
    return small


def picture_cover(slide, path, x, y, w, h):
    """枠 (x, y, w, h) を写真で埋める（はみ出す分は中央で切る）。"""
    path = _small(path)
    with Image.open(path) as im:
        iw, ih = im.size
    pic = slide.shapes.add_picture(path, px(x), px(y), px(w), px(h))
    k = max(w / iw, h / ih)
    pw, ph = iw * k, ih * k
    # crop は元画像に対する割合
    cx = (pw - w) / 2 / pw
    cy = (ph - h) / 2 / ph
    pic.crop_left = pic.crop_right = cx
    pic.crop_top = pic.crop_bottom = cy
    return pic


def picture_contain(slide, path, x, y, w, h):
    """枠の中に写真を収める（中央寄せ）。"""
    path = _small(path, 800)
    with Image.open(path) as im:
        iw, ih = im.size
    k = min(w / iw, h / ih)
    pw, ph = iw * k, ih * k
    return slide.shapes.add_picture(path, px(x + (w - pw) / 2), px(y + (h - ph) / 2), px(pw), px(ph))


# =====================================================================
# 1ページ構成: 料金・サービス内容・ご契約にあたってのご案内
# =====================================================================
s = content_slide("オフィスグリーンレンタル　料金とサービス内容")
message(s, f"月額のレンタル費に、{VISIT}目安の訪問ケアと、枯れた場合の交換を含みます")

# 左: サイズ別の料金表（写真つき）
x, w = MARGIN, 500
TOP = 156
rect(s, x, TOP, w, 6, T.accent)
text(s, x, TOP + 20, w, 32, "サイズ別の月額レンタル費", size=20, bold=True)
cols = [("", 84), ("サイズ", 110), ("高さの目安", 172), ("月額レンタル費", 134)]
cx = [x]
for _, cw in cols[:-1]:
    cx.append(cx[-1] + cw)
ty = TOP + 60
for j, (hd, cw) in enumerate(cols):
    text(s, cx[j], ty, cw, 24, hd, size=13, color=SECONDARY, bold=True,
         align=PP_ALIGN.RIGHT if j == 3 else PP_ALIGN.LEFT)
hline(s, x, ty + 28, w, MOSS, 1.5)
ry = ty + 34
row_h = 64
for size_, height_, price_, photo_ in PRICES:
    picture_contain(s, os.path.join(PHOTO, "sizes", photo_), cx[0] + 4, ry + 5, 64, row_h - 10)
    text(s, cx[1], ry, cols[1][1], row_h, size_, size=21, bold=True, en=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, cx[2], ry, cols[2][1], row_h, height_, size=15, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, cx[3], ry, cols[3][1], row_h, yen_(price_), size=21, bold=True, en=True, align=PP_ALIGN.RIGHT,
         anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    ry += row_h
    hline(s, x, ry - 1, w)
text(s, x, ry + 6, w, 22, "※ 税抜・1鉢あたりの月額", size=12, color=SECONDARY)
BOTTOM = ry + 30  # 左右の段の下端

# 右: サービスに含まれるもの
x2, w2 = 596, 476
vline(s, 576, TOP, BOTTOM - TOP)
rect(s, x2, TOP, w2, 6, MOSS)
text(s, x2, TOP + 20, w2, 32, "レンタル費に含まれるサービス", size=20, bold=True)
items = [
    (f"{VISIT}目安の訪問ケア",
     "弊社スタッフが訪問し、水やり・施肥・剪定・葉の清掃・病害虫予防まで行います。"
     "御社での水やりなどの作業は不要です。"),
    ("枯れた場合は無料で交換",
     "生育に問題が生じた植物は、同等品と無料で交換します。常に良い状態のグリーンを保ちます。"),
    ("プランニングから設置まで",
     "手乗りサイズから高さ約2mまで対応。現地を拝見し、環境・テイスト・ご予算に合わせて"
     "植物と鉢をご提案し、納品・設置まで弊社スタッフが行います。"),
]
y = TOP + 64
for i, (head, body) in enumerate(items, 1):
    badge(s, x2 + 13, y + 15, str(i), d=26)  # 中心座標で指定
    text(s, x2 + 40, y, w2 - 40, 30, head, size=18, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, x2 + 40, y + 34, w2 - 40, 70, body, size=14, color=SECONDARY, spacing=1.4)
    y += 118

# 下段: ご契約にあたってのご案内（全幅）
ny = BOTTOM + 28
notes_ = [
    f"水やりや日々のお手入れは、弊社スタッフが{VISIT}目安で訪問して行います。御社での作業はありません。",
    "枯れたり状態が悪くなったりした場合は、同等の植物と無料で交換します。",
    "植物は生きものなので、樹形や葉の様子は時期により変わります。写真はイメージです。",
    "訪問の曜日・時間帯と入館の方法は、ご契約時にすり合わせさせてください。",
    "最低契約期間・最低鉢数・初回の設置費は、設置数とフロア構成を伺ったうえでご相談させてください。",
]
step = 25
rect(s, MARGIN, ny, 6, 30 + step * len(notes_), T.accent)
text(s, MARGIN + 24, ny - 4, 400, 30, "ご契約にあたってのご案内", size=18, bold=True)
yy = ny + 32
for n_ in notes_:
    rect(s, MARGIN + 28, yy + 9, 7, 7, T.accent)
    text(s, MARGIN + 44, yy, 960, 26, n_, size=14, spacing=1.3)
    yy += step

os.makedirs(os.path.dirname(OUT), exist_ok=True)
save(OUT)
