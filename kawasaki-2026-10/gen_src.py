#!/usr/bin/env python3
"""src/giftee_kawasaki.src.html を生成する。数字とグラフ（インラインSVG）をここで計算し、
Domuz デザインシステム v2.1（4:3・1128×846px・src/_base.css）の型で組む。
実行: python3 gen_src.py && python3 build.py --pdf
"""
import os
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_NAME = "ギフティ様_川崎倉庫の収益性試算_20261013.html"

# ---------------- 数字（FY2026 = 2025/10〜2026/9） ----------------
L = ['10月','11月','12月','1月','2月','3月','4月','5月','6月','7月','8月','9月']
AF_O = [2143,1882,1613,1721,1420,2078,3900,4480,1238,1069,1263,1619]
AF_S = [14640304,14571066,11869042,12035044,10377877,14561957,27548522,30066779,8375926,7400312,8964449,11253445]
AF_M = [6357448,6572913,5258005,5212364,4622204,6653875,15392621,17552252,4043015,3513111,4289182,5410973]
HA_O = [199,205,165,114,168,257,248,224,203,221,430,431]
HA_S = [2297039,2427537,2716297,1880102,2337877,5638734,5789935,4418621,3643481,4193694,5941892,5531016]
HA_G = [568464,625740,759663,597509,761409,2059485,2169501,1641793,1281343,1389861,1705170,1506719]
LAB  = [3450000]*5 + [4200000,5407500,6798000] + [3553500]*4
UNIT, T2I, T2G, COLD = 7296, 128.84, 243.82, 10.0
RENT, GRENT = UNIT*T2I, UNIT*T2G
HA_T = T2I*0.2; AF_T = T2I-COLD-HA_T
avg = lambda a: sum(a)/len(a)
afm, hag, lab = avg(AF_M), avg(HA_G), avg(LAB)
afs, has_ = avg(AF_S), avg(HA_S)
cp = afm+hag-lab-RENT
MP = [a+b for a,b in zip(AF_M,HA_G)]
CPm = [m-l-RENT for m,l in zip(MP,LAB)]
labHV = 260000/(24*22); labS = 260000/(60*22)
SC = [
 dict(n='単純3PL', rev=6600+20*250, lab=20*labS, d='保管 6,600円＋出荷作業料 5,000円（20件）'),
 dict(n='高付加価値3PL', rev=60*800, lab=60*labHV, d='60件 × 800円（花オプション・同梱）'),
 dict(n='自社EC（AP&AF）', rev=afm/AF_T, lab=lab/AF_T, d='AND FLOWER 実績 ÷ 93.07坪'),
]
for s in SC: s['cp'] = s['rev']-s['lab']-UNIT
peak = max(AF_O); slack=[peak-o for o in AF_O]; slackAvg=avg(slack)
e1 = slackAvg*(800-labHV); haRun = avg(HA_G[-2:]); e2 = haRun-hag; eff = cp+e1+e2
q1,m1,q2,m2,p2,q3,m3,MGR = 6000,800,3000,2600,1200,40,3300,350000
g1=q1*(m1-labHV); g2=q2*(m2-p2)/12; g3=q3*m3; net=g1+g2+g3-MGR-GRENT; be1=(GRENT+MGR-g2-g3)/(m1-labHV)

fmt = lambda n: f"{round(n):,}"
def man(n, d=0):
    v = n/10000
    return (f"{v:,.{d}f}") + "万円"
def yen(n): return fmt(n)+"円"
def signed(n): return ("+" if n>=0 else "▲") + fmt(abs(n))

# ---------------- SVG グラフ ----------------
import math
def nice(x):
    p = 10**math.floor(math.log10(x)); f = x/p
    return (1 if f<=1 else 2 if f<=2 else 2.5 if f<=2.5 else 5 if f<=5 else 10)*p
def bars(w, h, labels, series, fmt_label, ymax=None, label_series=None, ylab=None, grid=4, line=None):
    """グループ棒グラフ。series=[(name, values, fill, stroke)]。棒の上に数値ラベル（§7）。
    line=(name, values, fmt) は破線の折れ線（末端に値）。"""
    ml, mr, mt, mb = 56, 40 if line else 8, 24, 28
    pw, ph = w-ml-mr, h-mt-mb
    allv = [v for _,vals,_,_ in series for v in vals] + (list(line[1]) if line else [])
    top = ymax or max(allv)*1.12
    step = nice(top/grid); ymax = math.ceil(top/step)*step
    ymin = min(0, min(allv))
    y = lambda v: mt + ph - (v-ymin)/(ymax-ymin)*ph
    n = len(labels); gw = pw/n; k = len(series); bw = gw*0.72/k
    o = [f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:auto;display:block" font-family="var(--font-en)" font-size="10">']
    for i in range(int(round(ymax/step))+1):
        v = i*step
        o.append(f'<line x1="{ml}" x2="{w-mr}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="var(--border-light)" stroke-width="1"/>')
        o.append(f'<text x="{ml-6}" y="{y(v)+3.5:.1f}" text-anchor="end" fill="var(--text-secondary)">{ylab(v) if ylab else fmt(v)}</text>')
    if ymin < 0:
        o.append(f'<line x1="{ml}" x2="{w-mr}" y1="{y(0):.1f}" y2="{y(0):.1f}" stroke="var(--text-secondary)" stroke-width="1"/>')
    for i,lb in enumerate(labels):
        o.append(f'<text x="{ml+gw*(i+.5):.1f}" y="{h-8}" text-anchor="middle" fill="var(--text-secondary)" font-family="var(--font-ja)">{lb}</text>')
    for si,(name,vals,fill,stroke) in enumerate(series):
        for i,v in enumerate(vals):
            x = ml + gw*i + gw*0.14 + si*bw
            y0, y1 = y(max(v,0)), y(min(v,0))
            st = f' stroke="{stroke}" stroke-width="1"' if stroke else ''
            o.append(f'<rect x="{x:.1f}" y="{y0:.1f}" width="{bw-2:.1f}" height="{max(y1-y0,0):.1f}" fill="{fill}"{st}/>')
            if label_series is None or si in label_series:
                ty = y0-4 if v>=0 else y1+11
                o.append(f'<text x="{x+(bw-2)/2:.1f}" y="{ty:.1f}" text-anchor="middle" fill="var(--text-primary)" font-weight="700" font-size="9.5">{fmt_label(v)}</text>')
    if line:
        name, vals, lf = line
        pts = " ".join(f"{ml+gw*(i+.5):.1f},{y(v):.1f}" for i,v in enumerate(vals))
        o.append(f'<polyline points="{pts}" fill="none" stroke="var(--text-secondary)" stroke-width="2" stroke-dasharray="6 4"/>')
        for i,v in enumerate(vals):
            o.append(f'<circle cx="{ml+gw*(i+.5):.1f}" cy="{y(v):.1f}" r="3" fill="var(--bg-white)" stroke="var(--text-secondary)" stroke-width="1.5"/>')
        o.append(f'<text x="{ml+gw*(n-.5)+8:.1f}" y="{y(vals[-1])+3.5:.1f}" fill="var(--text-secondary)" font-weight="700" font-size="9.5">{lf(vals[-1])}</text>')
    o.append('</svg>')
    return "\n".join(o)

def stacked(w, h, labels, base, top, fb, ft, ylab):
    """積み上げ棒。base（深緑）の上に top（灰）。base の値は境目の上、top の値は棒の上に置く。"""
    ml, mr, mt, mb = 56, 8, 24, 28
    pw, ph = w-ml-mr, h-mt-mb
    tot = max(a+b for a,b in zip(base,top))
    step = nice(tot*1.12/4); ymax = math.ceil(tot*1.12/step)*step
    y = lambda v: mt + ph - v/ymax*ph
    n = len(labels); gw = pw/n; bw = gw*0.56
    o = [f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:auto;display:block" font-family="var(--font-en)" font-size="10">']
    for i in range(int(round(ymax/step))+1):
        v = i*step
        o.append(f'<line x1="{ml}" x2="{w-mr}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="var(--border-light)" stroke-width="1"/>')
        o.append(f'<text x="{ml-6}" y="{y(v)+3.5:.1f}" text-anchor="end" fill="var(--text-secondary)">{ylab(v)}</text>')
    for i,lb in enumerate(labels):
        o.append(f'<text x="{ml+gw*(i+.5):.1f}" y="{h-8}" text-anchor="middle" fill="var(--text-secondary)" font-family="var(--font-ja)">{lb}</text>')
    for i,(a,b) in enumerate(zip(base,top)):
        x = ml + gw*i + (gw-bw)/2; cx = x+bw/2
        o.append(f'<rect x="{x:.1f}" y="{y(a):.1f}" width="{bw:.1f}" height="{y(0)-y(a):.1f}" fill="{fb}"/>')
        if b>0: o.append(f'<rect x="{x:.1f}" y="{y(a+b):.1f}" width="{bw:.1f}" height="{y(a)-y(a+b)-1.5:.1f}" fill="{ft}"/>')
        o.append(f'<text x="{cx:.1f}" y="{y(a)-4:.1f}" text-anchor="middle" fill="var(--text-primary)" font-weight="700" font-size="9.5">{a:,}</text>')
        if b>0: o.append(f'<text x="{cx:.1f}" y="{y(a+b)-4:.1f}" text-anchor="middle" fill="var(--text-secondary)" font-size="9.5">+{b:,}</text>')
    o.append('</svg>')
    return "\n".join(o)

def legend(items):
    return '<div class="legend">' + "".join(f'<span><i style="background:{c};{("border:1px solid var(--border-light);" if b else "")}"></i>{n}</span>' for n,c,b in items) + '</div>'

M1 = lambda v: f"{v/1e6:.1f}"
Mz = lambda v: f"{v/1e6:.0f}" if v>=1e6 or v==0 else f"{v/1e6:.1f}"
MOSS, GRAY, CREAM, LIGHT, WHITE = 'var(--brand-primary)','var(--bg-gray)','var(--bg-cream)','var(--bg-light)','var(--bg-white)'

c_af = bars(1016, 330, L, [('売上',AF_S,GRAY,None),('限界利益',AF_M,MOSS,None)], M1, ylab=Mz)
c_ha = bars(1016, 330, L, [('売上',HA_S,GRAY,None),('粗利',HA_G,MOSS,None)], M1, ylab=Mz)
c_cp = bars(660, 400, L, [('限界利益（AF＋ハナイチ）',MP,MOSS,None),('貢献利益',CPm,CREAM,'var(--border-light)')], M1, ylab=Mz, line=('人件費＋家賃',[l+RENT for l in LAB],M1))
c_cap = stacked(620, 400, L, AF_O, slack, MOSS, GRAY, lambda v: f"{round(v):,}")

def hbar_rows(rows, total, unit_fmt):
    """B-17 横棒（.hbars）。rows=[(label, value, cls)]。"""
    mx = max(abs(v) for _,v,_ in rows)
    o=[]
    for lb,v,cls in rows:
        o.append(f'<div class="hbar"><div class="hb-label">{lb}</div><div class="hb-track"><div class="hb-f {cls}" style="width:{abs(v)/mx*100:.1f}%"></div></div><div class="hb-total">{unit_fmt(v)}</div></div>')
    return "\n".join(o)

HD = '<div class="hd"><span>Domuz inc.</span><span>Confidential</span></div>'
pages = []
def page(body, cls=""):
    pages.append((cls, body))

# 1 表紙
page(f'''
  <div class="watermark">Domuz</div>
  <div class="cover-eyebrow">REPORT</div>
  <h1>ギフティ様<br>川崎倉庫の収益性試算</h1>
  <div class="cover-en">KAWASAKI WAREHOUSE ECONOMICS</div>
  <div class="cover-rule"></div>
  <div class="cover-meta">2026年10月13日<br>株式会社Domuz　代表取締役　髙木 弘貴</div>
  <div class="cover-brand en">AND FLOWER / HANAICHI</div>
''', "cover")

# 2 サマリー（B-7）
page(f'''
  {HD}
  <div class="sec-label">- SUMMARY -</div>
  <h2 class="page-title">結論：2I は稼いでいる。閑散月を埋め、2G は「埋め方」が決まれば借りる</h2>
  <p class="page-title-sub">ラポール川崎SRC 2階の 2I 区画（128.84坪）を1つの器として見たときの収益性を、確定している数字と FY2026（2025年10月〜2026年9月）の実績から積み上げました。単位は円・税抜・月次です。</p>
  <div class="body">
  <div class="kpis">
    <div class="kpi"><div class="label">2I の貢献利益（FY2026 平均）</div><div class="num">{cp/1e4:,.0f}<small>万円/月</small></div><div class="desc">年 {man(cp*12)}。家賃 94万円の {cp/RENT:.1f}倍、{fmt(cp/T2I)}円/坪/月</div></div>
    <div class="kpi"><div class="label">効率化後の 2I 貢献利益</div><div class="num">{eff/1e4:,.0f}<small>万円/月</small></div><div class="desc">閑散月の空き能力を高付加価値3PLで埋め、ハナイチを直近水準に</div></div>
    <div class="kpi"><div class="label">2G を借りた場合の増分</div><div class="num">+{net/1e4:,.0f}<small>万円/月</small></div><div class="desc">追加家賃 {man(GRENT)} を引いた後。高付加価値3PL だけなら損益分岐 {fmt(be1)}件/月</div></div>
  </div>
  <div class="box" style="margin-top:32px">
    <ul class="dots">
      <li><b>2I は家賃と人件費を引いても貢献利益が出ている。</b>FY2026 実績で月約{cp/1e4:,.0f}万円。ただし母の日の2か月に偏り、閑散月は家賃と人件費をまかなう程度。</li>
      <li><b>同じ1坪でも用途で収益は大きく変わる。</b>単純3PL は +{fmt(SC[0]['cp'])}円/坪/月、高付加価値3PL は +{SC[1]['cp']/1e4:.1f}万円、自社EC（AP&amp;AF）は +{SC[2]['cp']/1e4:.1f}万円。単純3PL に床は使わない。</li>
      <li><b>今後は「閑散月を埋める」と「2G で床を増やす」の2段。</b>2I のままでも月約{eff/1e4:,.0f}万円まで。2G は高付加価値3PL と AF の繁忙期増産で埋めれば、追加家賃を引いてもプラス。</li>
    </ul>
  </div>
  </div>
  <p class="note">限界利益＝売上−花材・資材・送料（AND FLOWER）。粗利＝売上−仕入（ハナイチ）。貢献利益＝限界利益（粗利）−拠点人件費−家賃。出典：受注管理システムの売上サマリー、ハナイチ管理画面、事業計画 AP/AF 202610（人件費の計画値）。</p>
''')

# 3 章扉 01
page('''
  <div class="num">01</div>
  <div class="title-en">Current State</div>
  <div class="title-ja">現状の整理 — 借りている床と、その使い方</div>
''', "divider")

# 4 区画図
page(f'''
  {HD}
  <div class="sec-label">- FLOOR PLAN -</div>
  <h2 class="page-title">2階フロアで 2I を借りている。2D の一部をギフティ様が利用予定、2G は交渉中</h2>
  <p class="page-title-sub">区画の坪数は図面の専有面積。坪単価は 2I の契約値 7,296円で、2G は同単価で仮置きしています。</p>
  <div class="body top">
  <div class="cols" style="gap:32px">
    <div class="col" style="flex:1.45">
      <div class="plan im-plan">
        <div class="ov dash" style="left:3.6%;top:36%;width:30.8%;height:14.6%"><span class="badge alt">2G　243.82坪 ・ 交渉中</span></div>
        <div class="ov solid" style="left:3.4%;top:60%;width:8.5%;height:38.5%"><span class="badge">2I　128.84坪 ・ 当社利用中</span></div>
        <div class="ov fill" style="left:57.2%;top:83.5%;width:8.4%;height:12.7%"><span class="badge alt">2D の一部 ・ ギフティ様 利用予定</span></div>
      </div>
      <p class="note">2I と 2G は同じフロアの左側で隣接し、2G は 2I の約1.9倍。2D（384.27坪）のうちギフティ様が使う部分の坪数は要確認。</p>
    </div>
    <div class="col">
      <table>
        <thead><tr><th>区画</th><th class="num">坪</th><th class="num">坪単価</th><th class="num">月額</th></tr></thead>
        <tbody>
          <tr><td>2I（当社・現在）</td><td class="num">128.84</td><td class="num">7,296</td><td class="num">{fmt(RENT)}</td></tr>
          <tr><td>　うち冷蔵庫 <span class="badge alt">坪数は要確認</span></td><td class="num">10.00</td><td class="num">7,296</td><td class="num">{fmt(UNIT*COLD)}</td></tr>
          <tr><td>2G（交渉中・同単価で仮置き）</td><td class="num">243.82</td><td class="num">7,296</td><td class="num">{fmt(GRENT)}</td></tr>
          <tr class="total"><td>2I ＋ 2G</td><td class="num">372.66</td><td class="num">7,296</td><td class="num">{fmt(RENT+GRENT)}</td></tr>
          <tr><td>2D の一部（ギフティ様）</td><td class="num">要確認</td><td class="num">—</td><td class="num">—</td></tr>
        </tbody>
      </table>
      <p class="note r">単位：円・月次・税抜</p>
      <p class="note">年額では 2I 1,128万円、2G 2,135万円。2G の坪単価・契約条件は提示待ちで、確定したら置き換えます。</p>
    </div>
  </div>
  </div>
''')

# 5 2I の使い方
now = [('冷蔵庫',COLD,'w','生花の鮮度保持（固定設備、坪数は要確認）'),('ハナイチ',HA_T,'m','生花の在庫・出荷（2I の20%を上限）'),('AND FLOWER',AF_T,'c','ブーケ制作、梱包、資材、出荷待ち、イネイブラー同梱')]
seg = "".join(f'<div class="seg {c}" style="flex:{v}"><span>{n} {v:.0f}坪</span></div>' for n,v,c,_ in now)
rows = "".join(f'<tr><td><i class="sw {c}"></i>{n}</td><td class="num">{v:.2f}</td><td class="num">{v/T2I*100:.0f}%</td><td class="num">{fmt(v*UNIT)}</td><td>{d}</td></tr>' for n,v,c,d in now)
page(f'''
  {HD}
  <div class="sec-label">- HOW WE USE 2I -</div>
  <h2 class="page-title">2I の 128.84坪は、冷蔵庫・ハナイチ（上限20%）・AND FLOWER で使っている</h2>
  <p class="page-title-sub">面積の配分ルール：冷蔵庫10坪は固定設備、ハナイチは 2I 全体の20%まで、残りは AND FLOWER（制作・梱包・資材・出荷待ち）。</p>
  <div class="body top">
  <div class="stackbar">{seg}</div>
  <table style="margin-top:28px">
    <thead><tr><th>用途</th><th class="num">坪</th><th class="num">比率</th><th class="num">家賃相当/月（円）</th><th>主な中身</th></tr></thead>
    <tbody>{rows}<tr class="total"><td>合計</td><td class="num">{T2I:.2f}</td><td class="num">100%</td><td class="num">{fmt(RENT)}</td><td></td></tr></tbody>
  </table>
  <div class="box" style="margin-top:28px">
    <ul class="dots">
      <li>床を使う主体は AND FLOWER の発送（ブーケ制作、梱包、資材、出荷待ち）。イネイブラー案件（パパブブレ等の同梱）も同じ作業スペースを使う。</li>
      <li>ハナイチは生花の在庫と出荷で、2I 全体の20%を上限に使う。超える分は AND FLOWER の床を圧迫するため、この上限で運用する。</li>
      <li>冷蔵庫だけが固定設備で、ほかは繁閑で入れ替わる。母の日の2か月は資材と出荷待ちが通路まで広がり、閑散期は作業台が空く。</li>
    </ul>
  </div>
  </div>
''')

# 6 章扉 02
page('''
  <div class="num">02</div>
  <div class="title-en">Current Performance</div>
  <div class="title-ja">現状の分析 — 2I から出ている売上と利益</div>
''', "divider")

# 7 AF
page(f'''
  {HD}
  <div class="sec-label">- AND FLOWER -</div>
  <h2 class="page-title">AND FLOWER は 2I から年 {sum(AF_S)/1e8:.2f}億円を出荷。限界利益は年 {sum(AF_M)/1e6:,.0f}百万円</h2>
  <p class="page-title-sub">FY2026（2025年10月〜2026年9月）の月次実績。注文日ベース・税抜。限界利益＝売上−花材・資材・送料。</p>
  <div class="body top">
  {legend([('売上',GRAY,False),('限界利益',MOSS,False)])}
  {c_af}
  <p class="note r">単位：百万円/月</p>
  <div class="kpis" style="margin-top:12px">
    <div class="kpi"><div class="label">年間売上</div><div class="num">{sum(AF_S)/1e8:.2f}<small>億円</small></div><div class="desc">月平均 {man(afs)}</div></div>
    <div class="kpi"><div class="label">年間限界利益</div><div class="num">{sum(AF_M)/1e6:,.0f}<small>百万円</small></div><div class="desc">限界利益率 {sum(AF_M)/sum(AF_S)*100:.0f}%、月平均 {man(afm)}</div></div>
    <div class="kpi"><div class="label">年間注文数</div><div class="num">{sum(AF_O):,}<small>件</small></div><div class="desc">最大月 5月 {max(AF_O):,}件、最小月 7月 {min(AF_O):,}件</div></div>
    <div class="kpi"><div class="label">繁閑差（限界利益）</div><div class="num">{max(AF_M)/min(AF_M):.1f}<small>倍</small></div><div class="desc">母の日月 ÷ 閑散月</div></div>
  </div>
  </div>
  <p class="note">受注管理システムの売上サマリー（AND FLOWER ブランド＝生花・ドライフラワー・スタンド花・胡蝶蘭など）。拠点を通らない直送品（スタンド花・胡蝶蘭の一部）を含む可能性があり、拠点通過分に絞る場合は下振れします。</p>
''')

# 8 ハナイチ
page(f'''
  {HD}
  <div class="sec-label">- HANAICHI -</div>
  <h2 class="page-title">ハナイチは年 {sum(HA_S)/1e6:,.0f}百万円を出荷。直近2か月は注文数が2倍の水準</h2>
  <p class="page-title-sub">FY2026（2025年10月〜2026年9月）の月次実績。注文日ベース・税抜。粗利＝売上−仕入。</p>
  <div class="body top">
  {legend([('売上',GRAY,False),('粗利',MOSS,False)])}
  {c_ha}
  <p class="note r">単位：百万円/月</p>
  <div class="kpis" style="margin-top:12px">
    <div class="kpi"><div class="label">年間売上</div><div class="num">{sum(HA_S)/1e6:,.0f}<small>百万円</small></div><div class="desc">月平均 {man(has_)}</div></div>
    <div class="kpi"><div class="label">年間粗利</div><div class="num">{sum(HA_G)/1e6:,.1f}<small>百万円</small></div><div class="desc">粗利率 {sum(HA_G)/sum(HA_S)*100:.0f}%、月平均 {man(hag)}</div></div>
    <div class="kpi"><div class="label">年間注文数</div><div class="num">{sum(HA_O):,}<small>件</small></div><div class="desc">8〜9月は月 {HA_O[-1]}件、FY 前半の約2倍</div></div>
    <div class="kpi"><div class="label">直近2か月の粗利</div><div class="num">{haRun/1e4:,.0f}<small>万円/月</small></div><div class="desc">FY2026 平均 {man(hag)} に対し +{man(e2)}</div></div>
  </div>
  </div>
  <p class="note">ハナイチ管理画面の売上推移。繁閑差（粗利の最大月 ÷ 最小月）は {max(HA_G)/min(HA_G):.1f}倍。</p>
''')

# 9 貢献利益
page(f'''
  {HD}
  <div class="sec-label">- CONTRIBUTION -</div>
  <h2 class="page-title">2I の貢献利益は月約{cp/1e4:,.0f}万円。坪あたりでは AND FLOWER {SC[2]['cp']/1e4:.1f}万円、ハナイチ {(hag/HA_T-UNIT)/1e4:.1f}万円</h2>
  <p class="page-title-sub">貢献利益＝限界利益（粗利）−拠点人件費−家賃。人件費は AND FLOWER 発送アルバイトの月次計画値。ハナイチの拠点人件費は未反映。</p>
  <div class="body top">
  <div class="cols" style="gap:32px">
    <div class="col" style="flex:1.5">
      {legend([('限界利益（AF＋ハナイチ）',MOSS,False),('貢献利益',CREAM,True)])[:-6]}<span><i style="height:0;border-top:2px dashed var(--text-secondary);border-radius:0"></i>人件費＋家賃</span></div>
      {c_cp}
      <p class="note r">単位：百万円/月</p>
      <p class="note">4〜5月は母の日。閑散月（6〜7月、1〜2月）の貢献利益は100万円を割り、家賃と人件費をまかなう程度。</p>
    </div>
    <div class="col">
      <table>
        <thead><tr><th>円/坪/月</th><th class="num">AND FLOWER</th><th class="num">ハナイチ</th><th class="num">2I 全体</th></tr></thead>
        <tbody>
          <tr><td>限界利益（粗利）</td><td class="num">{fmt(afm/AF_T)}</td><td class="num">{fmt(hag/HA_T)}</td><td class="num">{fmt((afm+hag)/T2I)}</td></tr>
          <tr><td>拠点人件費</td><td class="num">▲{fmt(lab/AF_T)}</td><td class="num">未反映</td><td class="num">▲{fmt(lab/T2I)}</td></tr>
          <tr><td>家賃</td><td class="num">▲7,296</td><td class="num">▲7,296</td><td class="num">▲7,296</td></tr>
          <tr class="total"><td>貢献利益</td><td class="num">{fmt((afm-lab)/AF_T-UNIT)}</td><td class="num">{fmt(hag/HA_T-UNIT)}</td><td class="num">{fmt(cp/T2I)}</td></tr>
          <tr><td>使っている坪数</td><td class="num">{AF_T:.2f}</td><td class="num">{HA_T:.2f}</td><td class="num">{T2I:.2f}</td></tr>
          <tr><td>月次の貢献利益（合計）</td><td class="num">{man((afm-lab)-UNIT*AF_T)}</td><td class="num">{man(hag-UNIT*HA_T)}</td><td class="num"><b>{man(cp)}</b></td></tr>
        </tbody>
      </table>
      <p class="note">AND FLOWER は 93.07坪、ハナイチは 25.77坪で割っている。2I 全体は冷蔵庫を含む 128.84坪で割った値。ハナイチは拠点人件費が未反映のため上振れしている。FY2026 平均。</p>
    </div>
  </div>
  </div>
''')

# 10 章扉 03
page('''
  <div class="num">03</div>
  <div class="title-en">Scenarios</div>
  <div class="title-ja">収益性の試算 — 単純3PL／高付加価値3PL／自社EC（AP&AF）</div>
''', "divider")

# 11 3用途
hb = hbar_rows([(s['n'], s['cp'], 'w') for s in SC], None, lambda v: ("+" if v>=0 else "▲")+fmt(abs(v)))
page(f'''
  {HD}
  <div class="sec-label">- PER TSUBO -</div>
  <h2 class="page-title">同じ1坪でも、単純3PL +{fmt(SC[0]['cp'])}円、高付加価値3PL +{SC[1]['cp']/1e4:.1f}万円、自社EC +{SC[2]['cp']/1e4:.1f}万円</h2>
  <p class="page-title-sub">3つの用途を「1坪・1か月の貢献利益」で比べます。単純3PL と高付加価値3PL は前提値、自社EC（AP&AF）は AND FLOWER の FY2026 実績です。</p>
  <div class="body top">
  <div class="cols" style="gap:32px">
    <div class="col" style="flex:1.3">
      <table>
        <thead><tr><th>円/坪/月</th><th class="num">単純3PL</th><th class="num">高付加価値3PL</th><th class="num">自社EC（AP&AF）</th></tr></thead>
        <tbody>
          <tr><td>限界利益</td>{"".join(f'<td class="num">{fmt(s["rev"])}</td>' for s in SC)}</tr>
          <tr><td>拠点人件費</td>{"".join(f'<td class="num">▲{fmt(s["lab"])}</td>' for s in SC)}</tr>
          <tr><td>家賃</td>{"".join('<td class="num">▲7,296</td>' for s in SC)}</tr>
          <tr class="total"><td>貢献利益</td>{"".join(f'<td class="num">{("+" if s["cp"]>=0 else "▲")+fmt(abs(s["cp"]))}</td>' for s in SC)}</tr>
          <tr><td>限界利益は家賃の何倍か</td>{"".join(f'<td class="num">{s["rev"]/UNIT:.1f}倍</td>' for s in SC)}</tr>
          <tr><td>限界利益の中身</td>{"".join(f'<td><span class="sub" style="font-size:10.5px;line-height:1.5;display:block">{s["d"]}</span></td>' for s in SC)}</tr>
        </tbody>
      </table>
    </div>
    <div class="col">
      <h3 style="margin-bottom:16px">貢献利益（円/坪/月）</h3>
      <div class="hbars hbars-wide">{hb}</div>
      <div class="box" style="margin-top:20px">
        <p style="font-size:12px">単純3PL は家賃をようやく賄う水準。保管単価が1割下がれば赤字になる。高付加価値3PL は作業が付く分だけ坪あたり貢献が大きく、自社EC は商品の粗利を含むため最も高い。</p>
      </div>
    </div>
  </div>
  <p class="note" style="margin-top:24px"><b>前提。</b>単純3PL：保管 3,300円/パレット/月 × 2パレット/坪、出荷作業料 250円/件 × 20件/坪/月、作業 60件/人/日（アルバイト26万円/人月・22日 → 197円/件）。高付加価値3PL：ギフト同梱・花オプション付き、限界利益 800円/件（保冷実費除く）× 60件/坪/月、作業 24件/人/日（→ 492円/件）。自社EC（AP&AF）：AND FLOWER の限界利益・人件費を 93.07坪で割った実績値で、商品の粗利を含むためサービス料だけの3PLとは性質が異なる。</p>
  </div>
''')

# 12 2Gに当てはめた場合
cond = ['2パレット/坪が常時埋まり、出荷 20件/坪/月。保管単価が1割下がると赤字','月 14,600件（60件/坪 × 243.82坪）の高付加価値案件の受注が前提','AND FLOWER の平均密度（22件/坪/月）で床が埋まる需要が前提。繁閑差5倍のため年間では成立しない']
page(f'''
  {HD}
  <div class="sec-label">- IF APPLIED TO 2G -</div>
  <h2 class="page-title">同じ用途を 2G（243.82坪）に当てはめると、月額の貢献利益はこう変わる</h2>
  <p class="page-title-sub">前ページの「1坪あたり貢献利益」に 2G の坪数を掛けた値。実際に成立するかは、右の条件を満たす需要があるかで決まります。</p>
  <div class="body">
  <div class="kpis">
    {"".join(f'<div class="kpi"><div class="label">{s["n"]}</div><div class="num">{("+" if s["cp"]>=0 else "▲")}{abs(s["cp"])*T2G/1e4:,.0f}<small>万円/月</small></div><div class="desc">年 {man(abs(s["cp"])*T2G*12)}</div></div>' for s in SC)}
  </div>
  <table style="margin-top:28px">
    <thead><tr><th>用途</th><th class="num">月額（円）</th><th class="num">年額（円）</th><th>成立条件</th></tr></thead>
    <tbody>
      {"".join(f'<tr><td>{s["n"]}</td><td class="num">{signed(s["cp"]*T2G)}</td><td class="num">{signed(s["cp"]*T2G*12)}</td><td style="font-size:11.5px">{c}</td></tr>' for s,c in zip(SC,cond))}
    </tbody>
  </table>
  <p class="note r">単位：円・税抜。2G の家賃は 7,296円/坪で仮置き</p>
  </div>
''')

# 13 章扉 04
page('''
  <div class="num">04</div>
  <div class="title-en">Next Steps</div>
  <div class="title-ja">今後 — 閑散月を埋める効率化と、2G の拡張</div>
''', "divider")

# 14 効率化
page(f'''
  {HD}
  <div class="sec-label">- EFFICIENCY -</div>
  <h2 class="page-title">2I のままでも、閑散月の空き能力を埋めれば貢献利益は月約{eff/1e4:,.0f}万円まで伸びる</h2>
  <p class="page-title-sub">効率化の2つの打ち手。① 母の日の出荷能力（{peak:,}件/月）に対する閑散月の空きを高付加価値3PLで埋める。② ハナイチを直近2か月の水準で回す。</p>
  <div class="body top">
  <div class="cols" style="gap:32px">
    <div class="col" style="flex:1.35">
      {legend([('AND FLOWER 注文数',MOSS,False),('空き能力（出荷能力 4,480件 との差）',GRAY,False)])}
      {c_cap}
      <p class="note r">単位：件/月</p>
      <p class="note">空き能力＝母の日の最大月（2026年5月、{peak:,}件）− 各月の実績。年間 {sum(slack):,}件、月平均 {fmt(slackAvg)}件分の作業能力が空いている。</p>
    </div>
    <div class="col">
      <table>
        <thead><tr><th>項目</th><th class="num">月額（円）</th><th class="num">年額（円）</th></tr></thead>
        <tbody>
          <tr><td>現状の貢献利益（FY2026 平均）</td><td class="num">{fmt(cp)}</td><td class="num">{fmt(cp*12)}</td></tr>
          <tr><td>① 空き能力を高付加価値3PLで埋める<span class="sub">{fmt(slackAvg)}件 × 1件あたり貢献 {fmt(800-labHV)}円</span></td><td class="num">+{fmt(e1)}</td><td class="num">+{fmt(e1*12)}</td></tr>
          <tr><td>② ハナイチを直近2か月の粗利水準に<span class="sub">{man(haRun)} − {man(hag)}（20%の床の中で成立）</span></td><td class="num">+{fmt(e2)}</td><td class="num">+{fmt(e2*12)}</td></tr>
          <tr class="total"><td>効率化後の 2I 貢献利益</td><td class="num">{fmt(eff)}</td><td class="num">{fmt(eff*12)}</td></tr>
          <tr><td>坪あたり（128.84坪）<span class="sub">円/坪/月、家賃との比</span></td><td class="num">{fmt(eff/T2I)}</td><td class="num">{eff/RENT:.1f}倍</td></tr>
        </tbody>
      </table>
      <p class="note">1件あたり貢献 = 限界利益 800円 − 人件費 492円（24件/人/日）。</p>
    </div>
  </div>
  </div>
''')

# 15 2G
nx = [('冷蔵',30,'w'),('保管',110,'m'),('AF 制作・梱包',80,'c'),('高付加価値3PL',90,'o'),('通路・撮影・事務',62.66,'l')]
seg2 = "".join(f'<div class="seg {c}" style="flex:{v}"><span>{n}　{v:.0f}坪</span></div>' for n,v,c in nx)
rows2 = [('① 高付加価値3PL（6,000件/月 × '+fmt(m1-labHV)+'円）',g1),('② AF 繁忙期の追加出荷 3,000件（月額換算）',g2),('③ 預かり在庫の保管売上（40パレット）',g3),('2G 管理者 1名',-MGR),('2G 追加家賃（7,296円 × 243.82坪）',-GRENT)]
page(f'''
  {HD}
  <div class="sec-label">- 2G EXPANSION -</div>
  <h2 class="page-title">2G を借りると 372.66坪。高付加価値3PL と AF の繁忙期増産で埋めれば、追加家賃を引いてもプラス</h2>
  <p class="page-title-sub">判断基準はひとつ。2G を借りて増える貢献利益が、2G の追加家賃（{man(GRENT)}/月）を上回るか。単純3PL では床を使うほど赤字になるため、2G には使いません。</p>
  <div class="body top">
  <div class="stackbar">{seg2}</div>
  <p class="note">2I＋2G の用途内訳（372.66坪・配置案）。2G の管理者1名（35万円/月）を固定費として控除。設備・什器・原状回復は含みません。</p>
  <div class="cols" style="gap:32px;margin-top:20px">
    <div class="col" style="flex:1.4">
      <table>
        <thead><tr><th>2G を借りた場合の増分</th><th class="num">月額（円）</th><th class="num">年額（円）</th></tr></thead>
        <tbody>
          {"".join(f'<tr><td>{n}</td><td class="num">{signed(v)}</td><td class="num">{signed(v*12)}</td></tr>' for n,v in rows2)}
          <tr class="total"><td>貢献利益の増分</td><td class="num">{signed(net)}</td><td class="num">{signed(net*12)}</td></tr>
        </tbody>
      </table>
    </div>
    <div class="col">
      <div class="box outline">
        <span class="tag moss">判定</span>
        <h3>借りてよい</h3>
        <p>貢献利益ベースで月 {man(net)} のプラス。2I の効率化と合わせると拠点全体で月 {man(eff+net)}。</p>
        <p style="margin-top:10px">高付加価値3PL だけで追加家賃と管理者を回収する場合の損益分岐は <b class="strong">{fmt(be1)}件/月</b>（1件あたり貢献 {fmt(m1-labHV)}円）。</p>
      </div>
      <p class="note">① 平常月 6,000件、1件あたり貢献 308円。② 母の日2か月で AF を 3,000件増産（限界利益 2,600円、人件費 1,200円/件）し、12で割って月額化。③ 預かり在庫 40パレット × 3,300円。</p>
    </div>
  </div>
  </div>
''')

# 16 まとめ
page(f'''
  {HD}
  <div class="sec-label">- CONCLUSION -</div>
  <h2 class="page-title">まとめと、次に確定する数字</h2>
  <p class="page-title-sub">この資料の数字は、仮置きの坪数と前提値を含みます。右の項目が確定したら、そのまま置き換えて更新します。</p>
  <div class="body top">
  <div class="cards">
    <div class="card cream">
      <h3>結論</h3>
      <ul class="dots">
        <li><b>現状。</b>2I の貢献利益は FY2026 で月約{cp/1e4:,.0f}万円（年{man(cp*12)}）、家賃の{cp/RENT:.1f}倍。AND FLOWER が床の7割を使って月{afm/1e4:,.0f}万円の限界利益、ハナイチが2割で月{hag/1e4:,.0f}万円の粗利。</li>
        <li><b>用途の選び方。</b>1坪あたり貢献利益は 単純3PL +{fmt(SC[0]['cp'])}円 ＜ 高付加価値3PL +{SC[1]['cp']/1e4:.1f}万円 ＜ 自社EC +{SC[2]['cp']/1e4:.1f}万円。単純3PL に床は使わない。</li>
        <li><b>効率化。</b>閑散月の空き能力（月{fmt(slackAvg)}件）を高付加価値3PLで埋め、ハナイチを直近水準にすると、2I のままで月約{eff/1e4:,.0f}万円。</li>
        <li><b>2G。</b>高付加価値3PL 6,000件/月、母の日の増産、預かり在庫 40パレットで埋めれば追加家賃を引いて月約{net/1e4:,.0f}万円のプラス。高付加価値3PL だけなら約{fmt(be1)}件/月が分岐点。</li>
      </ul>
    </div>
    <div class="card">
      <h3>次に確定する数字</h3>
      <ul class="dots">
        <li>冷蔵庫と各用途の実測坪数（P.5 の配分を置き換える）</li>
        <li>2G の提示坪単価・契約期間・原状回復条件</li>
        <li>2D のうちギフティ様が利用する坪数と、共同で使える設備（冷蔵・作業台）の有無</li>
        <li>高付加価値3PL の受注見込み件数（平常月ベース）と1件あたり単価</li>
        <li>AND FLOWER の拠点通過分の売上（直送品を除いた値）と、9月試算表の部門別人件費</li>
      </ul>
    </div>
  </div>
  </div>
''')

# ---------------- HTML 組み立て ----------------
secs = []
for i,(cls,body) in enumerate(pages, 1):
    ft = '' if cls == 'divider' else f'<div class="ft"><span>Copyright (C) Domuz inc, All Rights Reserved.</span><span>{i}</span></div>'
    secs.append(f'<section class="page {cls}">{body}{ft}</section>')

html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>ギフティ様_川崎倉庫の収益性試算_20261013</title>
<!-- OUT: {OUT_NAME} -->
<!--
  Domuz デザインシステム v2.1 準拠（proposal-materials/.claude/knowledge/design_system/domuz_design_system.md）。
  4:3 1128×846px。1 <section class="page"> = 1スライド。色は var(--…) のみ。
  このファイルは gen_src.py が生成する。数字・グラフを直すときは gen_src.py を直して再生成し、
  `python3 build.py --pdf` で最終HTML/PDFを作る。
-->
<style>
  /* @@BASE@@ */

  /* ===== この資料だけの型 ===== */
  .plan {{ position: relative; width: 100%; aspect-ratio: 1722 / 790; border-radius: 6px; overflow: hidden;
          background-color: var(--bg-white); background-size: contain; background-repeat: no-repeat; background-position: center; border: 1px solid var(--border-light); }}
  .ov {{ position: absolute; box-sizing: border-box; border-radius: 3px; }}
  .ov.solid {{ border: 2.5px solid var(--border-strong); background: rgba(0,67,71,0.14); }}
  .ov.dash  {{ border: 2px dashed var(--border-strong); background: rgba(0,67,71,0.06); }}
  .ov.fill  {{ border: 2px solid var(--text-secondary); background: rgba(203,208,211,0.55); }}
  .ov > .badge {{ position: absolute; left: -2px; top: -2px; transform: translateY(-100%); white-space: nowrap; margin-bottom: 0; }}
  .stackbar {{ display: flex; width: 100%; height: 56px; border-radius: var(--radius); overflow: hidden; border: 1px solid var(--border-light); }}
  .stackbar .seg {{ display: flex; align-items: center; justify-content: center; min-width: 0; overflow: hidden; white-space: nowrap; font-size: 11.5px; font-weight: 600; letter-spacing: 0; }}
  table th {{ white-space: nowrap; }}
  .stackbar .seg + .seg {{ border-left: 2px solid var(--bg-white); }}
  .seg.w, .sw.w {{ background: var(--brand-primary); color: var(--text-on-fill); }}
  .seg.m, .sw.m {{ background: var(--bg-gray); color: var(--text-primary); }}
  .seg.c, .sw.c {{ background: var(--bg-cream); color: var(--text-primary); }}
  .seg.o, .sw.o {{ background: var(--bg-white); color: var(--text-primary); box-shadow: inset 0 0 0 1.5px var(--border-strong); }}
  .seg.l, .sw.l {{ background: var(--bg-light); color: var(--text-primary); }}
  .sw {{ display: inline-block; width: 12px; height: 12px; border-radius: 2px; margin-right: 8px; vertical-align: -1px; border: 1px solid var(--border-light); }}
  .hbars-wide .hb-label {{ width: 128px; }}
  .hbars-wide .hb-total {{ width: 84px; }}
  .kpi .num {{ white-space: nowrap; font-size: 56px; }}
  .kpi .num small {{ font-family: var(--font-ja); }}
  table td.num {{ white-space: nowrap; }}
  table td .sub {{ font-weight: 400; }}
  .note.r {{ text-align: right; margin-top: 6px; }}
</style>
</head>
<body>

{chr(10).join(secs)}

</body>
</html>
'''
os.makedirs(os.path.join(ROOT,'src'), exist_ok=True)
with open(os.path.join(ROOT,'src','giftee_kawasaki.src.html'),'w',encoding='utf-8') as f:
    f.write(html)
print("wrote src/giftee_kawasaki.src.html", len(pages), "pages")
