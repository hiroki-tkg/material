"""GREEN SPOON 様向け オフィスグリーンレンタル ご提案資料（2026.10）— Domuz「発表スライド」型で .pptx を生成する。

    python3 build_deck.py                      # out/greenspoon_green_rental.pptx
    bash render.sh out/greenspoon_green_rental.pptx "オフィスグリーンレンタルのご提案" "2026.10 株式会社Domuz"

数字の出所:
- レンタル費: 2026-10-30 小松さんが #sales で共有した料金表（Table 750 / S 1,500 / M 2,250 / L 3,750 / XL 5,250）。
  ギフティ向け概要資料（2026-08-06）と同額で、同資料では「月額・税抜」として掲載。
- 高さの目安: ギフティ向け概要資料 P7 のサイズ一覧。
- サービス内容: 2026-08-08 ギフティ向け提案メッセージ（週1目安の訪問ケア、枯れたら無料で同等品と交換、手乗り〜2m）と概要資料 P8。
写真: photos/01_livinghouse.jpg（LIVING HOUSE）、photos/02_kanademono.jpg（KANADEMONO、右端の人物をトリミング）、
      photos/sizes/*.jpg（概要資料 P7 のサイズ写真）。
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
VISIT = "週1回"  # 訪問頻度の目安


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
# 1. 表紙（Domuz の透かし＋タイトル。合宿資料と同じ型）
# =====================================================================
s = new_slide()
for row in range(3):
    # 幅は Montserrat Bold の "Domuz" が1行に収まるように広めに取る（折り返すと "z" が次の行に落ちる）
    text(s, -200, -30 + row * 282, W_PX + 400, 300, "Domuz", size=300, color=WATERMARK, bold=True,
         en=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=0.8)
rect(s, 0, 0, 8, H_PX, T.accent)
text(s, 96, 226, 960, 40, f"{CLIENT} 様　ご提案資料", size=26, color=SECONDARY)
text(s, 96, 290, 1000, 180, ["オフィスグリーンレンタルの", "ご提案"], size=56, bold=True, spacing=1.3)
text(s, 96, 486, 960, 40, "月額のレンタル費に、植物の訪問ケアと交換を含めてご提供します", size=22, color=SECONDARY)
text(s, 96, 640, 900, 120, ["2026年10月", "株式会社Domuz"], size=22, color=SECONDARY, spacing=1.5)

# =====================================================================
# 2. 料金とサービス内容
# =====================================================================
s = content_slide("料金とサービス内容")
message(s, f"月額のレンタル費に、{VISIT}目安の訪問ケアと、枯れた場合の交換を含みます")

# 左: サイズ別の料金表（写真つき）
x, w = MARGIN, 500
rect(s, x, 160, w, 6, T.accent)
text(s, x, 182, w, 34, "サイズ別の月額レンタル費", size=21, bold=True)
cols = [("", 96), ("サイズ", 110), ("高さの目安", 160), ("月額レンタル費", 134)]
cx = [x]
for _, cw in cols[:-1]:
    cx.append(cx[-1] + cw)
ty = 232
for j, (hd, cw) in enumerate(cols):
    text(s, cx[j], ty, cw, 24, hd, size=14, color=SECONDARY, bold=True,
         align=PP_ALIGN.RIGHT if j == 3 else PP_ALIGN.LEFT)
hline(s, x, ty + 30, w, MOSS, 1.5)
ry = ty + 38
row_h = 82
for size_, height_, price_, photo_ in PRICES:
    picture_contain(s, os.path.join(PHOTO, "sizes", photo_), cx[0] + 6, ry + 6, 72, row_h - 12)
    text(s, cx[1], ry, cols[1][1], row_h, size_, size=22, bold=True, en=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, cx[2], ry, cols[2][1], row_h, height_, size=16, color=SECONDARY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, cx[3], ry, cols[3][1], row_h, yen_(price_), size=22, bold=True, en=True, align=PP_ALIGN.RIGHT,
         anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    ry += row_h
    hline(s, x, ry - 1, w)
text(s, x, ry + 8, w, 24, "※ 税抜・1鉢あたりの月額", size=13, color=SECONDARY)

# 右: サービスに含まれるもの
x2, w2 = 596, 476
vline(s, 576, 160, 560)
rect(s, x2, 160, w2, 6, MOSS)
text(s, x2, 182, w2, 34, "レンタル費に含まれるサービス", size=21, bold=True)
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
y = 236
for i, (head, body) in enumerate(items, 1):
    badge(s, x2 + 14, y + 17, str(i), d=28)  # 中心座標で指定
    text(s, x2 + 42, y, w2 - 42, 34, head, size=20, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, x2 + 42, y + 40, w2 - 42, 80, body, size=15, color=SECONDARY, spacing=1.4)
    y += 150
footnote(s, "※ 最低契約期間・最低鉢数・初回の設置費は、設置数とフロア構成を伺ったうえでご相談させてください")

# =====================================================================
# 3. 設置事例と注意事項
# =====================================================================
s = content_slide("設置事例とご契約にあたってのご案内")
message(s, "店舗・オフィスの空間に合わせてコーディネートした事例です")
py, ph = 160, 380
gap = 16
lw = 620
picture_cover(s, os.path.join(PHOTO, "01_livinghouse.jpg"), MARGIN, py, lw, ph)
picture_cover(s, os.path.join(PHOTO, "02_kanademono.jpg"), MARGIN + lw + gap, py, CONTENT_W - lw - gap, ph)
text(s, MARGIN, py + ph + 8, lw, 22, "LIVING HOUSE 様（ショールーム）", size=13, color=SECONDARY)
text(s, MARGIN + lw + gap, py + ph + 8, CONTENT_W - lw - gap, 22, "KANADEMONO 様（店舗）", size=13, color=SECONDARY)

ny = 600
rect(s, MARGIN, ny, 6, 150, T.accent)
text(s, MARGIN + 24, ny - 4, 400, 30, "ご契約にあたってのご案内", size=19, bold=True)
notes_ = [
    f"水やりや日々のお手入れは、弊社スタッフが{VISIT}目安で訪問して行います。御社での作業はありません。",
    "枯れたり状態が悪くなったりした場合は、同等の植物と無料で交換します。",
    "植物は生きものなので、樹形や葉の様子は時期により変わります。写真はイメージです。",
    "訪問の曜日・時間帯と入館の方法は、ご契約時にすり合わせさせてください。",
]
yy = ny + 36
for n_ in notes_:
    rect(s, MARGIN + 28, yy + 10, 8, 8, T.accent)
    text(s, MARGIN + 46, yy, 960, 28, n_, size=15, spacing=1.3)
    yy += 30

os.makedirs(os.path.dirname(OUT), exist_ok=True)
save(OUT)
