"""線画アイコン（黒線・白背景の PNG/WebP/JPG）を、余白を切って Moss / 白 / 灰の3色の透過 PNG にする。

    python3 trim_icon.py <入力画像> <出力ディレクトリ> <名前>
    → <出力>/icon_<名前>.png, icon_<名前>_white.png, icon_<名前>_gray.png

フロー図のノード（Deck.node）とタグ（Deck.tag）はこの3色セットを前提にしている。
"""
import sys
import numpy as np
from PIL import Image

src, out_dir, name = sys.argv[1:4]
im = Image.open(src).convert("L")
a = np.array(im).astype(float)
alpha = np.clip((235 - a) / (235 - 40), 0, 1)  # 黒線→不透明、白→透明
ys, xs = np.where(alpha > 0.3)
box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
for col, suffix in [((0x00, 0x43, 0x47), ""), ((0xFF, 0xFF, 0xFF), "_white"), ((0x62, 0x62, 0x62), "_gray")]:
    rgba = np.zeros((*a.shape, 4), dtype=np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = col
    rgba[..., 3] = (alpha * 255).astype(np.uint8)
    out = Image.fromarray(rgba, "RGBA").crop(box)
    w, h = out.size
    s = max(w, h)
    sq = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    sq.paste(out, ((s - w) // 2, (s - h) // 2))
    sq.thumbnail((400, 400))
    sq.save(f"{out_dir}/icon_{name}{suffix}.png")
print("saved", name, box)
