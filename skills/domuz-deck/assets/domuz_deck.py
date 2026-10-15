"""domuz_deck — Domuz デザインシステム v2.1「発表スライド」型の HTML デッキを組むための部品。

使い方（build_deck.py から）:

    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from domuz_deck import Deck

    d = Deck(title="資料タイトル", img_dir="images")
    d.cover(to="鳴海さん", title="イネイブラー事業・高付加価値3PL<br>現状共有とディスカッション",
            date="2026年10月15日（木）20:00〜｜オンライン")
    d.divider("01", "ENABLER BUSINESS", "イネイブラー事業の現状", "事業方針・計画・営業進捗")
    d.slide(title="本日のアジェンダ", sub="前半で現状を共有し、後半はディスカッション。",
            html=d.nlist([("1", "現状", "説明"), ("2", "計画", "説明")]))
    d.save("deck.html")        # deck.html と notes.md を書く

サイズは 4:3・1128×846px。文字は px で指定し、1スライドに収まるかは screenshots.js で必ず目視確認する。
PDF は render_pdf.js（Playwright）で同じ HTML から出力する。
"""
import base64
import html as _html
import os
import re

W, H = 1128, 846

# ---- デザイントークン（Domuz design system §2） ----
TOKENS = {
    "moss": "#004347",       # brand-primary / text-primary
    "light": "#00D79C",      # brand-secondary（強調・番号・ハイライト）
    "flower": "#EF667D",     # brand-flower（アンドフラワー・花の系列）
    "secondary": "#626262",  # text-secondary（サブタイトル・補足）
    "strong": "#E16464",     # text-strong（マイナス・警告）
    "muted": "#999999",      # text-muted（ページ番号など）
    "bg-gray": "#CBD0D3",    # 前年・比較対象・原価などの地味な棒
    "bg-gray2": "#9DA6A9",
    "bg-tint": "#F3F6F6",    # 薄い面（図の背景・カードの地）
    "border": "#C9CFCF",     # 罫線
    "watermark": "#ECEEEE",  # 表紙の透かし
    "white": "#FFFFFF",
}

FONT_LINK = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
             '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
             '<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;700'
             '&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">')

CSS = """
:root { %s }
* { box-sizing: border-box; margin: 0; padding: 0; }
html { background: #E9ECEC; }
body {
  font-family: "Outfit", "Zen Kaku Gothic New", "Hiragino Kaku Gothic ProN", "Noto Sans JP", sans-serif;
  color: var(--moss); -webkit-font-smoothing: antialiased; font-feature-settings: "palt";
}
.deck { display: flex; flex-direction: column; align-items: center; gap: 28px; padding: 28px 0; }
.slide { position: relative; width: 1128px; height: 846px; overflow: hidden; background: var(--white);
  box-shadow: 0 2px 14px rgba(0,0,0,.10); flex: none; }
.slide.content::before { content: ""; position: absolute; left: 0; top: 0; width: 8px; height: 100%%; background: var(--light); }
.slide.dark { background: var(--moss); color: var(--white); }
.slide .pageno { position: absolute; right: 40px; bottom: 20px; font-size: 14px; color: var(--muted); font-family: "Outfit", sans-serif; }
.slide .confidential { position: absolute; left: 56px; bottom: 20px; font-size: 12px; color: var(--muted); letter-spacing: 1px; font-family: "Outfit", sans-serif; }
.slide .title { position: absolute; left: 56px; top: 44px; width: 1016px; font-size: 38px; font-weight: 700; line-height: 1.3; }
.slide .sub { position: absolute; left: 56px; top: 100px; width: 1016px; font-size: 20px; color: var(--secondary); line-height: 1.5; }
.slide .foot { position: absolute; left: 56px; bottom: 44px; width: 1000px; font-size: 14px; color: var(--secondary); line-height: 1.5; }
.slide .body { position: absolute; left: 56px; top: 160px; width: 1016px; }
.bodywrap.long-sub { position: absolute; left: 0; top: 36px; width: 100%%; }
.slide .key { font-size: 28px; font-weight: 700; line-height: 1.5; }
.slide .center { position: absolute; left: 56px; top: 0; width: 1016px; height: 846px; display: flex; align-items: center; justify-content: center; text-align: center; }
.hl { color: var(--light); font-weight: 700; }
.en { font-family: "Outfit", sans-serif; }
.sec { color: var(--secondary); }
.num { font-family: "Outfit", sans-serif; font-weight: 700; color: var(--light); line-height: 1; }
p, li { line-height: 1.5; }

/* 表紙（P-1） */
.cover .wm { position: absolute; left: -20px; width: 1168px; text-align: center; font-size: 330px; font-weight: 700; line-height: .8; color: var(--watermark); font-family: "Outfit", sans-serif; letter-spacing: -.02em; }
.cover .brand { position: absolute; left: 72px; top: 96px; font-size: 28px; font-weight: 700; font-family: "Outfit", sans-serif; }
.cover .to { position: absolute; left: 72px; top: 190px; font-size: 26px; font-weight: 700; }
.cover .ttl { position: absolute; left: 72px; top: 246px; width: 1000px; font-size: 52px; font-weight: 700; line-height: 1.35; }
.cover .date { position: absolute; left: 72px; top: 432px; font-size: 22px; color: var(--secondary); letter-spacing: 2px; }
.cover .company { position: absolute; right: 72px; bottom: 72px; font-size: 24px; font-weight: 700; }

/* 章扉（P-3） */
.divider .no { position: absolute; left: 80px; top: 236px; font-size: 120px; font-weight: 700; line-height: 1; font-family: "Outfit", sans-serif; color: transparent; -webkit-text-stroke: 1.5px var(--white); }
.divider .en { position: absolute; left: 80px; top: 416px; font-size: 22px; letter-spacing: 6px; }
.divider .ttl { position: absolute; left: 80px; top: 460px; width: 900px; font-size: 46px; font-weight: 700; line-height: 1.3; }
.divider .sub { position: absolute; left: 80px; top: 544px; width: 900px; font-size: 22px; color: var(--white); line-height: 1.5; }

/* 番号付きリスト（P-11） */
.nlist { position: absolute; left: 96px; top: 176px; width: 936px; }
.nlist .row { display: flex; align-items: flex-start; gap: 36px; padding: 28px 0; border-bottom: 1px solid var(--border); }
.nlist .row:last-child { border-bottom: none; }
.nlist .n { font-size: 64px; width: 72px; flex: none; }
.nlist .lab { font-size: 36px; font-weight: 700; line-height: 1.3; padding-top: 6px; }
.nlist .desc { font-size: 20px; color: var(--secondary); margin-top: 10px; line-height: 1.5; }

/* カード・ブロック */
.cards { display: flex; gap: 20px; }
.card { flex: 1; border: 1.5px solid var(--moss); padding: 20px 22px; }
.card.fill { background: var(--moss); color: var(--white); border-color: var(--moss); }
.card.tint { background: var(--bg-tint); border: none; }
.card h4 { font-size: 22px; font-weight: 700; line-height: 1.35; }
.card p { font-size: 17px; margin-top: 10px; line-height: 1.6; }
.card.fill p { color: var(--white); }
.circ { display: inline-flex; width: 28px; height: 28px; border-radius: 50%%; background: var(--light); color: var(--white); font-family: "Outfit", sans-serif; font-size: 16px; font-weight: 700; align-items: center; justify-content: center; margin-right: 8px; vertical-align: 3px; }
.label { font-size: 16px; font-weight: 700; color: var(--light); letter-spacing: 2px; font-family: "Outfit", sans-serif; }
.h3 { font-size: 24px; font-weight: 700; line-height: 1.35; }
.bar4 { display: inline-block; width: 48px; height: 4px; background: var(--light); margin: 10px 0 14px; }
.hr { height: 1px; background: var(--border); }

/* 表 */
table.dt { border-collapse: collapse; width: 100%%; }
table.dt th { font-size: 16px; font-weight: 700; color: var(--secondary); text-align: left; padding: 8px 10px; border-bottom: 2px solid var(--moss); white-space: nowrap; }
table.dt td { font-size: 18px; padding: 10px 10px; border-bottom: 1px solid var(--border); vertical-align: middle; line-height: 1.45; }
table.dt .r { text-align: right; font-family: "Outfit", sans-serif; font-variant-numeric: tabular-nums; }
table.dt .r .pct { font-size: 14px; color: var(--secondary); margin-left: 3px; font-family: "Zen Kaku Gothic New", sans-serif; }
table.dt td.strong { font-weight: 700; color: var(--light); }
table.dt tr.total td { font-weight: 700; }
.pill { display: inline-block; font-size: 14px; font-weight: 700; padding: 3px 12px; border-radius: 999px; white-space: nowrap; line-height: 1.4; }
.pill.done { background: var(--light); color: var(--white); }
.pill.plan { border: 1.5px solid var(--moss); color: var(--moss); }
.pill.todo { background: var(--bg-gray); color: var(--moss); }

/* KPI（P-6） */
.kpi .lab { font-size: 20px; color: var(--secondary); }
.kpi .val { font-size: 72px; font-weight: 700; line-height: 1.1; font-family: "Outfit", sans-serif; }
.kpi .val .unit { font-size: 26px; font-family: "Zen Kaku Gothic New", sans-serif; margin-left: 4px; }
.kpi .val .jp { font-family: "Zen Kaku Gothic New", sans-serif; }

@media screen { .deck { transform-origin: top center; } }
@media print {
  html, body { background: var(--white); }
  .deck { display: block; padding: 0; gap: 0; transform: none !important; }
  .slide { box-shadow: none; page-break-after: always; break-after: page; }
  .slide:last-child { page-break-after: auto; break-after: auto; }
}
@page { size: 1128px 846px; margin: 0; }
""" % " ".join(f"--{k}: {v};" for k, v in TOKENS.items())

SCRIPT = """
(function () {
  function fit() {
    var deck = document.querySelector('.deck');
    var s = Math.min(1, (window.innerWidth - 24) / 1128);
    deck.style.transform = 'scale(' + s + ')';
    deck.style.marginBottom = ((s - 1) * deck.getBoundingClientRect().height / s) + 'px';
  }
  window.addEventListener('resize', fit);
  fit();
})();
"""


def md(s):
    """[[語]] はライトグリーン太字、**語** は太字。本文の強調はこの2つだけにする。"""
    s = re.sub(r"\[\[(.+?)\]\]", r'<span class="hl">\1</span>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return s


def esc(s):
    return _html.escape(str(s), quote=False)


class Deck:
    def __init__(self, title, img_dir="images", confidential=True, company="株式会社Domuz"):
        self.title = title
        self.img_dir = img_dir
        self.confidential = confidential
        self.company = company
        self.slides = []
        self.notes = []
        self.page_no = 0

    # ---- 画像 ----
    def img(self, name):
        """images/ の画像を data URI にして埋め込む（HTML を1ファイルで渡せるように）。"""
        path = name if os.path.isabs(name) else os.path.join(self.img_dir, name)
        ext = os.path.splitext(path)[1].lower()
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "svg": "image/svg+xml",
                "webp": "image/webp"}[ext.lstrip(".")]
        with open(path, "rb") as f:
            return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"

    # ---- スライド ----
    def slide(self, html, title=None, sub=None, foot=None, notes=None, cls="content", number=True):
        """白背景の内容スライド。title 38px / sub 20px / foot 14px。html は .body から始めるのが基本。
        sub が約50字を超えて2行になるときは本文を 36px 下げる（タイトルと重ならないように）。"""
        self.page_no += 1
        parts = [f'<section class="slide {cls}" id="s{self.page_no}">']
        if title:
            parts.append(f'<div class="title">{md(title)}</div>')
        if sub:
            parts.append(f'<div class="sub">{md(sub)}</div>')
        long_sub = bool(sub) and len(re.sub(r"<.*?>", "", sub)) > 50
        parts.append(f'<div class="bodywrap{" long-sub" if long_sub else ""}">{md(html)}</div>')
        if foot:
            parts.append(f'<div class="foot">{md(foot)}</div>')
        if number and cls == "content":
            if self.confidential:
                parts.append('<div class="confidential">Domuz inc.<span style="margin-left:14px">Confidential</span></div>')
            parts.append(f'<div class="pageno">{self.page_no}</div>')
        parts.append("</section>")
        self.slides.append("\n".join(parts))
        if notes:
            self.notes.append((self.page_no, notes.strip()))
        return self

    def cover(self, title, to=None, date=None, notes=None, brand="Domuz"):
        """P-1 表紙: 極太「Domuz」の透かし3段＋左寄せのタイトル。宛名（to）は外部向けのときだけ。"""
        h = ('<div class="wm" style="top:-40px">Domuz</div><div class="wm" style="top:242px">Domuz</div>'
             '<div class="wm" style="top:524px">Domuz</div>'
             f'<div class="brand">{brand}</div>')
        if to:
            h += f'<div class="to">{to}</div>'
        h += f'<div class="ttl">{title}</div>'
        if date:
            h += f'<div class="date">{date}</div>'
        h += f'<div class="company">{self.company}</div>'
        return self.slide(h, cls="cover", notes=notes)

    def divider(self, num, en, title, sub="", notes=None):
        """P-3 章扉: Moss 全面＋白アウトラインの章番号＋英字ラベル（ALL CAPS）＋和文タイトル。ページ番号は出さない。"""
        h = (f'<div class="no">{num}</div><div class="en">{en}</div>'
             f'<div class="ttl">{title}</div><div class="sub">{sub}</div>')
        return self.slide(h, cls="dark divider", notes=notes)

    def message(self, text, size=56, notes=None):
        """P-2 主張文: 白背景の中央に太字1〜2行だけ。章の切り替えや「言いたいことはこれ」に使う。"""
        return self.slide(f'<div class="center"><div style="font-size:{size}px;font-weight:700;line-height:1.4">{md(text)}</div></div>',
                          notes=notes)

    # ---- 部品（戻り値は HTML 文字列。slide() の html に組み込む） ----
    @staticmethod
    def nlist(items, top=176, num_size=64, lab_size=36, desc_size=20):
        """P-11 番号付きリスト: (番号, 見出し, 説明 or 説明のリスト)。アジェンダ・論点・3つの理由など。"""
        rows = ""
        for n, lab, desc in items:
            descs = desc if isinstance(desc, (list, tuple)) else [desc]
            rows += (f'<div class="row"><div class="n num" style="font-size:{num_size}px">{n}</div><div>'
                     f'<div class="lab" style="font-size:{lab_size}px">{md(lab)}</div>'
                     + "".join(f'<div class="desc" style="font-size:{desc_size}px">{md(x)}</div>' for x in descs if x)
                     + '</div></div>')
        return f'<div class="nlist" style="top:{top}px">{rows}</div>'

    @staticmethod
    def cards(items, numbered=True, kind=""):
        """横並びカード: (見出し, 本文)。numbered=True なら 01/02/03 をライトグリーンで添える。kind は "" / "fill" / "tint"。"""
        out = ""
        for i, (h, b) in enumerate(items):
            n = f'<div class="num" style="font-size:40px">0{i + 1}</div>' if numbered else ""
            out += f'<div class="card {kind}">{n}<h4 style="margin-top:{12 if numbered else 0}px">{md(h)}</h4><p class="sec">{md(b)}</p></div>'
        return f'<div class="cards">{out}</div>'

    @staticmethod
    def table(headers, rows, aligns=None, strong_col=None, font=18):
        """データ表。headers は列名、rows は各行のセル（文字列 or (文字列, "r") など）。
        aligns: 列ごとに "l"/"r"/"c"。右寄せ列は Outfit の等幅数字。"X（29%）" 形式の値は括弧内を小さく灰色にする。"""
        aligns = aligns or ["l"] + ["r"] * (len(headers) - 1)
        amap = {"l": "left", "r": "right", "c": "center"}

        def cell(v):
            m = re.match(r"(.+?)（(.+?)）$", str(v))
            return f'{m.group(1)}<span class="pct">({m.group(2)})</span>' if m else md(str(v))

        th = "".join(f'<th style="text-align:{amap[a]}">{h}</th>' for h, a in zip(headers, aligns))
        trs = ""
        for row in rows:
            cls = ""
            if isinstance(row, dict):
                cls, row = row.get("cls", ""), row["cells"]
            tds = ""
            for j, (v, a) in enumerate(zip(row, aligns)):
                c = ("r" if a == "r" else "") + (" strong" if strong_col == j else "")
                tds += f'<td class="{c}" style="text-align:{amap[a]};font-size:{font}px">{cell(v)}</td>'
            trs += f'<tr class="{cls}">{tds}</tr>'
        return f'<table class="dt"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>'

    @staticmethod
    def pill(text, kind="todo"):
        """ステータス: done（ライトグリーン塗り）/ plan（Moss 枠）/ todo（灰色）。"""
        return f'<span class="pill {kind}">{text}</span>'

    @staticmethod
    def kpi(label, value, unit="", prefix=""):
        """P-6 主要数字: ラベル20px＋数字72px（Outfit）＋単位。prefix は「約」など和文の接頭。"""
        pre = f'<span class="jp" style="font-size:40px">{prefix}</span>' if prefix else ""
        return (f'<div class="kpi"><div class="lab">{label}</div>'
                f'<div class="val">{pre}{value}<span class="unit">{unit}</span></div></div>')

    @staticmethod
    def hbar(label, total, segs, y, scale, h=64, x0=0, note=""):
        """横の積み上げ棒（利益の構造・内訳）。segs: (名前, 値, 塗り, 文字色[, 枠線色])。
        scale は px/単位。複数の棒を同じ scale で描くと量が比べられる。狭い区画のラベルは棒の下に出す。
        戻り値は position:absolute の要素群なので、高さを持った親 .body の中に置く。"""
        out = [f'<div style="position:absolute;left:{x0}px;top:{y}px;font-size:18px;font-weight:700">{label}'
               f'<span class="sec" style="font-size:14px;font-weight:400;margin-left:10px">{note}</span></div>']
        x = x0
        for name, val, col, fg, *bd in segs:
            w = val * scale
            border = f"border:1.5px solid {bd[0]};" if bd else ""
            lab = (f'<div style="font-size:14px;font-weight:700;white-space:nowrap">{name}</div>'
                   f'<div class="en" style="font-size:21px;font-weight:700;margin-top:1px;white-space:nowrap">{val:,}'
                   f'<span style="font-size:12px;font-weight:400;margin-left:3px">円 ({round(val / total * 100)}%)</span></div>')
            out.append(f'<div style="position:absolute;left:{x}px;top:{y + 32}px;width:{w - 3}px;height:{h}px;background:{col};{border}'
                       f'display:flex;flex-direction:column;justify-content:center;align-items:center;color:{fg}">'
                       + (lab if w >= 150 else "") + '</div>')
            if w < 150:
                line = col if col not in ("var(--white)", "#fff", "#FFFFFF") else (bd[0] if bd else "var(--moss)")
                out.append(f'<div style="position:absolute;left:{x}px;top:{y + 32 + h + 8}px;width:150px;color:var(--moss);'
                           f'border-left:2px solid {line};padding-left:8px">{lab}</div>')
            x += w
        return "".join(out)

    @staticmethod
    def vbars(labels, values, base_y=600, max_h=330, x0=432, bw=40, gap=14, highlight="max", unit_fmt="{:.0f}"):
        """縦棒グラフ（月次推移など）。最大値だけライトグリーン（highlight="max"）、他は Moss。"""
        top = max(values)
        out = []
        for i, (lab, v) in enumerate(zip(labels, values)):
            x = x0 + i * (bw + gap)
            h = max_h * v / top
            col = "var(--light)" if (highlight == "max" and v == top) or highlight == i else "var(--moss)"
            out.append(f'<div style="position:absolute;left:{x}px;top:{base_y - h}px;width:{bw}px;height:{h}px;background:{col}"></div>')
            out.append(f'<div class="en" style="position:absolute;left:{x - 10}px;top:{base_y - h - 26}px;width:{bw + 20}px;text-align:center;font-size:15px;font-weight:700">{unit_fmt.format(v)}</div>')
            out.append(f'<div class="sec" style="position:absolute;left:{x - 10}px;top:{base_y + 8}px;width:{bw + 20}px;text-align:center;font-size:15px">{lab}</div>')
        out.append(f'<div style="position:absolute;left:{x0 - 8}px;top:{base_y}px;width:{len(values) * (bw + gap)}px;height:1px;background:var(--border)"></div>')
        return "".join(out)

    @staticmethod
    def photo_grid(items, img, cols=2, w=496, ih=186, iw=150):
        """写真＋見出し＋値＋説明の一覧（商品ラインナップなど）。items: (画像名, 見出し, 値, 単位, 説明)。"""
        cells = ""
        for f, name, val, unit, desc in items:
            cells += (f'<div style="display:flex;gap:16px;width:{w}px;align-items:center">'
                      f'<img src="{img(f)}" style="width:{iw}px;height:{ih}px;object-fit:cover;flex:none;display:block">'
                      f'<div><div style="font-size:19px;font-weight:700;line-height:1.3">{name}</div>'
                      f'<div style="margin-top:6px"><span class="en" style="font-size:30px;font-weight:700;line-height:1">{val}</span>'
                      f'<span style="font-size:15px;color:var(--secondary);margin-left:4px">{unit}</span></div>'
                      f'<p class="sec" style="font-size:14px;margin-top:6px">{desc}</p></div></div>')
        return f'<div style="display:flex;flex-wrap:wrap;gap:16px 24px">{cells}</div>'

    # ---- フロー図（アイコン） ----
    def icons(self, icon_dir):
        """assets/icons のアイコン（box / warehouse / bouquet / person、moss・white・gray）を読み込む。"""
        self._icon = {}
        for k in ("box", "warehouse", "bouquet", "person"):
            for suf in ("", "_white", "_gray"):
                p = os.path.join(icon_dir, f"icon_{k}{suf}.png")
                if os.path.exists(p):
                    self._icon[k + suf] = self.img(p)
        return self

    def node(self, x, y, icon, label, kind="plain", r=40):
        """フロー図のノード: 丸＋アイコン＋ラベル。kind="moss" は自社（塗り）、"plain" は相手先（白＋Moss 枠）。"""
        if kind == "moss":
            bg = f'<circle cx="{x}" cy="{y}" r="{r}" fill="var(--moss)"/>'
            im = f'<image href="{self._icon[icon + "_white"]}" x="{x - 24}" y="{y - 24}" width="48" height="48"/>'
        else:
            bg = f'<circle cx="{x}" cy="{y}" r="{r}" fill="var(--white)" stroke="var(--moss)" stroke-width="1.5"/>'
            im = f'<image href="{self._icon[icon]}" x="{x - 24}" y="{y - 24}" width="48" height="48"/>'
        return bg + im + f'<text x="{x}" y="{y + r + 20}" text-anchor="middle" font-size="15" font-weight="700" fill="var(--moss)">{label}</text>'

    def tag(self, x, y, icons, label):
        """矢印に添える「何が動くか」: 小アイコン＋ラベルの白いピル。横矢印なら矢印の上（y-38）に置く。"""
        w = len(icons) * 30 + 10 + 15 * len(label) + 10
        out = [f'<rect x="{x - w / 2}" y="{y - 18}" width="{w}" height="36" rx="18" fill="var(--white)" stroke="var(--border)" stroke-width="1"/>']
        ix = x - w / 2 + 8
        for ic in icons:
            out.append(f'<image href="{self._icon[ic]}" x="{ix}" y="{y - 13}" width="26" height="26"/>')
            ix += 30
        out.append(f'<text x="{ix + 4}" y="{y + 5}" font-size="14" font-weight="700" fill="var(--moss)">{label}</text>')
        return "".join(out)

    @staticmethod
    def arrow(x1, y1, x2, y2, bend=None):
        st = 'fill="none" stroke="var(--moss)" stroke-width="2" marker-end="url(#ah)"'
        if bend:
            return f'<polyline points="{x1},{y1} {bend[0]},{bend[1]} {x2},{y2}" {st}/>'
        return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" {st}/>'

    @staticmethod
    def svg(body, w=320, h=330):
        defs = ('<defs><marker id="ah" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
                '<path d="M0,0 L8,4 L0,8 z" fill="var(--moss)"/></marker></defs>')
        return f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}">{defs}{body}</svg>'

    # ---- 書き出し ----
    def save(self, out="deck.html", notes_md="notes.md"):
        html = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(self.title)}</title>
{FONT_LINK}
<style>{CSS}</style>
</head>
<body>
<div class="deck">
{chr(10).join(self.slides)}
</div>
<script>{SCRIPT}</script>
</body>
</html>
"""
        with open(out, "w") as f:
            f.write(html)
        if notes_md:
            with open(notes_md, "w") as f:
                f.write(f"# {self.title} — 発表者ノート（スライド番号つき）\n\n")
                for n, body in self.notes:
                    f.write(f"## {n}\n\n{body}\n\n")
        print("saved", out, "slides:", len(self.slides))
        return out
