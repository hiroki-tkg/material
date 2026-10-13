#!/usr/bin/env python3
"""ギフティ様向け「川崎倉庫の収益性試算」を、事業エコノミクス資料（発表スライド型・4:3・左色帯）と
同じ見た目で生成する。数字とグラフ（インラインSVG）はここで計算する。
実行: python3 gen_deck.py  → giftee_kawasaki_economics_2026-10.html
"""
import os, json, math, re
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'giftee_kawasaki_economics_2026-10.html')
PLAN = json.load(open(os.path.join(ROOT, '..', 'assets', 'images.json')))['plan']
# 2I 周辺（左端〜2H あたり、2G の下〜下端）を切り抜く
import base64, io
from PIL import Image
_im = Image.open(io.BytesIO(base64.b64decode(PLAN.split(',',1)[1])))
CROP = (30, 455, 282, 790)  # 元画像 1722×790 のうち 2I とエレベーター（x30–282, y455–790）
_buf = io.BytesIO(); _im.crop(CROP).save(_buf, 'WEBP', quality=88)
PLAN_2I = 'data:image/webp;base64,' + base64.b64encode(_buf.getvalue()).decode()
CROP_W, CROP_H = CROP[2]-CROP[0], CROP[3]-CROP[1]
def pct(x0,y0,x1,y1):
    return f"left:{(x0-CROP[0])/CROP_W*100:.1f}%;top:{(y0-CROP[1])/CROP_H*100:.1f}%;width:{(x1-x0)/CROP_W*100:.1f}%;height:{(y1-y0)/CROP_H*100:.1f}%"

# ---------------- 数字（FY2026 = 2025/10〜2026/9） ----------------
L = ['10','11','12','1','2','3','4','5','6','7','8','9']
AF_O = [2143,1882,1613,1721,1420,2078,3900,4480,1238,1069,1263,1619]
AF_S = [14640304,14571066,11869042,12035044,10377877,14561957,27548522,30066779,8375926,7400312,8964449,11253445]
AF_M = [6357448,6572913,5258005,5212364,4622204,6653875,15392621,17552252,4043015,3513111,4289182,5410973]
HA_O = [199,205,165,114,168,257,248,224,203,221,430,431]
HA_S = [2297039,2427537,2716297,1880102,2337877,5638734,5789935,4418621,3643481,4193694,5941892,5531016]
HA_G = [568464,625740,759663,597509,761409,2059485,2169501,1641793,1281343,1389861,1705170,1506719]
LAB  = [3450000]*5 + [4200000,5407500,6798000] + [3553500]*4
UNIT, T2I, T2G, COLD = 7296, 128.84, 243.82, 18.0  # 冷蔵庫（キーパー）59.52㎡ ＝ 6.4m × 9.3m ≒ 18 坪
RENT, GRENT = UNIT*T2I, UNIT*T2G
HA_T = T2I*0.2; AF_T = T2I-COLD-HA_T
avg = lambda a: sum(a)/len(a)
afm, hag, lab, afs, has_ = avg(AF_M), avg(HA_G), avg(LAB), avg(AF_S), avg(HA_S)
cp = afm+hag-lab-RENT
MP = [a+b for a,b in zip(AF_M,HA_G)]; CPm = [m-l-RENT for m,l in zip(MP,LAB)]
labHV = 260000/(24*22); labS = 260000/(60*22)
SC = [dict(n='汎用3PL', rev=6600+20*250, lab=20*labS, d='保管 6,600円＋出荷作業料 5,000円（20件）'),
      dict(n='高付加価値3PL', rev=60*800, lab=60*labHV, d='60件 × 800円（花オプション・同梱）'),
      dict(n='自社EC（AP&AF）', rev=afm/AF_T, lab=lab/AF_T, d=f'AND FLOWER 実績 ÷ {AF_T:.2f}坪')]
for s in SC: s['cp'] = s['rev']-s['lab']-UNIT
peak = max(AF_O); slack = [peak-o for o in AF_O]; slackAvg = avg(slack)
e1 = slackAvg*(800-labHV); haRun = avg(HA_G[-2:]); e2 = haRun-hag; eff = cp+e1+e2
q1,m1,q2,m2,p2,q3,m3,MGR = 6000,800,3000,2600,1200,40,3300,350000
g1=q1*(m1-labHV); g2=q2*(m2-p2)/12; g3=q3*m3; net=g1+g2+g3-MGR-GRENT; be1=(GRENT+MGR-g2-g3)/(m1-labHV)

fmt = lambda n: f"{round(n):,}"
def man(n, d=0): return f"{n/10000:,.{d}f}万円"
def M(n, d=1): return f"{n/1e6:,.{d}f}"
def sg(n): return ("+" if n>=0 else "▲") + fmt(abs(n))
def tri(n, d=1): return (f"{n/1e6:,.{d}f}" if n>=0 else f"▲{abs(n)/1e6:,.{d}f}")

MOSS, MINT, PINK, YEL, GRAY, LINE, LIGHT, RED = 'var(--moss)','var(--mint)','var(--pink)','var(--yellow)','var(--gray)','var(--line)','var(--light)','var(--red)'

# ---------------- SVG ----------------
def nice(x):
    p = 10**math.floor(math.log10(x)); f = x/p
    return (1 if f<=1 else 2 if f<=2 else 2.5 if f<=2.5 else 5 if f<=5 else 10)*p
def bars(w, h, labels, series, lab_fmt, ylab, grid=4, line=None, label_all=True):
    ml, mr, mt, mb = 44, 44 if line else 10, 26, 26
    pw, ph = w-ml-mr, h-mt-mb
    allv = [v for s in series for v in s[1]] + (list(line[1]) if line else [])
    step = nice(max(allv)*1.1/grid); ymax = math.ceil(max(allv)*1.1/step)*step
    ymin = min(0, min(allv))
    y = lambda v: mt + ph - (v-ymin)/(ymax-ymin)*ph
    n=len(labels); gw=pw/n; k=len(series); bw=gw*0.7/k
    o=[f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:auto;display:block" font-family="Montserrat, sans-serif" font-size="11.5">']
    for i in range(int(round(ymax/step))+1):
        v=i*step
        o.append(f'<line x1="{ml}" x2="{w-mr}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="var(--line2)" stroke-width="1"/>')
        o.append(f'<text x="{ml-6}" y="{y(v)+3.5:.1f}" text-anchor="end" fill="var(--muted)">{ylab(v)}</text>')
    if ymin<0: o.append(f'<line x1="{ml}" x2="{w-mr}" y1="{y(0):.1f}" y2="{y(0):.1f}" stroke="var(--gray)" stroke-width="1"/>')
    for i,lb in enumerate(labels):
        o.append(f'<text x="{ml+gw*(i+.5):.1f}" y="{h-8}" text-anchor="middle" fill="var(--gray)" font-family="Noto Sans JP, sans-serif">{lb}</text>')
    for si,s in enumerate(series):
        name,vals,fill=s[:3]; mode=s[3] if len(s)>3 else 'all'
        peaks={vals.index(max(vals)),vals.index(min(vals))}
        for i,v in enumerate(vals):
            x=ml+gw*i+gw*0.15+si*bw; y0,y1=y(max(v,0)),y(min(v,0))
            o.append(f'<rect x="{x:.1f}" y="{y0:.1f}" width="{bw-3:.1f}" height="{max(y1-y0,0):.1f}" fill="{fill}" rx="1"/>')
            if label_all and (mode=='all' or i in peaks):
                ty = y0-4 if v>=0 else y1+11
                col = 'var(--red)' if v<0 else 'var(--moss)'
                o.append(f'<text x="{x+(bw-3)/2:.1f}" y="{ty:.1f}" text-anchor="middle" fill="{col}" font-weight="700" font-size="12">{lab_fmt(v)}</text>')
    if line:
        name, vals, lf, col = line
        pts=" ".join(f"{ml+gw*(i+.5):.1f},{y(v):.1f}" for i,v in enumerate(vals))
        o.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.5" stroke-linejoin="round"/>')
        o.append(f'<text x="{ml+gw*(n-.5)+8:.1f}" y="{y(vals[-1])+3.5:.1f}" fill="{col}" font-weight="700" font-size="12">{lf(vals[-1])}</text>')
    o.append('</svg>'); return "\n".join(o)

def stacked(w, h, labels, base, top, fb, ft, ylab):
    ml, mr, mt, mb = 44, 10, 26, 26; pw, ph = w-ml-mr, h-mt-mb
    tot=max(a+b for a,b in zip(base,top)); step=nice(tot*1.12/4); ymax=math.ceil(tot*1.12/step)*step
    y=lambda v: mt+ph-v/ymax*ph; n=len(labels); gw=pw/n; bw=gw*0.56
    o=[f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:auto;display:block" font-family="Montserrat, sans-serif" font-size="11.5">']
    for i in range(int(round(ymax/step))+1):
        v=i*step
        o.append(f'<line x1="{ml}" x2="{w-mr}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="var(--line2)" stroke-width="1"/>')
        o.append(f'<text x="{ml-6}" y="{y(v)+3.5:.1f}" text-anchor="end" fill="var(--muted)">{ylab(v)}</text>')
    for i,lb in enumerate(labels):
        o.append(f'<text x="{ml+gw*(i+.5):.1f}" y="{h-8}" text-anchor="middle" fill="var(--gray)" font-family="Noto Sans JP, sans-serif">{lb}</text>')
    for i,(a,b) in enumerate(zip(base,top)):
        x=ml+gw*i+(gw-bw)/2; cx=x+bw/2
        o.append(f'<rect x="{x:.1f}" y="{y(a):.1f}" width="{bw:.1f}" height="{y(0)-y(a):.1f}" fill="{fb}" rx="1"/>')
        if b>0: o.append(f'<rect x="{x:.1f}" y="{y(a+b):.1f}" width="{bw:.1f}" height="{y(a)-y(a+b)-1.5:.1f}" fill="{ft}" rx="1"/>')
        o.append(f'<text x="{cx:.1f}" y="{y(a)-4:.1f}" text-anchor="middle" fill="var(--moss)" font-weight="700" font-size="12">{a:,}</text>')
        if b>0: o.append(f'<text x="{cx:.1f}" y="{y(a+b)-4:.1f}" text-anchor="middle" fill="var(--gray)" font-size="11.5">+{b:,}</text>')
    o.append('</svg>'); return "\n".join(o)

def legend(items):
    return '<div class="legend">'+"".join(f'<span><i style="background:{c}"></i>{n}</span>' for n,c in items)+'</div>'
def hbars(rows):
    mx=max(abs(v) for _,v,_,_ in rows); o=[]
    for lb,v,col,sub in rows:
        o.append(f'<div class="hb"><div class="hb-l">{lb}<span>{sub}</span></div><div class="hb-t"><div class="hb-f" style="width:{abs(v)/mx*100:.1f}%;background:{col}"></div><b style="color:{"var(--red)" if v<0 else "var(--moss)"}">{sg(v)}</b></div></div>')
    return "\n".join(o)

c_af = bars(920, 300, L, [('売上',AF_S,'var(--pink-lt)'),('限界利益',AF_M,PINK)], lambda v: M(v), lambda v: M(v,0))
c_ha = bars(920, 300, L, [('売上',HA_S,'var(--yellow-lt)'),('粗利',HA_G,YEL)], lambda v: M(v), lambda v: M(v,0))
c_cp = bars(600, 380, L, [('限界利益（AF＋ハナイチ）',MP,MINT),('貢献利益',CPm,'var(--line)','peaks')], lambda v: tri(v), lambda v: M(v,0), line=('人件費＋家賃',[l+RENT for l in LAB],lambda v: M(v),MOSS))
c_cap = stacked(600, 380, L, AF_O, slack, PINK, 'var(--light)', lambda v: f"{round(v):,}")

INCLUDE_SUMMARY = False    # サマリー（結論の先出し）を入れるか
INCLUDE_ANALYSIS = False   # 第2章「現状の分析」（AF・ハナイチ月次、貢献利益）を入れるか
INCLUDE_DECISION = False   # 「効率化」「2G の判断」のページを入れるか
pages=[]
def page(body, cls='', accent=None, id=None, skip=False):
    if skip: return
    pages.append((cls, body, accent, id))
_sec=[0]
def sec():
    _sec[0]+=1; return f"{_sec[0]:02d}"

# 1 表紙
page('''
  <div class="cover">
    <div class="eyebrow">株式会社ギフティ様　ご参考資料</div>
    <h1>川崎拠点の現状と収益性</h1>
    <div class="sub">2I 区画の現状と、汎用3PL／高付加価値3PL／自社EC（AP&AF）の坪効率</div>
    <div class="meta">2026 年 10 月<br>株式会社 DOMUZ<br>髙木 弘貴</div>
  </div>
''','cover')

# 2 構成
toc=[('現状の整理','2階フロアで借りている床（2I）、その使い方とキャパシティ')]
if INCLUDE_ANALYSIS: toc.append(('現状の分析','AND FLOWER・ハナイチの FY2026 実績と、2I の貢献利益'))
toc+=[('収益性の試算','汎用3PL／高付加価値3PL／自社EC（AP&AF）を 1 坪あたりで比べる'),('今後の使い方','運用方針と、スケールした後の拠点の考え方')]
page('<h1>本資料の構成</h1><div class="toc">'+"".join(f'<div class="toc-i"><div class="n">{i}</div><div><div class="t">a</div><div class="s">{s}</div></div></div>'.replace('>a<',f'>{n}<') for i,(n,s) in enumerate(toc,1))+'</div><p class="note">※ 用語と集計の前提は最終ページにまとめています</p>')

# 3 サマリー
page(f'''
  <h1>サマリー</h1>
  <div class="sum">
    <div class="sum-i"><div class="n">1</div><div><div class="t">2I は家賃と人件費を引いても貢献利益が出ている</div>
      <ul><li>FY2026（25 年 10 月〜 26 年 9 月）の貢献利益は月 {cp/1e4:,.0f} 万円（年 {cp*12/1e6:,.1f} 百万円）。家賃 0.94 百万円の {cp/RENT:.1f} 倍</li>
      <li>ただし母の日の 2 か月に偏り、閑散月（6〜7 月、1〜2 月）は 100 万円を割る。繁閑差は限界利益で {max(MP)/min(MP):.1f} 倍</li></ul></div></div>
    <div class="sum-i"><div class="n">2</div><div><div class="t">同じ 1 坪でも、用途で貢献利益は大きく変わる</div>
      <ul><li>汎用3PL +{fmt(SC[0]['cp'])} 円／坪／月、高付加価値3PL +{fmt(SC[1]['cp'])} 円、自社EC（AP&AF）+{fmt(SC[2]['cp'])} 円</li>
      <li>汎用3PL は家賃をようやく賄う水準。<b class="hl">汎用3PL に床は使わない</b></li></ul></div></div>
    <div class="sum-i"><div class="n">3</div><div><div class="t">今後は「閑散月を埋める」と「2G で床を増やす」の 2 段</div>
      <ul><li>閑散月の空き能力（月 {fmt(slackAvg)} 件）を高付加価値3PL で埋め、ハナイチを直近水準にすると、2I のままで月 {eff/1e4:,.0f} 万円</li>
      <li>2G（243.82 坪）は高付加価値3PL と AF の繁忙期増産で埋めれば、追加家賃 {man(GRENT)} を引いて <b class="hl">月 +{net/1e4:,.0f} 万円</b>。高付加価値3PL だけなら損益分岐 {fmt(be1)} 件／月</li></ul></div></div>
  </div>
  <p class="note">※ 数値は税抜、月次。限界利益＝売上−花材・資材・送料、粗利＝売上−仕入、貢献利益＝限界利益（粗利）−拠点人件費−家賃。3PL の単価と件数は仮置き</p>
''', skip=not INCLUDE_SUMMARY)

# 4 章扉
page(f'<div class="num">{{SEC}}</div><div class="lab">CURRENT STATE</div><div class="t">現状の整理</div><div class="s">2階フロアで借りている床（2I）と、その使い方</div>','divider')

# 5 区画図
page(f'''
  <h1>現状の整理</h1>
  <p class="sub">2I を当社が借りており、2D の一部をギフティ社が利用中。2G は交渉中</p>
  <p class="cap">坪数は図面の専有面積　坪単価は 2I の契約値 7,296 円／坪／月（2G は同単価で仮置き）　※税抜</p>
  <div class="plan plan-wide" style="background-image:url({PLAN})">
    <div class="ov dash" style="left:3.6%;top:36%;width:30.8%;height:14.6%"><span class="tag alt">2G　243.82坪 ・ 交渉中</span></div>
    <div class="ov solid" style="left:3.4%;top:60%;width:8.5%;height:38.5%"><span class="tag">2I　128.84坪 ・ 当社利用中</span></div>
    <div class="ov fill" style="left:57.2%;top:83.5%;width:8.4%;height:12.7%"><span class="tag gray">2D の一部 ・ ギフティ社 利用中</span></div>
  </div>
  <div class="cols" style="margin-top:10px">
    <div style="flex:1">
      <table class="tb compact">
        <thead><tr><th>区画</th><th class="r">坪</th><th class="r">坪単価（円／坪／月）</th><th class="r">月額（円）</th><th class="r">年額（円）</th></tr></thead>
        <tbody>
          <tr><td>2I（当社・現在）</td><td class="r">128.84</td><td class="r">7,296</td><td class="r">{fmt(RENT)}</td><td class="r">{fmt(RENT*12)}</td></tr>
          <tr><td class="in">　うち冷蔵庫（キーパー）59.52㎡　6.4m × 9.3m</td><td class="r">18.00</td><td class="r">7,296</td><td class="r">{fmt(UNIT*COLD)}</td><td class="r">{fmt(UNIT*COLD*12)}</td></tr>
          <tr><td>2G（交渉中）</td><td class="r">243.82</td><td class="r">7,296（仮置き）</td><td class="r">{fmt(GRENT)}</td><td class="r">{fmt(GRENT*12)}</td></tr>
          <tr class="tot"><td>2I ＋ 2G</td><td class="r">372.66</td><td class="r">7,296（仮置き）</td><td class="r">{fmt(RENT+GRENT)}</td><td class="r">{fmt((RENT+GRENT)*12)}</td></tr>
          <tr><td>2D の一部（ギフティ社）</td><td class="r">要確認</td><td class="r">—</td><td class="r">—</td><td class="r">—</td></tr>
        </tbody>
      </table>
      <p class="unit">※税抜</p>
    </div>
  </div>
  <p class="note">※ 2I と 2G は同じフロアの左側で隣接し、2G は 2I の約 1.9 倍。2G の坪単価・契約条件は交渉中。2D（384.27 坪）のうちギフティ社が使う部分の坪数は要確認</p>
''')

# 6 2I の使い方
now=[('冷蔵庫（キーパー）',COLD,MOSS,'生花の鮮度保持（固定設備。59.52㎡、6.4m × 9.3m）'),('ハナイチ',HA_T,YEL,'生花の在庫・出荷（2I の 20% を上限）'),('AND FLOWER',AF_T,PINK,'ブーケ制作、梱包、資材、出荷待ち、イネイブラー同梱')]
seg="".join(f'<div class="seg" style="flex:{v};background:{c}"><span>{n.split("（")[0]} {v:.0f}坪</span></div>' for n,v,c,_ in now)
_acc=0; area=''
for n,v,c,_ in now:
    area+=f'<div class="ab"><div class="ab-l">{n}</div><div class="ab-t"><div class="ab-f" style="margin-left:{_acc/T2I*100:.1f}%;width:{v/T2I*100:.1f}%;background:{c}"></div></div><div class="ab-v">{v:.2f}<small>坪</small><span>{v/T2I*100:.0f}%</span></div></div>'
    _acc+=v
rows="".join(f'<tr><td><i class="sw" style="background:{c}"></i>{n}</td><td class="r">{v:.2f}</td><td class="r">{v/T2I*100:.0f}%</td><td class="r">{fmt(v*UNIT)}</td><td class="g">{d}</td></tr>' for n,v,c,d in now)
page(f'''
  <h1>現状の使い方</h1>
  <p class="sub">128.84 坪を、冷蔵庫（キーパー）・ハナイチ・AND FLOWER で使っている</p>
  <p class="cap">配分ルール：ハナイチは全体の 20% までを上限に運用中。残りは水揚げ、製作、梱包、資材管理、出荷待ち商品</p>
  <div class="cols" style="gap:40px;align-items:center">
    <div class="plan plan-2i" style="background-image:url({PLAN_2I})"></div>
    <div style="flex:1">
      <div class="hbt">面積の内訳（2I 全体 {T2I:.2f} 坪）</div>
      {area}
    </div>
  </div>
  <table class="tb compact" style="margin-top:16px">
    <thead><tr><th>用途</th><th class="r">坪</th><th class="r">比率</th><th class="r">家賃相当／月（円）</th><th>主な中身</th></tr></thead>
    <tbody>{rows}<tr class="tot"><td>合計</td><td class="r">{T2I:.2f}</td><td class="r">100%</td><td class="r">{fmt(RENT)}</td><td></td></tr></tbody>
  </table>
  <p class="note">※ 床を使う主体は AND FLOWER の発送（ブーケ制作、梱包、資材、出荷待ち）。イネイブラー案件（キャンディ、コーヒー、ギフトカード等の保管と同梱）も AND FLOWER と同じ作業スペースを利用する。冷蔵庫だけが固定設備で、ほかは繁閑で入れ替わる。母の日前後の 2 か月間は、資材等の準備で一部隣の倉庫を借りる場合もある</p>
  <p class="note" style="margin-top:4px">※ イネイブラー案件（ギフトカード、コーヒー、スイーツ等）は実施時期によって変動するが、床の使い方は AND FLOWER と同等とみなす</p>
''', id='usage')


# 現状のキャパシティ（発送日ベースの日次発送商品数、26年4月27日〜5月15日）
CAP_L = ['4/27','4/28','4/29','4/30','5/1','5/2','5/3','5/4','5/5','5/6','5/7','5/8','5/9','5/10','5/11','5/12','5/13','5/14','5/15']
CAP_V = [545,456,165,605,552,265,411,317,655,1259,2467,2778,4039,161,656,491,448,514,520]
CAP_MAX = max(CAP_V); CAP_DAY = CAP_L[CAP_V.index(CAP_MAX)]
HA_QUOTA = 800   # ハナイチ 出荷枠の上限（本／日）。管理画面の出荷枠（26年10月）の最大値
FREE_T = T2I - COLD  # 冷蔵庫を除く床
c_cap_day = bars(920, 290, CAP_L, [('発送商品数',CAP_V,PINK)], lambda v: f"{round(v):,}", lambda v: f"{round(v):,}")
page(f'''
  <h1>現状のキャパシティ（AND FLOWER に振り切った場合）</h1>
  <p class="sub">過去実績の最大は母の日前日（26 年 5 月 9 日）の {CAP_MAX:,} 点／日。この密度で床を広げた場合の発送数を出す</p>
  <p class="cap">AND FLOWER の日次発送商品数（全チャネル、発送日ベース）　26 年 4 月 27 日〜 5 月 15 日　単位：点／日</p>
  {c_cap_day}
  <div class="kpis" style="margin-top:14px">
    <div class="kpi"><div class="l">母の日前日の発送数（過去実績の最大）</div><div class="v">{CAP_MAX:,}<small>点／日</small></div><div class="d">26 年 5 月 9 日（土）。うち Shopify 3,892 点、法人 45 点、楽天 49 点、Amazon 53 点</div></div>
    <div class="kpi"><div class="l">坪あたり（{AF_T:.2f} 坪）</div><div class="v">{CAP_MAX/AF_T:,.1f}<small>点／坪／日</small></div><div class="d">AND FLOWER の床で割った値。冷蔵庫（キーパー）は共用のため除く</div></div>
    <div class="kpi"><div class="l">{FREE_T:.2f} 坪に振り切った場合</div><div class="v">{CAP_MAX/AF_T*FREE_T:,.0f}<small>点／日</small></div><div class="d">冷蔵庫を除く床をすべて AND FLOWER に使った場合（同じ密度）</div></div>
  </div>
  <p class="st">母の日前日は平常日（約 500 点）の <b class="hl pk">約 8 倍</b>。これが現状の最大発送実績</p>
  <p class="note">※ 受注管理システムの「チャネル別 発送商品数」（発送日ベース。Amazon のみ注文日）。Shopify には AND PLANTS の商品が一部含まれる。ハナイチの出荷枠は仕入と人員で日ごとに設定しており、床だけの制約ではない</p>
''', 'af', id='cap')

# 振り切った場合のシミュレーション
AF_FULL = CAP_MAX/AF_T*FREE_T; HA_FULL = HA_QUOTA/HA_T*FREE_T
sim = hbars([('AND FLOWER のみ', AF_FULL, PINK, f'{CAP_MAX/AF_T:,.1f} 点／坪／日 × {FREE_T:.2f} 坪'),('ハナイチのみ', HA_FULL, YEL, f'{HA_QUOTA/HA_T:,.1f} 本／坪／日 × {FREE_T:.2f} 坪')]).replace('+','')
page(f'''
  <h1>キャパシティのシミュレーション</h1>
  <p class="sub">冷蔵庫を除く {FREE_T:.2f} 坪を 1 つの事業に振り切ると、AND FLOWER なら {AF_FULL:,.0f} 点／日、ハナイチなら {HA_FULL:,.0f} 本／日</p>
  <p class="cap">現状の坪あたりの最大発送数に、振り切った場合の床を掛けた値　単位：点（本）／日</p>
  <table class="tb" style="margin-top:6px">
    <thead><tr><th></th><th class="r">現状の床（坪）</th><th class="r">現状の最大（／日）</th><th class="r">坪あたり（／坪／日）</th><th class="r">振り切った場合の床（坪）</th><th class="r">発送可能数（／日）</th></tr></thead>
    <tbody>
      <tr><td><i class="sw" style="background:{PINK}"></i>AND FLOWER のみ</td><td class="r">{AF_T:.2f}</td><td class="r">{CAP_MAX:,} 点</td><td class="r">{CAP_MAX/AF_T:,.1f}</td><td class="r">{FREE_T:.2f}</td><td class="r"><b>{AF_FULL:,.0f} 点</b></td></tr>
      <tr><td><i class="sw" style="background:{YEL}"></i>ハナイチのみ</td><td class="r">{HA_T:.2f}</td><td class="r">{HA_QUOTA:,} 本</td><td class="r">{HA_QUOTA/HA_T:,.1f}</td><td class="r">{FREE_T:.2f}</td><td class="r"><b>{HA_FULL:,.0f} 本</b></td></tr>
    </tbody>
  </table>
  <div style="margin-top:28px"><div class="hbt">振り切った場合の 1 日あたり発送可能数</div>{sim}</div>
  <p class="st">AND FLOWER は現状の約 1.3 倍、ハナイチは現状の約 4.3 倍まで伸ばせる。<b class="hl">床よりも先に、人員と仕入（花材）が上限になる</b></p>
  <p class="note">※ 坪あたりの密度が床の広さに比例して保てる前提。人員・作業台・冷蔵庫（共用 18 坪）は振り切った側に合わせて増やす必要がある。ハナイチは本数ベース（1 注文あたり平均 20〜30 本）</p>
''', 'ha', id='sim')

# 7 章扉
page(f'<div class="num">{{SEC}}</div><div class="lab">CURRENT PERFORMANCE</div><div class="t">現状の分析</div><div class="s">AND FLOWER・ハナイチの FY2026 実績と、2I の貢献利益</div>','divider', skip=not INCLUDE_ANALYSIS)

# 8 AF
page(f'''
  <h1>アンドフラワー：月次売上と限界利益</h1>
  <p class="sub">2I から年 {sum(AF_S)/1e6:,.0f} 百万円を出荷。限界利益は年 {sum(AF_M)/1e6:,.0f} 百万円（率 {sum(AF_M)/sum(AF_S)*100:.0f}%）</p>
  <p class="cap">26 年 9 月期（25 年 10 月〜 26 年 9 月）の月次　単位：百万円　棒の上は各月の値</p>
  {legend([('売上','var(--pink-lt)'),('限界利益',PINK)])}
  {c_af}
  <table class="tb kv" style="margin-top:14px">
    <thead><tr><th>期</th><th class="r">売上</th><th class="r">限界利益</th><th class="r">限界利益率</th><th class="r">注文数</th><th class="r">月平均売上</th><th class="r">月平均限界利益</th><th class="r">繁閑差</th></tr></thead>
    <tbody><tr class="tot"><td>26 年 9 月期</td><td class="r">{M(sum(AF_S))}</td><td class="r">{M(sum(AF_M))}</td><td class="r">{sum(AF_M)/sum(AF_S)*100:.1f}%</td><td class="r">{sum(AF_O):,} 件</td><td class="r">{M(afs)}</td><td class="r">{M(afm)}</td><td class="r">{max(AF_M)/min(AF_M):.1f} 倍</td></tr></tbody>
  </table>
  <p class="st">母の日の 4〜5 月で年間限界利益の <b class="hl pk">{(AF_M[6]+AF_M[7])/sum(AF_M)*100:.0f}%</b> を出し、最大月（5 月 {max(AF_O):,} 件）と最小月（7 月 {min(AF_O):,} 件）の差は注文数で {max(AF_O)/min(AF_O):.1f} 倍</p>
  <p class="note">※ 税抜・注文日ベース。受注管理システムの売上サマリー（AND FLOWER ブランド＝生花・ドライフラワー・スタンド花・胡蝶蘭など）。拠点を通らない直送品（スタンド花・胡蝶蘭の一部）を含む可能性があり、拠点通過分に絞る場合は下振れする。繁閑差＝限界利益の最大月 ÷ 最小月</p>
''', 'af', skip=not INCLUDE_ANALYSIS)

# 9 ハナイチ
page(f'''
  <h1>ハナイチ：月次売上と粗利</h1>
  <p class="sub">年 {sum(HA_S)/1e6:,.0f} 百万円を出荷。直近 2 か月は注文数が 2 倍の水準</p>
  <p class="cap">26 年 9 月期（25 年 10 月〜 26 年 9 月）の月次　単位：百万円　棒の上は各月の値</p>
  {legend([('売上','var(--yellow-lt)'),('粗利',YEL)])}
  {c_ha}
  <table class="tb kv" style="margin-top:14px">
    <thead><tr><th>期</th><th class="r">売上</th><th class="r">粗利</th><th class="r">粗利率</th><th class="r">注文数</th><th class="r">月平均売上</th><th class="r">月平均粗利</th><th class="r">直近 2 か月の粗利／月</th></tr></thead>
    <tbody><tr class="tot"><td>26 年 9 月期</td><td class="r">{M(sum(HA_S))}</td><td class="r">{M(sum(HA_G))}</td><td class="r">{sum(HA_G)/sum(HA_S)*100:.1f}%</td><td class="r">{sum(HA_O):,} 件</td><td class="r">{M(has_)}</td><td class="r">{M(hag)}</td><td class="r">{M(haRun)}</td></tr></tbody>
  </table>
  <p class="st">8〜9 月は月 {HA_O[-1]} 件と期前半の約 2 倍。粗利は月 {M(haRun)} 百万円で、期平均（{M(hag)} 百万円）から <b class="hl yl">+{M(e2)} 百万円</b> の水準にある</p>
  <p class="note">※ 税抜・注文日ベース。ハナイチ管理画面の売上推移。粗利＝売上−仕入（送料・資材・決済手数料は含まない）。拠点人件費は本資料では未反映</p>
''', 'ha', skip=not INCLUDE_ANALYSIS)

# 10 貢献利益
page(f'''
  <h1>2I の貢献利益</h1>
  <p class="sub">月 {cp/1e4:,.0f} 万円。坪あたりでは AND FLOWER {fmt((afm-lab)/AF_T-UNIT)} 円、ハナイチ {fmt(hag/HA_T-UNIT)} 円</p>
  <p class="cap">貢献利益＝限界利益（粗利）−拠点人件費−家賃　単位：百万円／月　人件費は AND FLOWER 発送アルバイトの月次計画値</p>
  <div class="cols">
    <div style="flex:1.45">
      {legend([('限界利益（AF＋ハナイチ）',MINT),('貢献利益','var(--line)'),('― 人件費＋家賃',MOSS)])}
      {c_cp}
    </div>
    <div style="flex:1">
      <table class="tb">
        <thead><tr><th>円／坪／月</th><th class="r">AND FLOWER</th><th class="r">ハナイチ</th><th class="r">2I 全体</th></tr></thead>
        <tbody>
          <tr><td>限界利益（粗利）</td><td class="r">{fmt(afm/AF_T)}</td><td class="r">{fmt(hag/HA_T)}</td><td class="r">{fmt((afm+hag)/T2I)}</td></tr>
          <tr><td>拠点人件費</td><td class="r rd">▲{fmt(lab/AF_T)}</td><td class="r g">未反映</td><td class="r rd">▲{fmt(lab/T2I)}</td></tr>
          <tr><td>家賃</td><td class="r rd">▲7,296</td><td class="r rd">▲7,296</td><td class="r rd">▲7,296</td></tr>
          <tr class="tot"><td>貢献利益</td><td class="r">{fmt((afm-lab)/AF_T-UNIT)}</td><td class="r">{fmt(hag/HA_T-UNIT)}</td><td class="r">{fmt(cp/T2I)}</td></tr>
          <tr><td>使っている坪数</td><td class="r">{AF_T:.2f}</td><td class="r">{HA_T:.2f}</td><td class="r">{T2I:.2f}</td></tr>
          <tr><td>月の貢献利益（百万円）</td><td class="r">{M((afm-lab)-UNIT*AF_T)}</td><td class="r">{M(hag-UNIT*HA_T)}</td><td class="r"><b>{M(cp)}</b></td></tr>
        </tbody>
      </table>
    </div>
  </div>
  <p class="st">4〜5 月は貢献利益が月 11 百万円。閑散月（6〜7 月、1〜2 月）は 1 百万円を割り、<b class="hl rd">家賃と人件費をまかなう程度</b></p>
  <p class="note">※ AND FLOWER は {AF_T:.2f} 坪、ハナイチは 25.77 坪で割った値。2I 全体は冷蔵庫を含む 128.84 坪。ハナイチは拠点人件費が未反映のため上振れ。家賃は川崎 2I の 0.94 百万円のみ。26 年 9 月期の平均</p>
''', skip=not INCLUDE_ANALYSIS)

# 11 章扉
page(f'<div class="num">{{SEC}}</div><div class="lab">SCENARIOS</div><div class="t">収益性の試算</div><div class="s">汎用3PL／高付加価値3PL／自社EC（AP&AF）を 1 坪あたりで比べる</div>','divider')

# 12 3用途
hb = hbars([(s['n'], s['cp'], c, s['d']) for s,c in zip(SC,[GRAY,MOSS,MINT])])
page(f'''
  <h1>坪効率：3 つの用途の比較</h1>
  <p class="sub">同じ 1 坪でも、汎用3PL +{fmt(SC[0]['cp'])} 円、高付加価値3PL +{fmt(SC[1]['cp'])} 円、自社EC +{fmt(SC[2]['cp'])} 円</p>
  <p class="cap">3 つの用途を「1 坪・1 か月の貢献利益」で比べる　単位：円／坪／月　※税抜</p>
  <div class="cols">
    <div style="flex:1.2">
      <table class="tb">
        <thead><tr><th></th><th class="r">汎用3PL</th><th class="r">高付加価値3PL</th><th class="r">自社EC（AP&AF）</th></tr></thead>
        <tbody>
          <tr><td>限界利益</td>{"".join(f'<td class="r">{fmt(s["rev"])}</td>' for s in SC)}</tr>
          <tr><td>拠点人件費</td>{"".join(f'<td class="r rd">▲{fmt(s["lab"])}</td>' for s in SC)}</tr>
          <tr><td>家賃</td>{"".join('<td class="r rd">▲7,296</td>' for s in SC)}</tr>
          <tr class="tot"><td>貢献利益</td>{"".join(f'<td class="r">{sg(s["cp"])}</td>' for s in SC)}</tr>
          <tr><td>限界利益は家賃の何倍か</td>{"".join(f'<td class="r">{s["rev"]/UNIT:.1f} 倍</td>' for s in SC)}</tr>
        </tbody>
      </table>
    </div>
    <div style="flex:1"><div class="hbt">貢献利益（円／坪／月）</div>{hb}</div>
  </div>
  <p class="st">汎用3PL は家賃をようやく賄う水準で、保管単価が 1 割下がれば赤字。<b class="hl">作業が付く高付加価値3PL</b> と、商品の粗利を含む自社EC が床を活かす</p>
  <p class="note">※ 汎用3PL：保管 3,300 円／パレット／月 × 2 パレット／坪、出荷作業料 250 円／件 × 20 件／坪／月、作業 60 件／人／日（アルバイト 26 万円／人月・22 日 → 197 円／件）。高付加価値3PL：ギフト同梱・花オプション付き、限界利益 800 円／件（保冷実費除く）× 60 件／坪／月、作業 24 件／人／日（→ 492 円／件）。自社EC（AP&AF）：AND FLOWER の限界利益・人件費を {AF_T:.2f} 坪で割った実績値で、商品の粗利を含むためサービス料だけの 3PL とは性質が異なる</p>
''', id='tsubo')

# 13 2Gに当てはめた
cond=['2 パレット／坪が常時埋まり、出荷 20 件／坪／月。保管単価が 1 割下がると赤字','月 14,600 件（60 件／坪 × 243.82 坪）の高付加価値案件の受注が前提','AND FLOWER の平均密度（22 件／坪／月）で床が埋まる需要が前提。繁閑差 5 倍のため年間では成立しない']
page(f'''
  <h1>2G に当てはめた場合</h1>
  <p class="sub">同じ用途を 243.82 坪に広げたときの月次貢献利益</p>
  <p class="cap">前ページの「1 坪あたり貢献利益」× 2G の坪数　実際に成立するかは、右の条件を満たす需要があるかで決まる　※税抜</p>
  <div class="kpis">
    {"".join(f'<div class="kpi"><div class="l">{s["n"]}</div><div class="v" style="color:{"var(--red)" if s["cp"]<0 else "var(--moss)"}">{"+" if s["cp"]>=0 else "▲"}{abs(s["cp"])*T2G/1e6:,.1f}<small>百万円／月</small></div><div class="d">年 {abs(s["cp"])*T2G*12/1e6:,.1f} 百万円</div></div>' for s in SC)}
  </div>
  <table class="tb" style="margin-top:28px">
    <thead><tr><th>用途</th><th class="r">月額（円）</th><th class="r">年額（円）</th><th>成立条件</th></tr></thead>
    <tbody>{"".join(f'<tr><td>{s["n"]}</td><td class="r">{sg(s["cp"]*T2G)}</td><td class="r">{sg(s["cp"]*T2G*12)}</td><td class="g">{c}</td></tr>' for s,c in zip(SC,cond))}</tbody>
  </table>
  <p class="st">2G を単一用途で埋める前提は現実的ではなく、<b class="hl">高付加価値3PL と AF の繁忙期増産の組み合わせ</b>で判断する</p>
  <p class="note">※ 2G の家賃は 7,296 円／坪で仮置き。設備・什器・原状回復は含まない</p>
''')

# 14 章扉
page(f'<div class="num">{{SEC}}</div><div class="lab">NEXT STEPS</div><div class="t">今後の使い方</div><div class="s">運用方針と、スケールした後の拠点の考え方</div>','divider')

# 15 運用方針
page(f'''
  <h1>今後の使い方：運用方針</h1>
  <p class="sub">現状の配分を基本に、当社の倉庫は「高付加価値な部分のみ」を担う</p>
  <div class="sum tight" style="margin-top:14px">
    <div class="sum-i"><div class="n">1</div><div><div class="t">現状の配分を基本にする</div>
      <ul><li>冷蔵庫（キーパー）18 坪は固定。ハナイチは全体の 20% までを上限に運用し、残りは AND FLOWER の水揚げ・製作・梱包・資材管理・出荷待ち商品に使う</li></ul></div></div>
    <div class="sum-i"><div class="n">2</div><div><div class="t">イネイブラーは高付加価値な部分のみを当社の倉庫でやる</div>
      <ul><li>現状はカードやスイーツなど在庫がそれほど多くないものが中心のため、AND FLOWER の一部として運用中</li>
      <li>汎用的な倉庫業務（保管して出すだけの仕事）は、基本的に <b class="hl">佐川急便（SGL）に委託する前提</b>。当社の倉庫でやるのは、花の扱いや製作作業が付く高付加価値な部分のみ</li>
      <li>坪単価 7,200〜7,300 円前後の倉庫を借りている理由は、<b class="hl">クオリティの高い花の制作と発送を実現するため</b>。汎用3PL は坪あたり貢献利益が家賃をようやく賄う水準で、この床を使う理由にならない（P.{{P:tsubo}}）</li></ul></div></div>
    <div class="sum-i"><div class="n">3</div><div><div class="t">空いた床は高付加価値3PL で埋め、足りなくなったら 2G を借りる</div>
      <ul><li>閑散月の空き能力（月 {fmt(slackAvg)} 件）を高付加価値3PL で埋め、それでも足りない段階で 2G を借りる</li></ul></div></div>
    <div class="sum-i"><div class="n">4</div><div><div class="t">川崎エリアよりスケールしたら、より広く坪単価の安いエリアで運用する</div>
      <ul><li>例えば埼玉県・栃木県・群馬県など、大都市圏の東京に近いエリアで <b class="hl">坪単価 5,000 円以下</b> の場所を探して運用していく想定</li></ul></div></div>
  </div>
  <p class="st"><b class="hl">保管して出すだけの仕事は外に出し、花の扱いや高付加価値な同梱・梱包作業がつく仕事だけを川崎でやる。</b>それが坪効率をいちばん高く保つ使い方</p>
''')

# 16 効率化
page(f'''
  <h1>効率化：閑散月の空き能力を埋める</h1>
  <p class="sub">2I のままでも、貢献利益は月 {eff/1e4:,.0f} 万円まで伸びる</p>
  <p class="cap">① 母の日の出荷能力（{peak:,} 件／月）に対する閑散月の空きを高付加価値3PL で埋める　② ハナイチを直近 2 か月の水準で回す</p>
  <div class="cols">
    <div style="flex:1.3">
      {legend([('AND FLOWER 注文数',PINK),('空き能力（出荷能力 4,480 件との差）','var(--light)')])}
      {c_cap}
      <p class="note" style="margin-top:6px">単位：件／月。空き能力＝26 年 5 月の実績（{peak:,} 件）− 各月の実績。年間 {sum(slack):,} 件、月平均 {fmt(slackAvg)} 件分の作業能力が空いている</p>
    </div>
    <div style="flex:1">
      <table class="tb">
        <thead><tr><th>貢献利益（円／月）</th><th class="r">月額</th><th class="r">年額</th></tr></thead>
        <tbody>
          <tr><td>現状（26 年 9 月期 平均）</td><td class="r">{fmt(cp)}</td><td class="r">{fmt(cp*12)}</td></tr>
          <tr><td>① 空き能力を高付加価値3PL で埋める<span class="g">{fmt(slackAvg)} 件 × 1 件あたり貢献 {fmt(800-labHV)} 円</span></td><td class="r">+{fmt(e1)}</td><td class="r">+{fmt(e1*12)}</td></tr>
          <tr><td>② ハナイチを直近 2 か月の粗利水準に<span class="g">{M(haRun)} − {M(hag)} 百万円（20% の床の中で成立）</span></td><td class="r">+{fmt(e2)}</td><td class="r">+{fmt(e2*12)}</td></tr>
          <tr class="tot"><td>効率化後の 2I 貢献利益</td><td class="r">{fmt(eff)}</td><td class="r">{fmt(eff*12)}</td></tr>
          <tr><td>坪あたり（128.84 坪）</td><td class="r">{fmt(eff/T2I)}</td><td class="r g">家賃の {eff/RENT:.1f} 倍</td></tr>
        </tbody>
      </table>
    </div>
  </div>
  <p class="st">閑散月を埋めるだけで貢献利益は <b class="hl">月 {cp/1e4:,.0f} → {eff/1e4:,.0f} 万円（+{(eff-cp)/cp*100:.0f}%）</b>。2G を借りる前に、まず 2I の空きを埋める</p>
  <p class="note">※ 1 件あたり貢献＝限界利益 800 円 − 人件費 492 円（24 件／人／日）。ハナイチの直近水準は 26 年 8〜9 月の平均</p>
''', skip=not INCLUDE_DECISION)

# 16 2G
nx=[('冷蔵',30,MOSS),('保管',110,'var(--line)'),('AF 制作・梱包',80,PINK),('高付加価値3PL',90,MINT),('通路・撮影・事務',62.66,'var(--light)')]
seg2="".join(f'<div class="seg" style="flex:{v};background:{c}"><span>{n} {v:.0f}坪</span></div>' for n,v,c in nx)
rows2=[('① 高付加価値3PL　6,000 件／月 × '+fmt(m1-labHV)+' 円',g1),('② AF 繁忙期の追加出荷 3,000 件（月額換算）',g2),('③ 預かり在庫の保管売上（40 パレット）',g3),('2G 管理者 1 名',-MGR),('2G 追加家賃（7,296 円 × 243.82 坪）',-GRENT)]
page(f'''
  <h1>2G の判断</h1>
  <p class="sub">高付加価値3PL と AF の繁忙期増産で埋めれば、追加家賃を引いても月 +{net/1e4:,.0f} 万円</p>
  <p class="cap">判断基準はひとつ。2G を借りて増える貢献利益が、2G の追加家賃（{M(GRENT)} 百万円／月）を上回るか　単位：円　※税抜</p>
  <div class="stack">{seg2}</div>
  <p class="note" style="margin-top:4px">2I＋2G の用途内訳（372.66 坪・配置案）。汎用3PL には床を使わない</p>
  <div class="cols" style="margin-top:20px">
    <div style="flex:1.3">
      <table class="tb">
        <thead><tr><th>2G を借りた場合の増分</th><th class="r">月額</th><th class="r">年額</th></tr></thead>
        <tbody>
          {"".join(f'<tr><td>{n}</td><td class="r{" rd" if v<0 else ""}">{sg(v)}</td><td class="r{" rd" if v<0 else ""}">{sg(v*12)}</td></tr>' for n,v in rows2)}
          <tr class="tot"><td>貢献利益の増分</td><td class="r">{sg(net)}</td><td class="r">{sg(net*12)}</td></tr>
        </tbody>
      </table>
    </div>
    <div style="flex:1">
      <div class="kpi" style="padding:0 0 0 12px">
        <div class="l">高付加価値3PL だけで回収する場合の損益分岐</div>
        <div class="v">{fmt(be1)}<small>件／月</small></div>
        <div class="d">1 件あたり貢献 {fmt(m1-labHV)} 円（限界利益 800 円 − 人件費 492 円）</div>
      </div>
      <ul class="pts" style="margin-top:20px;font-size:12px">
        <li>① 平常月 6,000 件。② 母の日 2 か月で AF を 3,000 件増産（限界利益 2,600 円、人件費 1,200 円／件）し、12 で割って月額化。③ 預かり在庫 40 パレット × 3,300 円</li>
        <li>2G の管理者 1 名（0.35 百万円／月）を固定費として控除。設備・什器・原状回復は含まない</li>
      </ul>
    </div>
  </div>
  <p class="st"><b class="hl">「埋め方」が決まれば借りてよい。</b>2I の効率化と合わせると拠点全体で月 {(eff+net)/1e4:,.0f} 万円（年 {(eff+net)*12/1e6:,.1f} 百万円）</p>
''', id='g2', skip=not INCLUDE_DECISION)

# 17 まとめ
page(f'''
  <h1>まとめと、次に確定する数字</h1>
  <div class="cols" style="margin-top:28px">
    <div style="flex:1.25">
      <div class="h2">結論</div>
      <ul class="pts">
        <li><b>現状。</b>2I の貢献利益は 26 年 9 月期で月 {cp/1e4:,.0f} 万円（年 {cp*12/1e6:,.1f} 百万円）、家賃の {cp/RENT:.1f} 倍。AND FLOWER が床の 7 割で月 {M(afm)} 百万円の限界利益、ハナイチが 2 割で月 {M(hag)} 百万円の粗利</li>
        <li><b>用途の選び方。</b>1 坪あたり貢献利益は 汎用3PL +{fmt(SC[0]['cp'])} 円 ＜ 高付加価値3PL +{fmt(SC[1]['cp'])} 円 ＜ 自社EC +{fmt(SC[2]['cp'])} 円。汎用3PL に床は使わない</li>
        <li><b>運用方針。</b>当社の倉庫でやるのは花の扱いや高付加価値な同梱・梱包作業がつく仕事のみ。汎用的な倉庫業務は佐川急便（SGL）に委託する</li>
        <li><b>スケール後。</b>川崎より広く坪単価の安いエリア（埼玉・栃木・群馬など、坪単価 5,000 円以下）で運用する想定</li>
      </ul>
    </div>
    <div style="flex:1">
      <div class="h2">次に確定する数字</div>
      <ul class="pts">
        <li>ハナイチ・AND FLOWER の実測坪数（P.{{P:usage}} の配分を置き換える。冷蔵庫は 18 坪で確定）</li>
        <li>2G の提示坪単価・契約期間・原状回復条件</li>
        <li>2D のうちギフティ社が利用する坪数と、共同で使える設備（冷蔵・作業台）の有無</li>
        <li>高付加価値3PL の受注見込み件数（平常月ベース）と 1 件あたり単価</li>
        <li>AND FLOWER の拠点通過分の売上（直送品を除いた値）と、9 月試算表の部門別人件費</li>
      </ul>
    </div>
  </div>
''')

# 18 用語
terms=[('期','9 月決算。「26 年 9 月期」＝ 2025 年 10 月〜 2026 年 9 月'),('売上','税抜・注文日ベース。AND FLOWER は受注管理システムの売上サマリー（ブランド合計）、ハナイチは管理画面の売上推移'),('限界利益','売上 − 花材・資材・送料（AND FLOWER）'),('粗利','売上 − 仕入（ハナイチ）。送料・資材・決済手数料は含まない'),('拠点人件費','AND FLOWER 発送アルバイトの月次計画値（事業計画 AP/AF 202610）。26 年 9 月は 8 月と同額で仮置き。ハナイチの拠点人件費は未反映'),('家賃','川崎 2I の 0.94 百万円／月（7,296 円／坪 × 128.84 坪）。2G は同単価で仮置き'),('貢献利益','限界利益（粗利）− 拠点人件費 − 家賃。本社人件費・光熱費・設備償却は含まない'),('空き能力','26 年 5 月の AND FLOWER 注文数（4,480 件）− 各月の注文数。作業能力の空きを件数で表したもの'),('3PL の前提','保管 3,300 円／パレット／月・2 パレット／坪、高付加価値3PL は限界利益 800 円／件・60 件／坪／月・24 件／人／日。いずれも仮置きで、受注条件が決まったら置き換える')]
page('<h1>用語と集計の前提</h1><table class="tb terms"><tbody>'+"".join(f'<tr><th>{k}</th><td>{v}</td></tr>' for k,v in terms)+'</tbody></table>')

# ---------------- HTML ----------------
N=len(pages); secs=[]
PID={pid:i for i,(_,_,_,pid) in enumerate(pages,1) if pid}
secno=0
for i,(cls,body,acc,_) in enumerate(pages,1):
    if cls=='divider': secno+=1; body=body.replace('{SEC}', f'{secno:02d}')
    body=re.sub(r'\{\{?P:(\w+)\}\}?', lambda m: str(PID[m.group(1)]), body)
    style=f' style="--accent:{acc}"' if acc else ''
    pn='' if cls in ('cover','divider') else f'<div class="pn">{i}</div>'
    secs.append(f'<section class="slide {cls}"{style}>{body}{pn}</section>')
CSS = '''
:root{--moss:#004347;--mint:#00D79C;--pink:#EF667D;--pink-lt:#F8B3BE;--yellow:#F5B700;--yellow-lt:#FBDF8A;--red:#E16464;--gray:#626262;--muted:#999999;--line:#C9CFCF;--line2:#E3E6E6;--light:#ECEEEE;--bg:#eef1f1;--accent:var(--mint)}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--moss);font-family:Montserrat,"Noto Sans JP","Hiragino Sans",sans-serif;font-feature-settings:"palt" 1;-webkit-font-smoothing:antialiased}
header{max-width:1040px;margin:0 auto;padding:24px 16px 8px}
header h1{font-size:20px;margin:0 0 4px} header p{font-size:13px;color:var(--gray);margin:0}
main{max-width:1040px;margin:0 auto;padding:8px 16px 48px;display:grid;gap:20px}
.slide{position:relative;width:1040px;height:780px;max-width:100%;background:#fff;border-radius:6px;box-shadow:0 1px 3px rgba(0,0,0,.12);overflow:hidden;padding:48px 48px 40px 52px;display:flex;flex-direction:column}
.slide::before{content:"";position:absolute;left:0;top:0;bottom:0;width:6px;background:var(--accent)}
.slide.af{--accent:var(--pink)} .slide.ha{--accent:var(--yellow)}
.slide.divider{background:var(--moss);color:#fff;justify-content:center;padding-left:72px} .slide.divider::before{display:none}
.divider .num{font-weight:300;font-size:88px;line-height:1;color:transparent;-webkit-text-stroke:1.5px #fff;letter-spacing:.02em;margin-bottom:44px}
.divider .lab{font-size:15px;letter-spacing:.38em;margin-bottom:18px;font-weight:400}
.divider .t{font-size:32px;font-weight:700;letter-spacing:.04em;margin-bottom:10px} .divider .s{font-size:15px;opacity:.85}
.pn{position:absolute;right:24px;bottom:14px;font-size:10px;color:var(--muted)}
h1{font-size:32px;font-weight:700;letter-spacing:.03em;line-height:1.35;margin:0 0 8px}
.sub{font-size:19px;font-weight:700;color:var(--moss);margin:0 0 6px;line-height:1.5}
.cap{font-size:14px;color:var(--gray);margin:0 0 14px;line-height:1.5}
.cover{margin:auto 0 0;padding:0 0 46px 48px} .cover .eyebrow{font-size:22px;margin-bottom:36px} .cover h1{font-size:52px;letter-spacing:.06em;margin-bottom:24px}
.cover .sub{font-size:21px;font-weight:400;color:var(--gray);letter-spacing:.06em;margin-bottom:120px} .cover .meta{font-size:19px;color:var(--gray);line-height:2.1}
.toc{margin-top:56px;padding:0 24px} .toc-i{display:flex;gap:28px;align-items:flex-start;padding:22px 0;border-bottom:1px solid var(--line2)} .toc-i:last-child{border-bottom:0}
.toc .n{font-size:42px;font-weight:700;color:var(--accent);line-height:1;width:44px} .toc .t{font-size:30px;font-weight:700;letter-spacing:.04em;margin-bottom:6px} .toc .s{font-size:18px;color:var(--gray)}
.sum{margin-top:10px} .sum-i{display:flex;gap:18px;align-items:flex-start;margin-bottom:18px} .sum .n{font-size:29px;font-weight:700;color:var(--accent);line-height:1.3;width:32px;flex:none}
.sum .t{font-size:21px;font-weight:700;margin-bottom:8px;line-height:1.5} .sum.tight .sum-i{margin-bottom:10px} .sum.tight .t{margin-bottom:4px} .sum.tight li{line-height:1.6} .sum ul{margin:0;padding:0;list-style:none} .sum li{font-size:16.5px;line-height:1.7;padding-left:18px;position:relative;margin-bottom:3px}
.sum li::before,.pts li::before{content:"";position:absolute;left:0;top:.62em;width:7px;height:7px;background:var(--accent)}
.hl{color:var(--mint)} .hl.pk{color:var(--pink)} .hl.yl{color:var(--yellow)} .hl.rd{color:var(--red)}
.st{font-size:19px;font-weight:700;line-height:1.65;margin:auto 0 0;padding-top:16px}
.note{font-size:11.5px;color:var(--gray);line-height:1.55;margin:8px 0 0}
.unit{font-size:12px;color:var(--gray);text-align:right;margin:6px 0 0}
.cols{display:flex;gap:32px;align-items:flex-start} .cols>div{min-width:0}
.h2{font-size:22px;font-weight:700;margin-bottom:14px}
.pts{margin:0;padding:0;list-style:none} .pts li{font-size:16.5px;line-height:1.7;padding-left:18px;position:relative;margin-bottom:8px}
table.tb{width:100%;border-collapse:collapse;font-size:14.5px} .tb th,.tb td{padding:8px 10px;text-align:left;vertical-align:middle;border-bottom:1px solid var(--line2);line-height:1.45}
.tb thead th{font-weight:700;border-bottom:2px solid var(--moss);font-size:14px} .tb .r{text-align:right;font-variant-numeric:tabular-nums}
.tb tr.tot td{background:var(--light);font-weight:700} .tb td.in{padding-left:24px;color:var(--gray)} .tb td.g,.tb span.g{color:var(--gray);font-size:12.5px;font-weight:400} .tb span.g{display:block} .tb .rd{color:var(--red)}
.tb.kv td{font-size:15px} .tb.terms th{width:160px;font-weight:700;padding:13px 10px;vertical-align:top;font-size:15px} .tb.terms td{padding:13px 10px;font-size:14px;color:var(--gray)}
.legend{display:flex;gap:18px;font-size:13.5px;color:var(--gray);margin:0 0 6px;justify-content:flex-end} .legend span{display:flex;align-items:center;gap:6px} .legend i{width:12px;height:12px;display:block;border-radius:2px}
.kpis{display:flex;gap:24px;margin-top:16px} .kpi{flex:1;min-width:0} .kpi .l{font-size:16px;font-weight:700;margin-bottom:6px} .kpi .v{font-size:52px;font-weight:700;line-height:1.1;letter-spacing:-.01em} .kpi .v small{font-size:19px;font-weight:600;margin-left:6px;letter-spacing:0} .kpi .d{font-size:13px;color:var(--gray);margin-top:6px;line-height:1.5}
.stack{display:flex;width:100%;height:52px;border-radius:4px;overflow:hidden} .stack .seg{display:flex;align-items:center;justify-content:center;min-width:0;overflow:hidden;white-space:nowrap;font-size:14px;font-weight:700;color:#fff} .stack .seg+.seg{border-left:2px solid #fff}
.stack .seg[style*="--line"],.stack .seg[style*="--light"],.stack .seg[style*="--yellow"]{color:var(--moss)}
.sw{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:8px;vertical-align:-1px}
.tb.compact th,.tb.compact td{padding:4px 10px}
.plan{position:relative;width:100%;aspect-ratio:1722/790;background-size:contain;background-repeat:no-repeat;background-position:center;background-color:#fff;border:1px solid var(--line2);border-radius:4px}
.ov{position:absolute;border-radius:3px} .ov.solid{border:2.5px solid var(--pink);background:rgba(239,102,125,.16)} .ov.dash{border:2px dashed var(--mint);background:rgba(0,215,156,.08)} .ov.fill{border:2px solid var(--gray);background:rgba(201,207,207,.55)}
.ov>.tag{position:absolute;left:-2px;top:-2px;transform:translateY(-100%);white-space:nowrap;font-size:12px;font-weight:700;padding:2px 8px;border-radius:3px;background:var(--pink);color:#fff}
.tag.alt{background:#fff;color:var(--moss);border:1px solid var(--mint)} .tag.gray{background:#fff;color:var(--gray);border:1px solid var(--gray)}
.hbt{font-size:15px;font-weight:700;margin-bottom:14px} .hb{display:flex;align-items:center;gap:14px;margin-bottom:18px} .hb-l{width:170px;font-size:15px;font-weight:700;line-height:1.35} .hb-l span{display:block;font-size:11.5px;color:var(--gray);font-weight:400;margin-top:2px}
.hb-t{flex:1;display:flex;align-items:center;gap:10px} .hb-f{height:24px;border-radius:2px;min-width:3px} .hb-t b{font-size:16px;white-space:nowrap}
.plan.plan-wide{width:75%;margin:0 auto} .plan.plan-2i{flex:none;width:248px;aspect-ratio:252/335;margin:0}
.ab{display:flex;align-items:center;gap:14px;margin-bottom:22px} .ab-l{width:150px;font-size:15px;font-weight:700} .ab-t{flex:1;height:26px;background:var(--light);border-radius:2px;overflow:hidden} .ab-f{height:100%} .ab-v{width:150px;font-size:22px;font-weight:700;white-space:nowrap} .ab-v small{font-size:13px;margin-left:3px} .ab-v span{font-size:13px;color:var(--gray);font-weight:400;margin-left:10px}
@page{size:1040px 780px;margin:0}
@media print{body{background:#fff}header{display:none}main{padding:0;gap:0;max-width:none;display:block}.slide{box-shadow:none;border-radius:0;page-break-after:always;break-after:page;max-width:none}.slide:last-child{page-break-after:auto;break-after:auto}*{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
'''
html=f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>川崎拠点の現状と収益性</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&family=Noto+Sans+JP:wght@400;700&display=swap">
<style>{CSS}</style>
</head>
<body>
<header>
<h1>株式会社ギフティ様　ご参考資料　川崎拠点の現状と収益性</h1>
<p>2026.10　株式会社Domuz　全{N}ページ</p>
</header>
<main>
{chr(10).join(secs)}
</main>
</body>
</html>
'''
open(OUT,'w',encoding='utf-8').write(html)
print('wrote',OUT,N,'pages')
