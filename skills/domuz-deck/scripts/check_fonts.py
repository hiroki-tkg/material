"""PDF に埋め込まれたフォントを確認する。Outfit / Zen Kaku Gothic New 以外（WenQuanYi 等の代替）が
出ているページと、その原因になりうる記号を表示する。全角スペース（U+3000）は見た目に影響しない。

    python3 check_fonts.py deck.pdf
"""
import sys
from pypdf import PdfReader

r = PdfReader(sys.argv[1])
print("pages", len(r.pages))
bad = False
for i, p in enumerate(r.pages):
    fs = [str(v.get_object().get("/BaseFont")) for k, v in p.get("/Resources", {}).get("/Font", {}).items()]
    others = sorted({f.split("+")[-1] for f in fs if "Outfit" not in f and "ZenKaku" not in f and f != "None"})
    if others:
        bad = True
        t = p.extract_text()
        sym = sorted({c for c in t if not ("぀" <= c <= "鿿") and not c.isascii() and c not in "。、・（）「」："})
        print(f"page {i + 1}: fallback {others} symbols {sym}")
print("OK: all fonts are Outfit / Zen Kaku Gothic New" if not bad else "fallback fonts found (usually harmless symbols)")
