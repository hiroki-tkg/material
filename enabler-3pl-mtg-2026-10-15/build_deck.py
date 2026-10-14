"""鳴海さんMTG 2026.10.15「イネイブラー事業・高付加価値3PL 現状共有とディスカッション」
— Domuz デザインシステム v2.1「発表スライド」型で deck.html を生成する。

元資料: Keynote（鳴海さんMTG_20261015）。文言・数値はそのまま、デザインだけ Domuz 標準に揃える。
サイズは 4:3・1128×846px。PDF は render_pdf.js（Playwright）で同じ HTML から出力する。

    python3 build_deck.py            # deck.html を書き出す
    node render_pdf.js               # deck.html → deck.pdf
"""
import base64
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "images")
W, H = 1128, 846

# ---- デザイントークン（design-system/domuz_design_system.md §2） ----
CSS = """
:root {
  --moss: #004347;        /* --brand-primary / --text-primary */
  --light: #00D79C;       /* --brand-secondary */
  --flower: #EF667D;      /* --brand-flower */
  --secondary: #626262;   /* --text-secondary */
  --strong: #E16464;      /* --text-strong */
  --muted: #999999;       /* --text-muted */
  --bg-gray: #CBD0D3;     /* --bg-gray */
  --bg-gray2: #9DA6A9;
  --bg-tint: #F3F6F6;
  --border: #C9CFCF;      /* --border-light */
  --watermark: #ECEEEE;
  --white: #FFFFFF;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { background: #E9ECEC; }
body {
  font-family: "Outfit", "Zen Kaku Gothic New", "Hiragino Kaku Gothic ProN", "Noto Sans JP", sans-serif;
  color: var(--moss);
  -webkit-font-smoothing: antialiased;
  font-feature-settings: "palt";
}
.deck { display: flex; flex-direction: column; align-items: center; gap: 28px; padding: 28px 0; }
.slide {
  position: relative; width: 1128px; height: 846px; overflow: hidden;
  background: var(--white); box-shadow: 0 2px 14px rgba(0, 0, 0, .10);
  flex: none;
}
.slide.content::before { content: ""; position: absolute; left: 0; top: 0; width: 8px; height: 100%; background: var(--light); }
.slide.dark { background: var(--moss); color: var(--white); }
.slide .pageno { position: absolute; right: 40px; bottom: 20px; font-size: 14px; color: var(--muted); font-family: "Outfit", sans-serif; }
.slide .confidential { position: absolute; left: 56px; bottom: 20px; font-size: 12px; color: var(--muted); letter-spacing: 1px; font-family: "Outfit", sans-serif; }
.slide .title { position: absolute; left: 56px; top: 44px; width: 1016px; font-size: 38px; font-weight: 700; line-height: 1.3; }
.slide .sub { position: absolute; left: 56px; top: 100px; width: 1016px; font-size: 20px; color: var(--secondary); line-height: 1.5; }
.slide .foot { position: absolute; left: 56px; bottom: 44px; width: 1000px; font-size: 14px; color: var(--secondary); line-height: 1.5; }
.slide .body { position: absolute; left: 56px; top: 160px; width: 1016px; }
.bodywrap.long-sub { position: absolute; left: 0; top: 36px; width: 100%; }  /* サブタイトル2行ぶん下げる */
.slide .key { font-size: 28px; font-weight: 700; line-height: 1.5; }
.hl { color: var(--light); font-weight: 700; }
.en { font-family: "Outfit", sans-serif; }
.sec { color: var(--secondary); }
.num { font-family: "Outfit", sans-serif; font-weight: 700; color: var(--light); line-height: 1; }
p, li { line-height: 1.5; }

/* 表紙 */
.cover .wm { position: absolute; left: -20px; width: 1168px; text-align: center; font-size: 330px; font-weight: 700; line-height: 0.8; color: var(--watermark); font-family: "Outfit", sans-serif; letter-spacing: -0.02em; }
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
.circ { display: inline-flex; width: 28px; height: 28px; border-radius: 50%; background: var(--light); color: var(--white); font-family: "Outfit", sans-serif; font-size: 16px; font-weight: 700; align-items: center; justify-content: center; margin-right: 8px; vertical-align: 3px; }
.label { font-size: 16px; font-weight: 700; color: var(--light); letter-spacing: 2px; font-family: "Outfit", sans-serif; }
.h3 { font-size: 24px; font-weight: 700; line-height: 1.35; }
.bar4 { display: inline-block; width: 48px; height: 4px; background: var(--light); margin: 10px 0 14px; }
.hr { height: 1px; background: var(--border); }

/* 表 */
table.dt { border-collapse: collapse; width: 100%; }
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

/* 画面表示：幅に合わせて縮小 */
@media screen { .deck { transform-origin: top center; } }
@media print {
  html, body { background: var(--white); }
  .deck { display: block; padding: 0; gap: 0; transform: none !important; }
  .slide { box-shadow: none; page-break-after: always; break-after: page; }
  .slide:last-child { page-break-after: auto; break-after: auto; }
}
@page { size: 1128px 846px; margin: 0; }
"""

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


def img(name):
    path = os.path.join(IMG, name)
    mime = "image/jpeg" if name.endswith(".jpg") else "image/png"
    with open(path, "rb") as f:
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"


def md(s):
    """[[語]] はライトグリーン太字、**語** は太字。"""
    s = re.sub(r"\[\[(.+?)\]\]", r'<span class="hl">\1</span>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return s


SLIDES = []
NOTES = []
page_no = 0


def add(html, notes=None, cls="content", title=None, sub=None, foot=None, number=True):
    global page_no
    page_no += 1
    parts = [f'<section class="slide {cls}" id="s{page_no}">']
    if title:
        parts.append(f'<div class="title">{md(title)}</div>')
    if sub:
        parts.append(f'<div class="sub">{md(sub)}</div>')
    long_sub = bool(sub) and len(re.sub(r"<.*?>", "", sub)) > 50  # 20px で 1016px に収まるのは約50字
    parts.append(f'<div class="bodywrap{" long-sub" if long_sub else ""}">{md(html)}</div>')
    if foot:
        parts.append(f'<div class="foot">{md(foot)}</div>')
    if number and cls == "content":
        parts.append('<div class="confidential">Domuz inc.<span style="margin-left:14px">Confidential</span></div>')
        parts.append(f'<div class="pageno">{page_no}</div>')
    parts.append("</section>")
    SLIDES.append("\n".join(parts))
    if notes:
        NOTES.append((page_no, notes.strip()))


def divider(num, en, title, sub=""):
    add(
        f'<div class="no">{num}</div><div class="en">{en}</div>'
        f'<div class="ttl">{title}</div><div class="sub">{sub}</div>',
        cls="dark divider",
    )


# =====================================================================
# 1. 表紙（P-1）
# =====================================================================
add(
    '<div class="wm" style="top:-40px">Domuz</div>'
    '<div class="wm" style="top:242px">Domuz</div>'
    '<div class="wm" style="top:524px">Domuz</div>'
    '<div class="brand">Domuz</div>'
    '<div class="to">鳴海さん</div>'
    '<div class="ttl">イネイブラー事業・高付加価値3PL<br>現状共有とディスカッション</div>'
    '<div class="date">2026年10月15日（木）20:00〜｜オンライン</div>'
    '<div class="company">株式会社Domuz</div>',
    cls="cover",
    notes="10/15（木）20:00のオンライン面談用。メモの流れ（現状の事業進捗 → ライセンス → ディスカッション）に沿って構成。",
)

# =====================================================================
# 2. アジェンダ（P-11 番号付きリスト）
# =====================================================================
agenda = [
    ("1", "イネイブラー事業の現状", "事業方針・フラワーギフトオプション・第9期の計画・営業進捗"),
    ("2", "高付加価値3PLとライセンスの現状", "許認可の状況・拠点・用地"),
    ("3", "ディスカッション", "高付加価値3PLでやりたいこと・営業倉庫の要否・用地"),
]
rows = "".join(
    f'<div class="row"><div class="n num">{n}</div><div><div class="lab">{t}</div><div class="desc">{d}</div></div></div>'
    for n, t, d in agenda
)
add(f'<div class="nlist">{rows}</div>', title="本日のアジェンダ",
    sub="前半で現状を共有し、後半は営業倉庫と用地を中心にディスカッションしたいです。")

# =====================================================================
# 章扉 01
# =====================================================================
divider("01", "ENABLER BUSINESS", "イネイブラー事業の現状", "事業方針・フラワーギフトオプション・第9期の計画・営業進捗")

# =====================================================================
# 3. イネイブラー事業の方針
# =====================================================================
reasons = [
    ("広告費ゼロで売上", "他社ECで花が売れるため、広告費をかけずに売上をつくれます"),
    ("原価ダウン", "拠点からの発送数が増え、大量発注で原価が下がります"),
    ("作業の効率化", "少SKU・大量制作に絞ることで、作業が標準化されコストが下がります"),
]
cards = "".join(
    f'<div class="card"><div class="num" style="font-size:40px">0{i + 1}</div>'
    f'<h4 style="margin-top:12px">{h}</h4><p class="sec">{b}</p></div>'
    for i, (h, b) in enumerate(reasons)
)
add(
    f'''
<div class="body">
  <div class="label">FLOWER GIFT OPTION</div>
  <div class="h3" style="margin-top:6px">フラワーギフトオプションとは</div>
  <p style="font-size:20px;margin-top:10px;width:1000px">他社のECで買い物をするときに、お花をセットで贈れる仕組みです。EC事業者が自社で花の在庫や品質管理を持たなくても、お花付きギフトを提供できるようになります。生花パターンとプリパターンの2種類があります。</p>
  <div class="hr" style="margin:28px 0 26px"></div>
  <div class="key">BtoBで進める理由：[[他社の力を借りて、一気に裾野を広げられる]]から</div>
  <div class="cards" style="margin-top:28px">{cards}</div>
</div>''',
    title="イネイブラー事業の方針",
    sub="他社ECで、お花付きギフトが買える。その仕組みを提供し、お花を楽しむ人の「裾野」を広げる事業です。",
    notes="出典：10/9合宿資料。BtoBで進める理由は、他社の力を借りて一気に裾野を広げられるため。",
)

# =====================================================================
# 4. フラワーギフトオプションとは（2カラム）
# =====================================================================
merits = [
    ("顧客体験の向上", "ギフトの受け手の体験が向上し、ブランドのロイヤリティにもプラスに働きます。"),
    ("売上・粗利向上", "購入時に花のセット販売を案内することで購入単価が上がり、売上・粗利の向上に貢献します。"),
    ("CVR向上", "選択肢に花があることでCVRが向上します。事例：某ECモールの母の日ギフトで、購入率が[[1.5倍]]に上昇。"),
]
mrows = "".join(
    f'<div style="display:flex;gap:18px;padding:16px 0;border-bottom:1px solid var(--border)">'
    f'<div class="num" style="font-size:34px;width:44px;flex:none;padding-top:2px">{i + 1}</div>'
    f'<div><div style="font-size:22px;font-weight:700">{h}</div><p class="sec" style="font-size:16px;margin-top:4px">{md(b)}</p></div></div>'
    for i, (h, b) in enumerate(merits)
)
add(
    f'''
<div class="body" style="display:flex;gap:48px">
  <div style="width:480px">
    <div class="h3">お花とのセット販売を実現</div>
    <div class="bar4"></div>
    <img src="{img('set_gift.jpg')}" style="width:480px;display:block">
    <p class="sec" style="font-size:16px;margin-top:14px">飲料、食品、コスメなど様々な事業者様に向けて、ギフトシーンにおける花のセット販売機能を提供し、より高いギフト体験を実現します。</p>
  </div>
  <div style="width:488px">
    <div class="h3">導入のメリット</div>
    <div class="bar4"></div>
    {mrows}
  </div>
</div>''',
    title="フラワーギフトオプションとは",
    sub="花はギフトの需要が高い一方、品質管理が難しく、提供できていない事業者が多い。Domuzなら「花とともに贈る体験」を簡単に導入できます。",
    notes="出典：村上さん共有資料 P7。事例は、某ECモール内で複数ジャンルの母の日ギフトに「花を同時に注文できる」ようにしたところ購入率が1.5倍に上昇した実績。",
)

# =====================================================================
# 5. 実現パターン（図は SVG で描き直し）
# =====================================================================


def node(x, y, label, fill=False):
    w, h = 118, 60
    bg = "var(--moss)" if fill else "var(--white)"
    fg = "var(--white)" if fill else "var(--moss)"
    return (f'<rect x="{x - w / 2}" y="{y - h / 2}" width="{w}" height="{h}" fill="{bg}" stroke="var(--moss)" stroke-width="1.5"/>'
            f'<text x="{x}" y="{y + 6}" text-anchor="middle" font-size="16" font-weight="700" fill="{fg}">{label}</text>')


def tag(x, y, label, color):
    w = 16 * len(label) + 16
    return (f'<rect x="{x - w / 2}" y="{y - 12}" width="{w}" height="24" rx="12" fill="{color}"/>'
            f'<text x="{x}" y="{y + 5}" text-anchor="middle" font-size="13" font-weight="700" fill="#fff">{label}</text>')


def arrow(x1, y1, x2, y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="var(--moss)" stroke-width="1.5" marker-end="url(#ah)"/>'


DEFS = '<defs><marker id="ah" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="var(--moss)"/></marker></defs>'
LIGHT, FLOWER = "var(--light)", "var(--flower)"
p1 = (f'<svg viewBox="0 0 320 230" width="320" height="230">{DEFS}'
      + node(70, 190, "導入企業様") + arrow(70, 160, 70, 72) + tag(70, 116, "商品", LIGHT)
      + node(70, 42, "Domuz 倉庫", True) + arrow(129, 42, 190, 42) + tag(160, 42, "花＋商品", FLOWER)
      + node(250, 42, "消費者") + '</svg>')
p2 = (f'<svg viewBox="0 0 320 230" width="320" height="230">{DEFS}'
      + node(70, 42, "Domuz 倉庫", True) + node(70, 190, "導入企業様")
      + arrow(129, 42, 190, 70) + tag(165, 40, "花", FLOWER)
      + arrow(129, 190, 190, 150) + tag(165, 190, "商品", LIGHT)
      + node(250, 116, "消費者") + '</svg>')
p3 = (f'<svg viewBox="0 0 320 230" width="320" height="230">{DEFS}'
      + node(70, 42, "Domuz 倉庫", True) + arrow(70, 72, 70, 160) + tag(70, 116, "花", FLOWER)
      + node(70, 190, "導入企業様") + arrow(129, 190, 190, 190) + tag(160, 190, "花＋商品", LIGHT)
      + node(250, 190, "消費者") + '</svg>')
patterns = [
    ("1", "弊社から同梱して送る", "弊社へ導入企業様の商品を事前に納入いただき、弊社から同梱して発送するパターン", p1),
    ("2", "同じタイミングで送る", "注文情報を連携し、ギフトの送り先住所へ同じ配送業者・配送日時で届けるパターン。発送拠点が関東エリアにあり、サイズが大きく異ならない場合に限られます（佐川急便、ヤマト運輸の場合）", p2),
    ("3", "導入企業様から送る", "事前に導入企業様へ花を卸しておき、配送していただくパターン。ドライフラワーやプリザーブドフラワーに限られます", p3),
]
cols = "".join(
    f'<div style="width:320px">{svg}<div class="hr" style="margin:10px 0 14px"></div>'
    f'<div style="font-size:22px;font-weight:700"><span class="circ">{n}</span>{h}</div>'
    f'<p class="sec" style="font-size:15px;margin-top:8px">{b}</p></div>'
    for n, h, b, svg in patterns
)
add(
    f'<div class="body" style="display:flex;gap:28px;top:172px">{cols}</div>',
    title="フラワーギフトオプションの実現パターン",
    sub="導入企業様の販売方法や状況に合わせて、配送オペレーションのパターンを複数ご用意しています。",
    notes="出典：村上さん共有資料 P8。図は同資料をもとに描き直し。",
)

# =====================================================================
# 6. セット用ブーケのイメージ（写真グリッド）
# =====================================================================
bouquets = [
    ("bouquet_L.jpg", "フラワーブーケ Lサイズ", "6,300", "特別なギフト向けの大ぶりの花束。"),
    ("bouquet_M.jpg", "フラワーブーケ Mサイズ", "4,900", "定番のサイズ。"),
    ("bouquet_S.jpg", "フラワーブーケ Sサイズ", "2,500", "コンパクトでもしっかり存在感のある人気サイズ。"),
    ("bouquet_rose2.jpg", "バラのミニブーケ", "1,800", "バラ2輪と葉物のミニブーケ。"),
    ("bouquet_rose1.jpg", "バラのプチブーケ", "1,200", "バラ1輪と葉物のミニブーケ。"),
    ("bouquet_omakase.jpg", "おまかせプチブーケ", "980", "その時に合わせてアレンジするミニブーケ。"),
]
cells = "".join(
    f'<div style="display:flex;gap:16px;width:496px;align-items:center">'
    f'<img src="{img(f)}" style="width:150px;height:186px;object-fit:cover;flex:none;display:block">'
    f'<div><div style="font-size:19px;font-weight:700;line-height:1.3">{n}</div>'
    f'<div style="margin-top:6px"><span class="en" style="font-size:30px;font-weight:700;line-height:1">{p}</span>'
    f'<span style="font-size:15px;color:var(--secondary);margin-left:4px">円（下代）</span></div>'
    f'<p class="sec" style="font-size:14px;margin-top:6px">{d}</p></div></div>'
    for f, n, p, d in bouquets
)
add(
    f'<div class="body" style="display:flex;flex-wrap:wrap;gap:16px 24px;top:158px">{cells}</div>',
    title="セット用ブーケのイメージ",
    sub="価格帯・色味は導入企業様のイメージに合わせて選択できます。記載の価格は下代（卸値）で、セット価格は貴社で自由に設定可能です。",
    foot="※ 上記価格は一般的な花材を利用した場合の目安です。花材やラッピングの内容・色は相談可能です。",
    notes="出典：村上さん共有資料 P9。価格は一般的な花材を利用した場合の目安。花材やラッピングの内容・色は相談可能。",
)

# =====================================================================
# 7. イネイブラーのエコノミクス（表）
# =====================================================================
econ = [
    ("フラワーブーケ Lサイズ", "6,300", "2,352（37%）", "1,427（23%）", "+373", "1,800（24%）"),
    ("フラワーブーケ Mサイズ", "4,900", "2,138（44%）", "1,413（29%）", "+414", "1,827（31%）"),
    ("フラワーブーケ Sサイズ", "2,500", "878（35%）", "353（14%）", "+368", "721（21%）"),
    ("バラの二輪ブーケ", "1,800", "830（46%）", "480（27%）", "+368", "848（32%）"),
    ("バラの一輪ブーケ", "1,200", "640（53%）", "340（28%）", "+368", "708（34%）"),
    ("おまかせミニブーケ（M）", "1,500", "670（45%）", "370（25%）", "+368", "738（31%）"),
    ("おまかせミニブーケ（S）", "980", "300（31%）", "±0（0%）", "+368", "368（20%）"),
]


def cell(v):
    m = re.match(r"(.+?)（(.+?)）$", v)
    if m:
        return f'{m.group(1)}<span class="pct">({m.group(2)})</span>'
    return v


trs = "".join(
    f'<tr><td>{r[0]}</td><td class="r">{cell(r[1])}</td><td class="r">{cell(r[2])}</td>'
    f'<td class="r">{cell(r[3])}</td><td class="r">{cell(r[4])}</td><td class="r strong">{cell(r[5])}</td></tr>'
    for r in econ
)
add(
    f'''
<div class="body" style="top:152px">
  <table class="dt">
    <thead><tr><th>商品</th><th style="text-align:right">B2B下代</th><th style="text-align:right">限界利益</th><th style="text-align:right">貢献利益</th><th style="text-align:right">送料差益</th><th style="text-align:right">送料込み貢献</th></tr></thead>
    <tbody>{trs}</tbody>
  </table>
  <p class="key" style="font-size:24px;margin-top:30px">送料差益（B2B配送料収入と佐川実費の差）は、商品単体の貢献利益に上乗せされます。<br>たとえばSサイズは、貢献利益353円が送料差益368円を加えて[[721円]]になります。</p>
</div>''',
    title="イネイブラーのエコノミクス",
    sub="商品単体でも限界利益・貢献利益を確保できます。さらに送料差益が上乗せされ、利益は一段と向上します。",
    foot="※ 単位は円。限界利益・貢献利益の（）内は下代に対する率、送料込み貢献の（）内は送料収入を含む総収入に対する率。貢献利益は限界利益から作業費（25円／分）を引いた額です。",
    notes="出典：Notion「イネイブラー エコノミクス比較表」（9/14更新）。商品単体は送料実費・配送料収入を除いた数字。作業費は25円/分でサイズ別に算出。送料差益は箱サイズ別（80=+368円、100=+414円、120=+373円）。",
)

# =====================================================================
# 8. 利益の構造（Mサイズの例）— 横の積み上げ棒
# =====================================================================
SCALE = 1016 / 4900  # px / 円（下代4,900円 = 1016px）


def hbar(label, total, segs, y):
    """segs: (名前, 円, 色, 文字色)。幅は共通スケール（1円=同じ長さ）。"""
    x = 0
    out = [f'<div style="position:absolute;left:0;top:{y}px;font-size:20px;font-weight:700">{label}</div>']
    for name, yen, col, fg in segs:
        w = yen * SCALE
        lab = (f'<div style="font-size:15px;font-weight:700">{name}</div>'
               f'<div class="en" style="font-size:24px;font-weight:700;margin-top:2px">{yen:,}'
               f'<span style="font-size:13px;font-weight:400;margin-left:4px">円 ({round(yen / total * 100)}%)</span></div>')
        out.append(f'<div style="position:absolute;left:{x}px;top:{y + 40}px;width:{w - 3}px;height:84px;background:{col};'
                   f'display:flex;flex-direction:column;justify-content:center;align-items:center;color:{fg}">'
                   + (lab if w >= 200 else "") + '</div>')
        if w < 200:  # 狭いセグメントは棒の下にラベル
            out.append(f'<div style="position:absolute;left:{x}px;top:{y + 132}px;width:160px;color:var(--moss);'
                       f'border-left:2px solid {col};padding-left:8px">{lab}</div>')
        x += w
    return "".join(out)


b1 = hbar("商品（下代 4,900円）", 4900,
          [("原価＆変動費", 2762, "var(--bg-gray)", "var(--moss)"), ("作業費", 725, "var(--bg-gray2)", "#fff"),
           ("貢献利益", 1413, "var(--light)", "#fff")], 0)
b2 = hbar("送料（収入 960円）", 960,
          [("佐川実費", 546, "var(--bg-gray)", "var(--moss)"), ("送料差益", 414, "var(--light)", "#fff")], 150)
add(
    f'''
<div class="body" style="top:166px;height:300px">{b1}{b2}</div>
<div class="body" style="top:560px">
  <div class="hr"></div>
  <div style="display:flex;align-items:baseline;gap:18px;margin-top:30px;flex-wrap:wrap">
    <span style="font-size:26px;font-weight:700">貢献利益 <span class="en">1,413</span>円 ＋ 送料差益 <span class="en">414</span>円</span>
    <span style="font-size:26px;font-weight:700">＝</span>
    <span class="hl en" style="font-size:64px;line-height:1">1,827</span><span class="hl" style="font-size:28px">円</span>
    <span style="font-size:22px;color:var(--secondary)">（下代の約37%）</span>
  </div>
</div>''',
    title="利益の構造（Mサイズの例）",
    sub="下代のうち貢献利益は約29%。これに送料差益（+414円）が上乗せされ、1商品あたりの利益は1,827円になります。",
    foot="※ 上代はお客様側で設定。事業者様の粗利は20〜30%を想定。直接固定費（作業費）は発送個数が多いほど効率化できます。",
    notes="出典：Notion「イネイブラー エコノミクス比較表」。フラワーブーケMサイズ（下代4,900円、100サイズ）。花材2,310円＋資材452円＝原価・変動費2,762円（56%）、作業費725円（15%）、貢献利益1,413円（29%）。送料は配送料収入960円に対し佐川実費546円、差益414円（43%）。上代はお客様側で設定し、事業者様の粗利は20〜30%を想定。",
)

# =====================================================================
# 9. 名入れオプション
# =====================================================================
add(
    f'''
<div class="body" style="top:164px">
  <img src="{img('naire.jpg')}" style="width:1016px;height:520px;object-fit:contain;display:block;background:#fff">
  <p style="font-size:22px;margin-top:22px">アンドフラワー上の一部の商品に対して、名入れオプションを[[サイレントで販売]]しています。</p>
</div>''',
    title="名入れオプション",
    sub="商品への名入れも今後のスコープに入れ、一部商品でサイレント販売を始めています。",
    notes="出典：村上さん共有資料 P12。アンドフラワー上の一部商品に対して名入れオプションをサイレントで販売中。",
)

# =====================================================================
# 10. 第9期の事業計画（KPI＋内訳）
# =====================================================================
plan = [
    ("イネイブラー領域", "7,200万円", [
        ("卸", "生花・ドライ・プリを卸売り", "3,000万円"),
        ("生花を送る", "他社商品と花束をセットで送る", "3,000万円"),
        ("その他オプション", "チョコ・ぬいぐるみ等を同梱", "1,200万円"),
    ]),
    ("高付加価値3PL領域", "1億1,800万円", [
        ("倉庫業", "他社商品の保管・梱包・発送を代行", "1億1,800万円"),
    ]),
]
prows = ""
for grp, total, items in plan:
    prows += (f'<tr class="total"><td style="font-size:19px">{grp}</td><td></td>'
              f'<td class="r" style="font-size:19px">{total}</td></tr>')
    for name, desc, val in items:
        prows += (f'<tr><td style="padding-left:30px;font-size:17px">{name}</td>'
                  f'<td class="sec" style="font-size:15px">{desc}</td><td class="r" style="font-size:17px">{val}</td></tr>')
# 構成比の横棒（百万円）
comp = [("高付加価値3PL", 118, "var(--moss)"), ("卸", 30, "var(--light)"), ("生花を送る", 30, "#5FE3BE"), ("その他", 12, "var(--bg-gray)")]
tot = sum(v for _, v, _ in comp)
segs = "".join(
    f'<div class="en" style="width:{v / tot * 100}%;background:{c};height:100%;display:flex;align-items:center;justify-content:center;'
    f'color:{"#fff" if c != "var(--bg-gray)" else "var(--moss)"};font-size:15px;font-weight:700;white-space:nowrap;overflow:hidden">'
    f'{round(v / tot * 100)}%</div>'
    for n, v, c in comp
)
legend = "".join(
    f'<span style="display:inline-flex;align-items:center;gap:6px;margin-right:18px;font-size:14px;color:var(--secondary)">'
    f'<span style="width:12px;height:12px;background:{c};display:inline-block"></span>{n}</span>'
    for n, v, c in comp
)
add(
    f'''
<div class="body" style="top:160px;display:flex;gap:48px">
  <div style="width:300px">
    <div class="kpi">
      <div class="lab">第9期 売上目標</div>
      <div class="val"><span class="jp" style="font-size:40px">約</span>1.9<span class="unit">億円</span></div>
    </div>
    <div class="kpi" style="margin-top:34px">
      <div class="lab">第8期比</div>
      <div class="val"><span class="jp" style="font-size:40px">約</span>16<span class="unit">倍</span></div>
    </div>
    <div class="hr" style="margin:34px 0 24px"></div>
    <p class="key" style="font-size:22px">売上の[[約6割]]を<br>高付加価値3PL領域（倉庫業）で見込む</p>
  </div>
  <div style="width:668px">
    <table class="dt">
      <thead><tr><th>事業</th><th>内容</th><th style="text-align:right">第9期目標</th></tr></thead>
      <tbody>{prows}</tbody>
    </table>
    <div style="margin-top:28px;font-size:14px;color:var(--secondary)">売上構成比</div>
    <div style="display:flex;height:40px;margin-top:8px;gap:3px">{segs}</div>
    <div style="margin-top:10px">{legend}</div>
  </div>
</div>''',
    title="第9期の事業計画",
    sub="第9期は売上約1.9億円が目標で、その約6割を高付加価値3PL領域（倉庫業）で見込んでいます。",
    foot="※ 事業計画（2026/8版）。第9期の発送数目標は284,061件。",
    notes="出典：10/9合宿資料（事業計画2026/8版）。3PL領域が約62%を占める。第8期実績は資料間で数値が異なるため掲載していない。",
)

# =====================================================================
# 11. 営業進捗
# =====================================================================


def section(label, extra=""):
    return (f'<div style="display:flex;align-items:baseline;gap:14px;margin-bottom:12px">'
            f'<div style="font-size:20px;font-weight:700">{label}</div>{extra}</div>')


decided = [
    ("PAPABUBBLE", "10/13 リリース済み", "16SKU", "done"),
    ("フレッシュロースター珈琲問屋", "10/15 リリース目標", "4SKU（ドリップバッグ2・花2）", "plan"),
]
dcards = "".join(
    f'<div class="card" style="padding:16px 20px"><div style="display:flex;justify-content:space-between;align-items:center;gap:12px">'
    f'<div style="font-size:21px;font-weight:700">{n}</div><span class="pill {k}">{s}</span></div>'
    f'<p class="sec" style="font-size:16px;margin-top:6px">{d}</p></div>'
    for n, s, d, k in decided
)
talking = [
    ("遠鉄百貨店", ["生花単体を最終検討中", "配送はヤマト指定"]),
    ("HAKUBA CRAFT", ["クール便での実施予定", "初の生花クール便で実施"]),
    ("UCC・BAKE", ["2027年の母の日コラボ", "今期は生花の提案を行う"]),
]
tcards = "".join(
    f'<div class="card tint" style="padding:16px 20px"><div style="font-size:20px;font-weight:700">{n}</div>'
    + "".join(f'<p style="font-size:15px;margin-top:4px;color:var(--secondary)">・{l}</p>' for l in ls)
    + '</div>'
    for n, ls in talking
)
measures = [
    ("ギフティ連携", "LINEギフト・Giftee.comへの機能導入"),
    ("営業代行のコールド", "月300件・アポ率3%"),
    ("既存企業へ再営業", "AIで候補先を探索し、自動で営業連絡"),
]
mcards = "".join(
    f'<div style="flex:1;display:flex;gap:12px;align-items:flex-start"><div class="num" style="font-size:28px;padding-top:2px">0{i + 1}</div>'
    f'<div><div style="font-size:18px;font-weight:700">{h}</div><p class="sec" style="font-size:14px;margin-top:2px">{b}</p></div></div>'
    for i, (h, b) in enumerate(measures)
)
add(
    f'''
<div class="body" style="top:150px">
  {section("導入決定", '<span class="hl en" style="font-size:30px;line-height:1">2</span><span class="hl" style="font-size:18px">社</span>')}
  <div class="cards">{dcards}</div>
  <div style="margin-top:22px">{section("具体協議中")}</div>
  <div class="cards">{tcards}</div>
  <div style="margin-top:22px">{section("営業施策")}</div>
  <div style="display:flex;gap:24px">{mcards}</div>
</div>''',
    title="営業進捗",
    sub="商談すると6〜7割が具体協議に進み、2社の導入が決定。10月に順次リリースします。",
    foot="※ 珈琲問屋はサイト制作の都合で若干のディレイあり。",
    notes="出典：10/9合宿資料、10/13イネイブラー事業推進MTG。珈琲問屋はサイト制作の都合で若干のディレイあり。",
)

# =====================================================================
# 章扉 02
# =====================================================================
divider("02", "3PL &amp; LICENSES", "高付加価値3PLとライセンスの現状", "許認可の状況・拠点・用地")

# =====================================================================
# 12. 免許・許認可の取得ステータス（表）
# =====================================================================
lic = [
    ("第一種貨物利用運送事業", "送料差益の請求", ("申請済み（10/13）", "done"), "低", "書類審査のみ。標準処理期間は2〜3ヶ月で、年内取得の見込み"),
    ("営業倉庫（倉庫業登録）", "保管費の請求", ("方向性相談", "todo"), "中〜高", "取得時期は未定（SGL社との調整後）。要否は本日の議論で決めたい"),
    ("冷蔵倉庫業の届出", "冷蔵商品の管理・発送", ("方向性相談", "todo"), "低", "同様に取得要否は未定。相談"),
    ("化粧品製造業許可", "コスメのセット組み・名入れ・ラベル貼付", ("要検討", "todo"), "中", "出荷判定前の保管は製造行為にあたり許可が必須。責任技術者の配置あり"),
    ("高圧ガス保安法", "大型冷凍設備の設置・運用", ("要確認", "todo"), "中", "冷凍能力が一定規模を超えると手続きが必要。設備仕様の確定時に判断"),
    ("酒類販売業免許", "酒類の発送", ("取得予定", "plan"), "中", "荷主の酒の保管・発送のみなら不要。自社で仕入れて販売する場合は必要"),
]
ltrs = "".join(
    f'<tr><td style="font-weight:700;font-size:17px">{a}</td><td style="font-size:15px">{b}</td>'
    f'<td><span class="pill {k}">{s}</span></td><td style="font-size:15px;text-align:center">{d}</td>'
    f'<td class="sec" style="font-size:14px">{e}</td></tr>'
    for a, b, (s, k), d, e in lic
)
add(
    f'''
<div class="body" style="top:160px">
  <table class="dt">
    <thead><tr><th>免許・届出</th><th>できる業務</th><th>ステータス</th><th style="text-align:center">難易度</th><th>備考</th></tr></thead>
    <tbody>{ltrs}</tbody>
  </table>
  <p class="key" style="font-size:24px;margin-top:30px">営業倉庫の要否を、[[今日の議論で決めたい]]。</p>
</div>''',
    title="免許・許認可の取得ステータス",
    sub="第一種貨物利用運送事業は10/13に申請済み。営業倉庫は今日の議論で方向性を決めたいと考えています。",
    notes="出典：村上さん共有資料 P14〜15（2026/9/9時点）を、10/13の経営MTG・推進MTGで更新。第一種貨物利用運送事業は10/13に登録申請済み（ご指示により反映）。",
)

# =====================================================================
# 13. 拠点・用地の状況
# =====================================================================
options = [
    ("A", "SGL一部を少し借りて佐川へ業務委託し、2Hの一部、2H全部へと段階的に広げる"),
    ("B", "2Gを最初から丸ごと借りる"),
    ("C", "佐川以外の倉庫を借りる"),
]
orows = "".join(
    f'<div style="display:flex;gap:16px;align-items:flex-start;padding:10px 0;border-bottom:1px solid var(--border)">'
    f'<div class="num" style="font-size:30px;width:36px;flex:none">{k}</div>'
    f'<p style="font-size:18px;padding-top:4px">{t}</p></div>'
    for k, t in options
)
add(
    f'''
<div class="body" style="top:156px">
  <div class="cards" style="gap:28px">
    <div class="card" style="padding:22px 26px">
      <div class="label">KAWASAKI</div>
      <h4 style="font-size:24px;margin-top:4px">川崎拠点（花）</h4>
      <div style="display:flex;gap:22px;margin-top:12px;align-items:baseline">
        <div><span class="en" style="font-size:32px;font-weight:700">128.84</span><span class="sec" style="font-size:14px;margin-left:3px">坪</span></div>
        <div><span class="sec" style="font-size:14px">家賃</span> <span class="en" style="font-size:32px;font-weight:700">94</span><span class="sec" style="font-size:14px;margin-left:3px">万円／月</span></div>
        <div><span class="sec" style="font-size:14px">限界利益率</span> <span class="en" style="font-size:32px;font-weight:700">約45</span><span class="sec" style="font-size:14px;margin-left:3px">%</span></div>
      </div>
      <p style="font-size:16px;margin-top:10px">2Iが手狭になり、坪あたりの発送効率の目標を定めて改善しつつ、新しい場所も探します。</p>
    </div>
    <div class="card fill" style="padding:22px 26px">
      <div class="label">2G</div>
      <h4 style="font-size:24px;margin-top:4px">2Gの賃借</h4>
      <p style="font-size:17px;margin-top:12px">借りる方向で、最短で<b>12月</b>。川崎の場所を空けるため、2I自体の効率化も急務で進めたい</p>
    </div>
  </div>
  <div style="margin-top:30px">
    <div class="h3">佐川スペースの確保方式（ラフ）</div>
    <div class="bar4"></div>
    {orows}
    <p class="sec" style="font-size:16px;margin-top:14px">段階論も含め検討しております。倉庫業をとる場合Aではできないと想定されるため要検討</p>
  </div>
</div>''',
    title="拠点・用地の状況",
    sub="川崎拠点は手狭になりつつあり、2Gの賃借と佐川スペースの活用を並行して検討しています。",
    notes="出典：経営MTG（10/14）、Notion「3PL事業立ち上げまとめ」のバックログ（拠点確保方式A/B/C）。方式の整理は7月時点。",
)

# =====================================================================
# 章扉 03
# =====================================================================
divider("03", "DISCUSSION", "ディスカッション", "高付加価値3PLでやりたいこと・営業倉庫の要否・用地")

# =====================================================================
# 14. ディスカッションしたいこと（P-11）
# =====================================================================
topics = [
    ("01", "営業倉庫は、いま必要か",
     ["当初は営業倉庫がなくても、SGL（佐川）との3社間契約でお客さまを連れて来られるか", "営業倉庫が必要なら、具体的に動き始めたい"]),
    ("02", "高付加価値3PLを進めるうえで、やりたいこと・事前に用意すべきこと",
     ["最初に狙う荷主像や、すぐ提案できる先"]),
    ("03", "用地をどうするか",
     ["営業倉庫の今後と、拠点・ライセンスの進め方"]),
]
trows = "".join(
    f'<div class="row" style="padding:34px 0"><div class="n num" style="font-size:56px">{n}</div>'
    f'<div><div class="lab" style="font-size:30px">{t}</div>'
    + "".join(f'<div class="desc" style="font-size:19px;margin-top:8px">・{l}</div>' for l in ls)
    + '</div></div>'
    for n, t, ls in topics
)
add(
    f'<div class="nlist" style="top:150px">{trows}</div>',
    title="ディスカッションしたいこと",
    sub="高付加価値3PLを進めるうえでやりたいことと、用地をどうするかを一緒に考えたいです。",
    notes="メモの「高付加価値3PLを進めていく上でやりたいこと」「用地をどうするか」に対応。",
)

# =====================================================================
# 書き出し
# =====================================================================
HTML = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>イネイブラー事業・高付加価値3PL 現状共有とディスカッション｜2026.10.15</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;700&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="deck">
{chr(10).join(SLIDES)}
</div>
<script>{SCRIPT}</script>
</body>
</html>
"""
out = os.path.join(HERE, "deck.html")
with open(out, "w") as f:
    f.write(HTML)
with open(os.path.join(HERE, "notes.md"), "w") as f:
    f.write("# 鳴海さんMTG 2026.10.15 — 発表者ノート（出典メモ・スライド番号つき）\n\n")
    for n, body in NOTES:
        f.write(f"## {n}\n\n{body}\n\n")
print("saved", out, "slides:", len(SLIDES))
