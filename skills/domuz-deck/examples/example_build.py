"""domuz_deck の使い方の見本。代表的なスライド型を1枚ずつ組んで deck.html を書く。

    python3 example_build.py            # カレントに deck.html / notes.md
    NODE_PATH=$(npm root -g) node ../scripts/render_pdf.js deck.html deck.pdf
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "assets"))
from domuz_deck import Deck  # noqa: E402

d = Deck(title="見本デッキ｜domuz_deck", img_dir=HERE)
d.icons(os.path.join(HERE, "..", "assets", "icons"))

# 1. 表紙（P-1）
d.cover(to="鳴海さん", title="イネイブラー事業・高付加価値3PL<br>現状共有とディスカッション",
        date="2026年10月15日（木）20:00〜｜オンライン", notes="表紙。宛名は外部向けのときだけ。")

# 2. アジェンダ（P-11）
d.slide(d.nlist([("1", "イネイブラー事業の現状", "事業方針・フラワーギフトオプション・第9期の計画・営業進捗"),
                 ("2", "高付加価値3PLとライセンスの現状", "許認可の状況・拠点・用地"),
                 ("3", "ディスカッション", "高付加価値3PLでやりたいこと・営業倉庫の要否・用地")]),
        title="本日のアジェンダ", sub="前半で現状を共有し、後半は営業倉庫と用地を中心にディスカッションしたいです。")

# 3. 章扉（P-3）
d.divider("01", "ENABLER BUSINESS", "イネイブラー事業の現状", "事業方針・計画・営業進捗")

# 4. 説明＋3カード
d.slide(f'''
<div class="body">
  <div class="label">FLOWER GIFT OPTION</div>
  <div class="h3" style="margin-top:6px">フラワーギフトオプションとは</div>
  <p style="font-size:20px;margin-top:10px">他社のECで買い物をするときに、お花をセットで贈れる仕組みです。</p>
  <div class="hr" style="margin:28px 0 26px"></div>
  <div class="h3" style="font-size:26px">イネイブラーのメリット<span class="sec" style="font-size:18px;font-weight:400;margin-left:14px">他社の力を借りて、一気に裾野を広げられる</span></div>
  <div style="margin-top:28px">{d.cards([("広告費ゼロで売上", "他社ECで花が売れるため、広告費をかけずに売上をつくれます"),
                                        ("原価ダウン", "拠点からの発送数が増え、大量発注で原価が下がります"),
                                        ("作業の効率化", "少SKU・大量制作に絞ることで、作業が標準化されコストが下がります")])}</div>
</div>''', title="イネイブラー事業の方針", sub="他社ECで、お花付きギフトが買える。その仕組みを提供し、お花を楽しむ人の「裾野」を広げる事業です。")

# 5. 表＋キーメッセージ
rows = [("フラワーブーケ Mサイズ", "4,900", "2,138（44%）", "1,413（29%）", "+414", "1,827（31%）"),
        ("フラワーブーケ Sサイズ", "2,500", "878（35%）", "353（14%）", "+368", "721（21%）")]
d.slide(f'''
<div class="body" style="top:152px">
  {d.table(["商品", "B2B下代", "限界利益", "貢献利益", "送料差益", "送料込み貢献"], rows, strong_col=5)}
  <p class="key" style="font-size:24px;margin-top:30px">送料差益は商品単体の貢献利益に上乗せされます。たとえばSサイズは[[721円]]になります。</p>
</div>''', title="イネイブラーのエコノミクス", sub="商品単体でも限界利益・貢献利益を確保できます。",
        foot="※ 単位は円。（）内は下代に対する率。", notes="出典：Notion「イネイブラー エコノミクス比較表」")

# 6. KPI＋ステータス表
d.slide(f'''
<div class="body" style="display:flex;gap:48px">
  <div style="width:300px">
    {d.kpi("第9期 売上目標", "1.9", "億円", prefix="約")}
    <div style="margin-top:34px">{d.kpi("第8期比", "16", "倍", prefix="約")}</div>
    <div class="hr" style="margin:34px 0 24px"></div>
    <p class="key" style="font-size:22px">売上の[[約6割]]を<br>高付加価値3PL領域で見込む</p>
  </div>
  <div style="width:668px">
    {d.table(["免許・届出", "できる業務", "ステータス"],
             [("第一種貨物利用運送事業", "送料差益の請求", d.pill("申請済み（10/13）", "done")),
              ("営業倉庫（倉庫業登録）", "保管費の請求", d.pill("方向性相談", "todo")),
              ("酒類販売業免許", "酒類の発送", d.pill("取得予定", "plan"))], aligns=["l", "l", "l"], font=16)}
  </div>
</div>''', title="第9期の事業計画と許認可", sub="KPI（P-6）とステータス表の組み合わせ。")

# 7. 横の積み上げ棒（利益の構造）
S = 1016 / 6000
G, G2, M, Wt = "var(--bg-gray)", "var(--bg-gray2)", "var(--moss)", "var(--white)"
d.slide(f'''
<div class="body" style="top:160px;height:360px">
  {d.hbar("花 6,000円の内訳", 6000, [("事業者様の粗利", 1100, Wt, M, M), ("原価＆変動費", 2762, G, M), ("作業費", 725, G2, Wt),
                                   ("貢献利益", 1413, "var(--light)", Wt)], 0, S, note="右の3区画がDomuzの下代 4,900円")}
  {d.hbar("配送料 960円", 960, [("佐川実費", 546, G, M), ("送料差益", 414, "var(--light)", Wt)], 170, S, h=48)}
</div>
<div class="body" style="top:560px">
  <div class="hr"></div>
  <div style="display:flex;align-items:baseline;gap:16px;margin-top:22px">
    <span style="font-size:24px;font-weight:700">貢献利益 <span class="en">1,413</span>円 ＋ 送料差益 <span class="en">414</span>円 ＝</span>
    <span class="hl en" style="font-size:56px;line-height:1">1,827</span><span class="hl" style="font-size:26px">円</span>
  </div>
</div>''', title="利益の構造（Mサイズの例）", sub="同じ目盛りで棒を並べると、量が比べられる。")

# 8. フロー図（アイコン）
p1 = d.svg(d.node(70, 270, "warehouse", "導入企業様") + d.arrow(70, 226, 70, 138) + d.tag(70, 182, ["box"], "商品")
           + d.node(70, 64, "warehouse", "Domuz 倉庫", "moss") + d.arrow(114, 64, 208, 64) + d.tag(161, 26, ["bouquet", "box"], "花＋商品")
           + d.node(252, 64, "person", "消費者"))
p2 = d.svg(d.node(70, 64, "warehouse", "Domuz 倉庫", "moss") + d.node(70, 270, "warehouse", "導入企業様")
           + d.arrow(118, 64, 212, 150) + d.tag(150, 64, ["bouquet"], "花")
           + d.arrow(118, 270, 212, 184) + d.tag(150, 270, ["box"], "商品") + d.node(252, 167, "person", "消費者"))
cols = "".join(
    f'<div style="width:320px"><div style="font-size:22px;font-weight:700;height:40px"><span class="circ">{n}</span>{h}</div>'
    f'<div class="hr" style="margin:8px 0 14px"></div><div style="background:var(--bg-tint);padding:10px 0">{svg}</div>'
    f'<p class="sec" style="font-size:15px;margin-top:14px">{b}</p></div>'
    for n, h, b, svg in [("1", "弊社から同梱して送る", "弊社へ商品を事前に納入いただき、同梱して発送", p1),
                         ("2", "同じタイミングで送る", "注文情報を連携し、同じ配送業者・配送日時で届ける", p2)])
d.slide(f'<div class="body" style="display:flex;gap:28px">{cols}</div>',
        title="フラワーギフトオプションの実現パターン", sub="ノードは丸＋アイコン、矢印には「何が動くか」のタグ。")

# 9. 主張文（P-2）
d.message("花/植物を楽しむ人の「[[裾野]]」を広げる")

# 10. 月次の縦棒
d.slide(f'''
<div class="body" style="top:150px;height:560px">
  {d.vbars([f"{m}月" for m in [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]], [59, 60, 60, 79, 55, 68, 98, 112, 62, 62, 59, 66], x0=56, bw=56, gap=24, base_y=460, max_h=280)}
</div>
<div class="body" style="top:690px"><p class="key">5月に、創業以来はじめて[[月商1億円]]を超えた。</p></div>''',
        title="全社の数字", sub="月次売上　単位：百万円　※税抜", foot="※ 試算表の暫定値")

d.save(os.path.join(HERE, "deck.html"), os.path.join(HERE, "notes.md"))
