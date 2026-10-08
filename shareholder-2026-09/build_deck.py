# -*- coding: utf-8 -*-
import sys, re
HERE=__import__('os').path.dirname(__import__('os').path.abspath(__file__))
sys.path.insert(0, HERE)
from presentation_charts import compare_bars, monthly_compare, single_bars, segment_row, MOSS, LIGHT, PINK, GRAY, SUB, LINE, EN, JA, SEG_COLOR, SEG_TEXT, SEG_NAME, _open

TPL = open(HERE+'/presentation.template.html', encoding='utf-8').read()
head = TPL.split('</head>')[0]
head = head.replace('<title>{{YYYYMMDD}}_{{発表テーマ}}</title>', '<title>20261008_ギフティ様_株主報告_2026年9月</title>')
head += '''<style>
  /* このデッキだけの最小限の追加（本体 §6-2 の型の範囲内） */
  .kpi3 { display: flex; gap: 32px; margin-top: 40px; }
  .kpi3 > div { flex: 1; min-width: 0; border-left: 1px solid var(--border-light); padding-left: 24px; }
  .kpi3 > div:first-child { border-left: none; padding-left: 0; }
  .kpi3 .yoys { gap: 24px; margin-top: 12px; }
  .kpi3 .yoy { min-width: 0; }
  .kpi3 .yoy .yv { font-size: 40px; }
  .kpi3 .yoy .yl, .kpi3 .yoy .yn { font-size: 19px; }
  ul.li { list-style: none; margin-top: 8px; }
  ul.li li { position: relative; padding-left: 28px; font-size: 25px; font-weight: 400; line-height: 1.6; margin-bottom: 10px; }
  ul.li li::before { content: ""; position: absolute; left: 4px; top: 16px; width: 10px; height: 10px; border-radius: 50%; background: var(--brand-secondary); }
  ul.li li b { font-weight: 700; }
  .pillars.tight .p { padding: 16px 0; }
  .pillars.tight .p .t { font-size: 29px; }
  .pillars.tight .p .s { font-size: 21px; margin-top: 4px; }
  .pillars.tight .p .i { font-size: 40px; width: 48px; }
  .status { display: inline-block; font-size: 17px; font-weight: 700; padding: 2px 12px; border-radius: 4px; margin-left: 12px; vertical-align: middle; color: var(--text-on-fill); background: var(--brand-primary); }
  .status.go { background: var(--brand-secondary); color: var(--text-primary); }
  .status.wait { background: var(--bg-dull-green); }
  .vcenter { height: calc(100% - 64px); }
  .sum { margin-top: 20px; }
  .sum .h { font-size: 27px; font-weight: 700; color: var(--brand-secondary); border-left: 6px solid var(--brand-secondary); padding-left: 14px; line-height: 1.3; margin-bottom: 8px; }
  .sum .b { font-size: 19px; font-weight: 400; line-height: 1.7; padding-left: 20px; }
  table.fy { margin-top: 12px; }
  table.fy th, table.fy td { padding: 9px 12px; font-size: 20px; border-bottom: 1px solid var(--border-light); }
  table.fy th { background: var(--bg-moss); color: var(--text-on-fill); font-size: 17px; font-weight: 700; text-align: right; }
  table.fy th:first-child { text-align: left; }
  table.fy td { font-family: var(--font-en); text-align: right; font-weight: 700; }
  table.fy td:first-child { font-family: var(--font-ja); text-align: left; font-weight: 700; }
  table.fy tr.cur td { background: var(--bg-light); }
  .tag { display: inline-block; font-size: 15px; font-weight: 700; padding: 2px 10px; border-radius: 4px; white-space: nowrap; margin-left: auto; }
  .tag.done { background: var(--brand-secondary); color: var(--text-primary); }
  .tag.poc { background: var(--brand-primary); color: var(--text-on-fill); }
  .tag.talk { background: var(--bg-light); color: var(--text-secondary); border: 1px solid var(--border-light); }
  .legend { display: flex; gap: 24px; justify-content: flex-end; font-size: 15px; color: var(--text-secondary); font-weight: 400; align-items: center; }
  .legend .tag { margin-left: 0; margin-right: 6px; }
  .org { text-align: center; margin-top: 12px; }
  .org .root { display: inline-block; background: var(--bg-moss); color: var(--text-on-fill); font-family: var(--font-en); font-size: 20px; font-weight: 700; padding: 10px 40px; border-radius: 8px; letter-spacing: 0.08em; }
  .org .stem { width: 2px; height: 20px; background: var(--border-light); margin: 0 auto; }
  .org .bar { height: 2px; background: var(--border-light); margin: 0 112px 0 160px; }
  .cos { display: flex; gap: 24px; margin-top: 24px; }
  .cos > div { flex: 1; min-width: 0; border: 2px solid var(--border-light); border-radius: 8px; padding: 20px 20px 16px; position: relative; }
  .cos > div::before { content: ""; position: absolute; top: -26px; left: 50%; width: 2px; height: 24px; background: var(--border-light); }
  .cos .drop { width: 2px; height: 20px; background: var(--border-light); margin: 0 auto; }
  .cos .logo { height: 64px; display: flex; align-items: center; justify-content: center; margin-bottom: 12px; border-bottom: 2px solid var(--brand-primary); padding-bottom: 14px; }
  .cos .logo img { max-height: 56px; max-width: 220px; object-fit: contain; }
  .cos ul, .cainz ul { list-style: none; }
  .cos li, .cainz li { display: flex; align-items: flex-start; gap: 10px; font-size: 18px; line-height: 1.5; padding: 7px 0; border-bottom: 1px solid var(--bg-light); }
  .cos li::before, .cainz li::before { content: ""; flex: 0 0 8px; width: 8px; height: 8px; border-radius: 50%; background: var(--brand-primary); margin-top: 9px; }
  .cos li span.x, .cainz li span.x { flex: 1; }
  .cainz li { font-size: 25px; padding: 14px 0; border-bottom: 1px solid var(--border-light); }
  .cainz li .d { display: block; font-size: 16px; color: var(--text-secondary); font-weight: 400; margin-top: 2px; }
  .cainz li .tag { font-size: 17px; padding: 4px 14px; }
  .pillars.tighter .p { padding: 12px 0; }
  .pillars.tighter .p .t { font-size: 27px; }
  .pillars.tighter .p .s { font-size: 20px; }
</style>
'''

CH_COLOR={'Shopify':LIGHT,'モール':MOSS,'その他':'var(--bg-dull-green)'}
CH_TEXT={'Shopify':'var(--text-primary)','モール':'var(--text-on-fill)','その他':'var(--text-on-fill)'}
CH_NAME={'Shopify':'Shopify','モール':'モール','その他':'その他'}
def stacked_mm(data, labels, totals=None, w=520, h=440):
    """前月 vs 当月の チャネル別 積み上げ（百万円表記）。helper の stacked_segments の百万円版"""
    cats=list(data); segs=list(CH_COLOR); SEG_COLOR=CH_COLOR; SEG_TEXT=CH_TEXT; SEG_NAME=CH_NAME
    totals=totals or [sum(data[c][g] for g in segs) for c in cats]
    mx=max(totals)*1.18; pb=48; pt=40; ch=h-pb-pt; gw=w/2; bw=170
    o=[_open(w,h),f'<line x1="0" y1="{h-pb}" x2="{w}" y2="{h-pb}" stroke="{LINE}" stroke-width="2"/>']
    for i,c in enumerate(cats):
        x=i*gw+(gw-bw)/2; y=h-pb
        for g in segs:
            v=data[c][g]; hh=ch*v/mx; y-=hh
            o.append(f'<rect x="{x}" y="{y:.1f}" width="{bw}" height="{hh:.1f}" fill="{SEG_COLOR[g]}"/>')
            o.append(f'<text x="{x+bw/2}" y="{y+hh/2+8:.1f}" text-anchor="middle" font-size="22" font-weight="700" fill="{SEG_TEXT[g]}" style="{EN}">{v:.1f}</text>')
        o.append(f'<text x="{x+bw/2}" y="{h-pb-ch*totals[i]/mx-12:.1f}" text-anchor="middle" font-size="30" font-weight="700" fill="{MOSS}" style="{EN}">{totals[i]:.1f}</text><text x="{x+bw/2}" y="{h-pb+32}" text-anchor="middle" font-size="22" fill="{SUB}" style="{JA}">{labels[i]}</text>')
    lx=20
    for g in segs:
        o.append(f'<rect x="{lx}" y="6" width="20" height="20" fill="{SEG_COLOR[g]}"/><text x="{lx+28}" y="23" font-size="19" fill="{SUB}" style="{JA}">{SEG_NAME[g]}</text>'); lx+=130
    o.append('</svg>')
    return ''.join(o)

# ---------- 数字（会計の試算表 2026年10月8日時点・暫定。単位: 円 → 百万円で表記） ----------
# 限界利益 = 売上総利益 − 荷造運賃 − 支払手数料（過去の株主報告資料と同じ定義。7月 25.3／8月 19.5 に一致）
# 全体ROAS = 売上高 ÷ 広告宣伝費
MONTHS=['10月','11月','12月','1月','2月','3月','4月','5月','6月','7月','8月','9月']
SALES=[59197005,59760976,59779303,79337562,54849614,67535713,98372443,111498180,62032508,61635649,58720586,65720929]
# 9月は試算表に棚卸が未反映（期首・期末 0）のため、期首 142,364,396（8月末）・期末 135,863,553（9月末実地棚卸）で売上原価を再計算した売上総利益 34,893,585 を使う
GP   =[34518279,36312551,36781343,50680508,39623270,36529439,58913945,55111962,42422761,39554867,33890923,34893585]
SHIP =[7705772,6975908,7030374,10481854,6129251,8205163,7846281,15838706,7418200,6549013,7549602,7022898]
FEE  =[5321009,6878187,5207029,5151221,4388363,4906158,7191742,7120007,7398905,7638654,6760499,6490152]
AD   =[13583903,13798530,7115072,11301555,10650384,9871615,15374493,18830186,11515103,12398258,11878543,13494678]
MP   =[g-sh-f for g,sh,f in zip(GP,SHIP,FEE)]
MPA  =[m-a for m,a in zip(MP,AD)]
S8=[v/1e6 for v in SALES]
H8=[2.30,2.43,2.72,1.88,2.34,5.64,5.79,4.42,3.64,4.19,5.94,5.53]   # ハナイチ 第8期 月次売上（ハナイチ管理画面・税抜）
FY_SALES=834399504; FY_GP=501693312; FY_SHIP=98753022; FY_FEE=74469720; FY_AD=155721411
FY_MP=FY_GP-FY_SHIP-FY_FEE
print('9月 売上', SALES[11], '限界利益', MP[11], '広告', AD[11], '広告費込み', MPA[11], 'ROAS', round(SALES[11]/AD[11]*100,1), '率', round(MP[11]/SALES[11]*100,1))
print('8月 売上', SALES[10], '限界利益', MP[10], '広告', AD[10], '広告費込み', MPA[10], 'ROAS', round(SALES[10]/AD[10]*100,1), '率', round(MP[10]/SALES[10]*100,1))
print('FY 売上', FY_SALES, '限界利益', FY_MP, '広告費込み', FY_MP-FY_AD, 'MoM', round(SALES[11]/SALES[10]*100-100,1), round(MP[11]/MP[10]*100-100,1), round(AD[11]/AD[10]*100-100,1), round(MPA[11]/MPA[10],2))
f_int=lambda v: f'{v:g}'
f_1=lambda v: f'{v:.1f}'

# ---------- 事業別 四半期（売上・限界利益、百万円。四半期エコノミクス.xlsx。ハナイチは粗利） ----------
QL=['Q1','Q2','Q3','Q4']*4   # 第5期（FY2023）→ 第8期（FY2026）
Q_FY=['第5期','第6期','第7期','第8期']
Q_SALES={'AP':[32.30,41.49,58.02,62.38, 64.97,90.57,117.65,119.60, 110.04,145.46,171.03,128.23, 118.20,141.25,172.04,131.73],
         'AF':[4.11,6.15,16.88,8.17, 10.77,20.14,41.48,27.06, 33.09,36.46,56.31,35.68, 41.09,37.06,66.48,27.80],
         'HI':[0,0,0,0, 0,0.63,4.07,7.34, 2.92,5.73,10.77,10.96, 7.44,9.86,13.85,15.67]}
Q_MP   ={'AP':[15.30,19.47,27.98,28.40, 29.08,40.95,54.00,54.48, 51.45,66.18,79.41,58.88, 54.88,65.35,81.45,60.20],
         'AF':[2.07,3.05,7.25,3.91, 5.28,8.95,20.80,11.68, 14.78,16.24,28.43,16.05, 18.19,16.52,37.26,13.30],
         'HI':[0,0,0,0, 0,0.26,1.63,2.88, 0.97,1.61,3.16,3.46, 1.95,3.42,5.09,4.62]}
Q_COLOR={'AP':LIGHT,'AF':PINK,'HI':MOSS}; Q_TEXT={'AP':'var(--text-primary)','AF':'var(--text-on-fill)','HI':'var(--text-on-fill)'}
Q_NAME={'AP':'AND PLANTS','AF':'AND FLOWER','HI':'ハナイチ'}
def fy(d,i0): return sum(sum(d[k][i0:i0+4]) for k in d)
print('FY25 売上',round(fy(Q_SALES,0),1),'FY26 売上',round(fy(Q_SALES,4),1),'FY25 限利',round(fy(Q_MP,0),1),'FY26 限利',round(fy(Q_MP,4),1))
for k in Q_SALES: print(k, 'sales', round(sum(Q_SALES[k][:4]),1), round(sum(Q_SALES[k][4:]),1), 'mp', round(sum(Q_MP[k][:4]),1), round(sum(Q_MP[k][4:]),1))

def quarterly_stack(data, w=1000, h=270, unit='百万円'):
    """16四半期×事業別の積み上げ棒（4期分）。合計ラベルは棒の上、帯の中は18px以上のときだけ値を出す"""
    segs=['AP','AF','HI']; n=len(QL)
    totals=[sum(data[k][i] for k in segs) for i in range(n)]
    mx=max(totals)*1.22; pb=64; pt=30; ch=h-pb-pt; gw=(w-16)/n; bw=gw*0.7
    o=[_open(w,h),f'<line x1="0" y1="{h-pb}" x2="{w}" y2="{h-pb}" stroke="{LINE}" stroke-width="2"/>']
    for i in range(n):
        x=16+i*gw+(gw-bw)/2; y=h-pb
        for k in segs:
            v=data[k][i]; hh=ch*v/mx; y-=hh
            if hh>0: o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{hh:.1f}" fill="{Q_COLOR[k]}"/>')
            if hh>=16: o.append(f'<text x="{x+bw/2:.1f}" y="{y+hh/2+4:.1f}" text-anchor="middle" font-size="11" font-weight="700" fill="{Q_TEXT[k]}" style="{EN}">{v:.0f}</text>')
        o.append(f'<text x="{x+bw/2:.1f}" y="{h-pb-ch*totals[i]/mx-7:.1f}" text-anchor="middle" font-size="13" font-weight="700" fill="{MOSS}" style="{EN}">{totals[i]:.0f}</text>')
        o.append(f'<text x="{x+bw/2:.1f}" y="{h-pb+22}" text-anchor="middle" font-size="14" fill="{SUB}" style="{EN}">{QL[i]}</text>')
    for f in range(4):
        if f: xx=16+4*f*gw; o.append(f'<line x1="{xx:.1f}" y1="{pt}" x2="{xx:.1f}" y2="{h-pb+36}" stroke="{LINE}" stroke-width="1" stroke-dasharray="4 4"/>')
        o.append(f'<text x="{16+(4*f+2)*gw:.1f}" y="{h-pb+50}" text-anchor="middle" font-size="15" fill="{SUB}" style="{JA}">{Q_FY[f]}</text>')
    o.append(f'<text x="{w}" y="18" text-anchor="end" font-size="14" fill="{SUB}" style="{JA}">単位: {unit}</text></svg>')
    return ''.join(o)
QLEGEND=''

import json
HERE_=HERE
MB=json.load(open(HERE+'/monthly_by_business.json',encoding='utf-8'))
FYB=json.load(open(HERE+'/fy_by_business.json',encoding='utf-8'))
_i0=MB['months'].index('2022-10')
M_MONTHS=MB['months'][_i0:]
M_SERIES={'AP':MB['AP_S'][_i0:],'AF':MB['AF_S'][_i0:]}
def fy_of(m): y=int(m[:4]); mo=int(m[5:]); return (y+1 if mo>=10 else y)-2018   # 2018-10 創業 → 第1期
def monthly_single(vals, color, w=760, h=330, unit='百万円'):
    """48ヶ月の単系列棒。期ごとに区切り線・期合計、各期の最高月にだけ数値ラベル"""
    n=len(M_MONTHS); mx=max(vals)*1.18; pb=60; pt=34; ch=h-pb-pt; gw=w/n; bw=gw*0.72
    o=[_open(w,h),f'<line x1="0" y1="{h-pb}" x2="{w}" y2="{h-pb}" stroke="{LINE}" stroke-width="2"/>']
    for i,v in enumerate(vals):
        x=i*gw+(gw-bw)/2; hh=ch*v/mx
        if hh>0: o.append(f'<rect x="{x:.1f}" y="{h-pb-hh:.1f}" width="{bw:.1f}" height="{hh:.1f}" fill="{color}" rx="2"/>')
    fys=[fy_of(m) for m in M_MONTHS]
    for f in sorted(set(fys)):
        idx=[i for i,v in enumerate(fys) if v==f]; a,b=idx[0],idx[-1]
        if a>0: o.append(f'<line x1="{a*gw:.1f}" y1="{pt-8}" x2="{a*gw:.1f}" y2="{h-pb+30}" stroke="{LINE}" stroke-width="1" stroke-dasharray="4 4"/>')
        cx=(a+b+1)/2*gw; tot=sum(vals[a:b+1])
        o.append(f'<text x="{cx:.1f}" y="{h-pb+22}" text-anchor="middle" font-size="15" font-weight="700" fill="{MOSS}" style="{JA}">第{f}期</text>')
        o.append(f'<text x="{cx:.1f}" y="{h-pb+42}" text-anchor="middle" font-size="14" fill="{SUB}" style="{EN}">{tot:.0f}</text>')
        pk=max(idx,key=lambda i: vals[i]); o.append(f'<text x="{pk*gw+gw/2:.1f}" y="{h-pb-ch*vals[pk]/mx-6:.1f}" text-anchor="middle" font-size="13" font-weight="700" fill="{MOSS}" style="{EN}">{vals[pk]:.0f}</text>')
    o.append(f'<text x="0" y="18" font-size="14" fill="{SUB}" style="{JA}">単位: {unit}　棒の上は各期の最高月、期名の下は期合計</text></svg>')
    return ''.join(o)
def fy_table(prefix):
    rows=[]
    for f in ['5','6','7','8']:
        d=FYB[f]; S=d[prefix+'_S']; M=d[prefix+'_M']; AD=d[prefix+'_AD']; MA=d[prefix+'_MA']
        cls=' class="cur"' if f=='8' else ''
        rows.append(f'<tr{cls}><td>第{f}期</td><td>{S:,.1f}</td><td>{M:,.1f}</td><td>{M/S*100:.1f}%</td><td>{AD:,.1f}</td><td>{S/AD*100:.0f}%</td><td>{MA:,.1f}</td><td>{MA/S*100:.1f}%</td></tr>')
    return '<table class="fy"><tr><th>期</th><th>売上</th><th>限界利益</th><th>限界利益率</th><th>広告費</th><th>全体ROAS</th><th>広告費込み限界利益</th><th>同率</th></tr>'+''.join(rows)+'</table>'
pages=[]
def P(html): pages.append(html)

# P-1 表紙
P('''<section class="page cover">
  <div class="eyebrow">SHAREHOLDER REPORT 2026.10.08</div>
  <h1>2026年9月<br>株主報告資料</h1>
  <div class="rule"></div>
  <div class="meta">株式会社ギフティ様　株主定例月次MTG<br>株式会社Domuz　代表取締役　髙木 弘貴</div>
</section>''')

# P-3 章扉 01
P('''<section class="page sec">
  <div class="num">01</div>
  <div class="en-t">September 2026 Review</div>
  <div class="ja-t">2026年9月の振り返り<br><span style="font-size: 28px; font-weight: 400; opacity: 0.85;">前月比と第8期の推移で見る</span></div>
</section>''')

# KPI 3つ
P('''<section class="page">
  <h1>9月の事業進捗</h1>
  <div class="cap">試算表ベース　※税抜・暫定数字</div>
  <div class="kpi3">
    <div>
      <div class="lbl">売上高</div>
      <div class="big" style="font-size: 76px;">65.7<small>百万円</small></div>
      <div class="yoys"><div class="yoy"><div class="yl">前月比</div><div class="yv pos">+11.9%</div><div class="yn">8月 58.7 → 65.7</div></div></div>
    </div>
    <div>
      <div class="lbl">限界利益</div>
      <div class="big" style="font-size: 76px;">21.4<small>百万円</small></div>
      <div class="yoys"><div class="yoy"><div class="yl">前月比</div><div class="yv pos">+9%</div><div class="yn">8月 19.6 → 21.4</div></div></div>
    </div>
    <div>
      <div class="lbl">全体ROAS</div>
      <div class="big" style="font-size: 76px;">487<small>%</small></div>
      <div class="yoys"><div class="yoy"><div class="yl">前月</div><div class="yv">494%</div><div class="yn">広告宣伝費 11.9 → 13.5</div></div></div>
    </div>
  </div>
  <div class="sum" style="margin-top: 36px;">
    <div class="h">生花イネイブラー事業が進行中</div>
    <div class="b">来年母の日に向けて、今年お取り扱い（卸モデル）でイネイブラーを導入いただいたお客様から、追加での発注が始まっています。昨年発注量 +50% の発注希望もあり、来年に向けていいスタートを切れそうです。また諸々先方事情で遅れていた生花のイネイブラー自体も、10月に2件スタート予定（PAPABUBBLE、フレッシュロースター）。ギフティ社との具体打ち合わせも進んでおり、ブランド様へ共同での提案にいけるよう進めております。</div>
  </div>
  <div class="sum">
    <div class="h">AP/AFのtoB向けアプローチが本格開始！</div>
    <div class="b">コンシェルジュサービスと銘打って、ToB向けへのアプローチを本格化していますが、オフィス向けグリーンレンタルのニーズが多く、徐々に獲得できています。月次での継続売上と貢献利益で40%程度出るので、ToB向けとしてここは推進していきます。</div>
  </div>
</section>''')

# AND PLANTS 月次売上＋期別表
P(f'''<section class="page">
  <h1>AND PLANTS：月次売上と期別の収益性</h1>
  <div class="cap">第5期（2022年10月）〜 第8期（2026年9月）</div>
  <div style="margin-top: 4px; width: 760px; margin-left: auto; margin-right: auto;">{monthly_single(M_SERIES['AP'], LIGHT)}</div>
  {fy_table('AP')}
  <div class="note">※ 税抜・単位: 百万円。自社EC＋モール（楽天・Amazon・Yahoo!）。広告費＝Web広告の直課＋共通配賦＋モール広告（モール広告は2025年6月以降のみ計上）。マーケティングマスター集計のため試算表とは集計基準が異なる</div>
</section>''')

# AND FLOWER 月次売上＋期別表
P(f'''<section class="page">
  <h1>AND FLOWER：月次売上と期別の収益性</h1>
  <div class="cap">第5期（2022年10月）〜 第8期（2026年9月）</div>
  <div style="margin-top: 4px; width: 760px; margin-left: auto; margin-right: auto;">{monthly_single(M_SERIES['AF'], PINK)}</div>
  {fy_table('AF')}
  <div class="note">※ 税抜・単位: 百万円。自社EC（モールの花は微小のため含む）。広告費＝Web広告の直課＋共通配賦（母の日・指名検索などの共通広告は自社EC売上比で配賦）。マーケティングマスター集計のため試算表とは集計基準が異なる</div>
</section>''')

# P-8 広告効率
P(f'''<section class="page">
  <h1>広告宣伝費と広告効率</h1>
  <div class="cap">前月との比較　※全体ROAS＝売上高÷広告宣伝費</div>
  <div class="two" style="margin-top: 20px; align-items: flex-start;">
    <div style="flex: 0 0 440px;">
      <div class="lbl">9月の広告宣伝費</div>
      <div class="big" style="font-size: 76px;">13.5<small>百万円</small></div>
      <div class="yoy" style="margin-top: 12px;"><div class="yl">前月比</div><div class="yv">+13.6%</div><div class="yn">11.9 → 13.5百万円</div></div>
      <div class="yoys" style="margin-top: 12px; gap: 24px;">
        <div class="yoy" style="min-width: 0;"><div class="yl">全体ROAS</div><div class="yv" style="font-size: 44px;">487%</div><div class="yn">前月 494%</div></div>
        <div class="yoy" style="min-width: 0;"><div class="yl">広告費込み限界利益</div><div class="yv" style="font-size: 44px;">+2%</div><div class="yn">7.7 → 7.9百万円</div></div>
      </div>
    </div>
    <div style="flex: 1;">{compare_bars(['売上高','広告宣伝費','広告費込み限界利益'],prev=[58.7,11.9,7.7],cur=[65.7,13.5,7.9],labels=('2026年8月','2026年9月'),w=560,h=380)}</div>
  </div>
  <div class="line" style="margin-top: 8px;">広告を1割強増やしてもROASはほぼ維持。広告費込み限界利益は 7.9百万円で前月並み</div>
  <div class="note">※ 媒体別の広告費（媒体レポート値）: Google 4.6／Meta 2.4／楽天RPP 1.2／Amazon 1.2／Yahoo! 0.3／その他 0.2百万円。試算表の広告宣伝費とは計上基準が異なる。広告費込み限界利益は9月末棚卸を反映した暫定値</div>
</section>''')

# P-3 章扉 02
P('''<section class="page sec">
  <div class="num">02</div>
  <div class="en-t">AND PLANTS / AND FLOWER</div>
  <div class="ja-t">アンドプランツ／アンドフラワー事業</div>
</section>''')

# マルシェ
P('''<section class="page">
  <h1>9/19 中目黒マルシェを開催（3年ぶりのリアルイベント）</h1>
  <div class="cap">中目黒GT広場・観葉植物の生産者と小売店が出店・ワークショップ併催</div>
  <div class="pillars tight mt">
    <div class="p"><div class="i">1</div><div><div class="t">生産者との関係づくりが最大の目的</div><div class="s">出店者のリスクをゼロに近づけた設計。指宿の生産者も来場。中長期の仕入れ力向上につなげる</div></div></div>
    <div class="p"><div class="i">2</div><div><div class="t">雨天でも来場は多く、出店者の満足度も高い</div><div class="s">投資家・取引先にもご来場いただき、事業を知っていただく場に。ワークショップは14名が参加</div></div></div>
  </div>
  <div class="note">※ 売上・来場者数の確定値は集計完了後にご共有します</div>
</section>''')

# アプリ P-9
P(f'''<section class="page">
  <h1>アプリ経由の注文が3ヶ月で伸びている</h1>
  <div class="cap">7月 → 8月 → 9月の月次推移（注文数）</div>
  <div class="two" style="margin-top: 24px; gap: 32px;">
    <div><div class="sub">観葉植物アプリの注文</div><div class="big pos" style="font-size: 72px;">48<small>件</small></div>{single_bars(['7月','8月','9月'],[9,31,48],w=290,h=220,fmt=f_int,unit='件',label_size=22)}</div>
    <div><div class="sub">生花アプリの注文</div><div class="big pos" style="font-size: 72px;">91<small>件</small></div>{single_bars(['7月','8月','9月'],[53,72,91],w=290,h=220,fmt=f_int,unit='件',label_size=22)}</div>
    <div><div class="sub" style="font-size: 27px;">観葉アプリ 累計ユーザー</div><div class="big" style="font-size: 72px;">2,464<small>人</small></div><div class="body" style="font-size: 25px; margin-top: 12px;">9月の新規 421人<br>MAU 1,241人<br>翌月継続率 49.5%</div></div>
  </div>
  <div class="line" style="margin-top: 16px;">観葉アプリは7月のEC連携開始から3ヶ月で月48件に</div>
  <div class="note">※ 観葉アプリの注文はアプリチャネル注文、生花アプリは Appify＋花アプリチャネル注文（受注管理画面集計）。ユーザー数は社内スタッフ除く</div>
</section>''')

# グリーンレンタル
P('''<section class="page">
  <h1>グリーンレンタル：オフィス向けの受注が動き始めた</h1>
  <div class="cap">9月の重点テーマ「契約数増」。案件数が増えるほど利益率の高い事業に</div>
  <div class="pillars tight" style="margin-top: 16px;">
    <div class="p"><div class="i">1</div><div><div class="t">8月末〜9月に新規2件を受注。コアラマットレス様（オフィス）が10月初めに決定</div><div class="s">9月に現地調査・提案を実施し受注。12/1 納品予定。外資系はオフィス環境への要望が多く、既存業者からの切り替えが起きやすい</div></div></div>
    <div class="p"><div class="i">2</div><div><div class="t">ギフティ様オフィスの現地調査を実施。ほか2案件が確度高く進行中</div><div class="s">オフィスグリーンが中心。ショールーム装飾は単価を上げやすく、本部側との接点づくりが課題</div></div></div>
    <div class="p"><div class="i">3</div><div><div class="t">導入事例をLPに掲載、設置事例の撮影も開始</div><div class="s">koujitsu様、アンカージャパン様（福利厚生）を掲載。KANADEMONO YOYOGI PARK様は10/14のメンテナンス訪問時に撮影予定</div></div></div>
    <div class="p"><div class="i">4</div><div><div class="t">請求をフラワー・グリーンコンシェルジュ経由に統一</div><div class="s">レンタル契約先は全社コンシェルジュに登録し、祝い花・植物の追加購入とまとめて請求。法人向けフェイクグリーンも検討中</div></div></div>
  </div>
</section>''')

# AP/AF その他の動き
P('''<section class="page">
  <h1>9月のその他の動き（AP/AF）</h1>
  <div class="pillars tight mt">
    <div class="p"><div class="i">1</div><div><div class="t">敬老の日：生花 Autumn シリーズを発売</div><div class="s">狙いどおりの結果には届かず。初動を見てレシピ変更・撮り直しを検討中</div></div></div>
    <div class="p"><div class="i">2</div><div><div class="t">秋セールを 9/25 から開始</div><div class="s">最終日 10/4 に伸び、税込 500万円を突破。10月は楽天お買い物マラソンへ</div></div></div>
    <div class="p"><div class="i">3</div><div><div class="t">中国・昆明の花き展示会を視察（9/18〜21）</div><div class="s">品質は高く単価は安い（バラ小売1本40円）。昆明からの直輸入ルートを本格検討。大谷商会様とも意見交換</div></div></div>
  </div>
</section>''')

# P-3 章扉 03 ハナイチ
P('''<section class="page sec">
  <div class="num">03</div>
  <div class="en-t">Hanaichi</div>
  <div class="ja-t">ハナイチ事業<br><span style="font-size: 28px; font-weight: 400; opacity: 0.85;">生花・植木鉢の業務用EC</span></div>
</section>''')

# ハナイチ 数字
P(f'''<section class="page">
  <h1>ハナイチ：月商550万円台を2ヶ月連続で維持</h1>
  <div class="cap">第8期の月次売上　※税抜・注文日基準</div>
  <div class="two" style="margin-top: 16px; align-items: flex-start;">
    <div style="flex: 0 0 400px;">
      <div class="lbl">9月の売上</div>
      <div class="big" style="font-size: 76px;">5.5<small>百万円</small></div>
      <div class="yoy" style="margin-top: 12px;"><div class="yl">前年同月比</div><div class="yv pos">+60%</div><div class="yn">3.45 → 5.53百万円</div></div>
      <div class="yoys" style="margin-top: 12px; gap: 24px;">
        <div class="yoy" style="min-width: 0;"><div class="yl">注文数</div><div class="yv pos" style="font-size: 44px;">431<span style="font-family: var(--font-ja); font-size: 24px;">件</span></div><div class="yn">前年 162件</div></div>
        <div class="yoy" style="min-width: 0;"><div class="yl">粗利率</div><div class="yv" style="font-size: 44px;">27.4%</div><div class="yn">8月 28.7%</div></div>
      </div>
    </div>
    <div style="flex: 1;">{single_bars(['10月','11月','12月','1月','2月','3月','4月','5月','6月','7月','8月','9月'],H8,w=600,h=380,highlight=10,fmt=f_1,label_size=16)}</div>
  </div>
  <div class="line" style="margin-top: 8px;">注文数は前年の2.7倍。客単価が下がり（1.28万円）、粗利率は8月から1.3pt低下</div>
  <div class="note">※ ハナイチ管理画面の集計（試算表の売上高に含まれる）。生花（切り花）のみの9月売上は 2.88百万円で、目標 4.72百万円に対し 61%</div>
</section>''')

# ハナイチ 施策
P('''<section class="page">
  <h1>ハナイチ：新規獲得が課題。価格と見せ方を直す</h1>
  <div class="cap">9月の生花マーケ振り返りと10月の打ち手</div>
  <div class="pillars tight mt">
    <div class="p"><div class="i">1</div><div><div class="t">リピートは目標達成、新規が未達</div><div class="s">リピート率 42.1%（目標比144%）。新規注文は目標比59%で、新規の立ち上げが最大の課題</div></div></div>
    <div class="p"><div class="i">2</div><div><div class="t">競合（ハナプライム）分析をもとに価格・写真・送料設定を調整</div><div class="s">指宿出張でバイヤーと同行し解像度を上げた。切り花市場は伸びている</div></div></div>
    <div class="p"><div class="i">3</div><div><div class="t">植木鉢（ECOPOTS）は量販店へ</div><div class="s">カインズ様へ卸提案、10/29 にサンプル持参で訪問。POTS社とアンバサダー施策を協議</div></div></div>
    <div class="p"><div class="i">4</div><div><div class="t">楽天での生花販売を本格始動へ準備</div><div class="s">商品・カテゴリ名の統一、秋限定6SKUの追加</div></div></div>
  </div>
</section>''')

# P-3 章扉 04 イネイブラー
P('''<section class="page sec">
  <div class="num">04</div>
  <div class="en-t">Enabler & 3PL</div>
  <div class="ja-t">イネイブラー事業<br><span style="font-size: 28px; font-weight: 400; opacity: 0.85;">生花イネイブラー・高付加価値3PL</span></div>
</section>''')

# イネイブラー HAKUBA CRAFT
P('''<section class="page">
  <h1>ご紹介いただいた HAKUBA CRAFT様との連携が進行中</h1>
  <div class="cap">10月にリリース予定</div>
  <div class="body" style="margin-top: 8px; font-size: 27px;">プリザーブドフラワーを納品し先方から発送する形だけでなく、<br><b>クラフトビールをDomuzで冷蔵保管し、生花とセットで発送する</b>生花イネイブラーも進捗中。</div>
  <div style="margin-top: 20px; text-align: center;"><img src="assets/hakuba_craft.jpg" alt="HAKUBA CRAFT ギフトセット" style="width: 760px; height: 500px; object-fit: contain; border-radius: 6px;"></div>
</section>''')

# イネイブラー 保健所の登録
P('''<section class="page">
  <h1>商品を寄託して発送する際の保健所登録について</h1>
  <div class="cap">クラフトビールに関しては、今回の座組での保健所申請は不要</div>
  <div class="sub" style="margin-top: 24px;">食品衛生法上、営業許可／届出が不要なケース</div>
  <div class="pillars tight" style="margin-top: 8px;">
    <div class="p"><div class="i">1</div><div><div class="t">先方の商品を預かり、保管・発送だけを行う場合</div><div class="s">常温で保管できる商品を、開封・加工せずに保管・発送するだけなら、原則として保健所への営業届出は不要。<br>冷蔵・冷凍での保管や、小分け・加工を行う場合は、取り扱い開始前に保健所へ確認します</div></div></div>
    <div class="p"><div class="i">2</div><div><div class="t">自社在庫として販売・発送する場合</div><div class="s">包装済みで、常温で長期間保存しても衛生上の危害が生じるおそれがない食品を、そのまま扱う場合は、原則として営業許可・営業届出は不要。<br>例：未開封のコーヒー豆、ドリップバッグ、茶葉、ティーバッグなど</div></div></div>
  </div>
</section>''')

# P-3 章扉 05 ベイシアグループ連携
P('''<section class="page sec">
  <div class="num">05</div>
  <div class="en-t">Beisia Group</div>
  <div class="ja-t">ベイシアグループ連携<br><span style="font-size: 28px; font-weight: 400; opacity: 0.85;">カインズ・ハンズ・ベイシア</span></div>
</section>''')

# ベイシアグループ連携 全体図
P('''<section class="page">
  <h1>ベイシアグループ連携</h1>
  <div class="legend"><span class="tag done">実施済み</span>すでに稼働している取り組み<span class="tag poc">PoC実施予定</span>実証実験の実施を予定<span class="tag talk">協議中</span>連携に向けて協議・検討中</div>
  <div class="org"><div class="root">Domuz</div><div class="stem"></div><div class="bar"></div></div>
  <div class="cos">
    <div>
      <div class="logo"><img src="assets/logo_cainz.png" alt="CAINZ"></div>
      <ul>
        <li><span class="x">植木鉢（Ecopots）の卸</span><span class="tag poc">PoC実施予定</span></li>
        <li><span class="x">観葉植物産地の調達連携／物流共同化</span><span class="tag poc">PoC実施予定</span></li>
        <li><span class="x">観葉植物ECイネイブラー</span><span class="tag talk">協議中</span></li>
        <li><span class="x">植物パーソナル診断機能／ケアアプリの提供</span><span class="tag talk">協議中</span></li>
      </ul>
    </div>
    <div>
      <div class="logo"><img src="assets/logo_hands.png" alt="HANDS"></div>
      <ul>
        <li><span class="x">生花／ギフトイネイブラー機能の提供</span><span class="tag talk">協議中</span></li>
      </ul>
    </div>
    <div>
      <div class="logo"><img src="assets/logo_beisia.png" alt="Beisia"></div>
      <ul>
        <li><span class="x">スーパーでの花販売関連共同施策</span><span class="tag talk">協議中</span></li>
        <li><span class="x">オンライン（アプリ含む）での生花／植物イネイブラー提供</span><span class="tag done">実施済み</span></li>
      </ul>
    </div>
  </div>
  <div class="small" style="margin-top: 12px; font-size: 20px; line-height: 1.55;">カインズ・ハンズ・ベイシアをはじめとしたベイシアグループ様との連携が進行中です。既にベイシア様とは母の日でベイシアアプリ販売 → スーパーへ配架施策は実施済み。<br>グループ内で特にカインズ様は非常に温度感が高く、生産者からの共同仕入れ、ECのイネイブラー（EC共同物流網）の構築等も視野にご連携を実行予定です。ハンズ様は、観葉イネイブラーよりも、生花イネイブラーが非常に刺さっており、ギフトニーズを取りにいく施策を実施予定。</div>
</section>''')

# カインズ様
P('''<section class="page">
  <h1>カインズ様とのご連携が進んでいます</h1>
  <div class="cap">植木鉢卸に関しては10月中に具体的な調整を実施予定</div>
  <div class="two" style="margin-top: 16px; align-items: flex-start; gap: 48px;">
    <div style="flex: 0 0 300px; padding-top: 24px;"><img src="assets/logo_cainz.png" alt="CAINZ" style="width: 260px; object-fit: contain;"></div>
    <div class="cainz" style="flex: 1;">
      <ul>
        <li><span class="x">植木鉢（Ecopots）の卸<span class="d">10/29 に具体の調整予定</span></span><span class="tag poc">PoC実施予定</span></li>
        <li><span class="x">観葉植物ECイネイブラー</span><span class="tag poc">PoC実施予定</span></li>
        <li><span class="x">観葉植物産地の調達連携／物流共同化</span><span class="tag poc">PoC実施予定</span></li>
        <li><span class="x">植物パーソナル診断機能／ケアアプリの提供</span><span class="tag talk">協議中</span></li>
      </ul>
    </div>
  </div>
  <div class="small" style="margin-top: 32px; font-size: 23px; line-height: 1.7;">来年実施予定の花博開催後の観葉植物／ガーデニング需要を、オンラインでも獲得するべくオンラインストアの強化をしたいが、自社で運営＆伸ばすのは、なかなか時間もかかり難しいため、<b>イネイブラー施策をDomuzで受託するべく調整をしています。</b></div>
</section>''')

# P-3 章扉 06 ギフティ様との協業
P('''<section class="page sec">
  <div class="num">06</div>
  <div class="en-t">With giftee</div>
  <div class="ja-t">ギフティ様との協業</div>
</section>''')

# giftee e-Gift
P(f'''<section class="page">
  <h1>giftee.com の花セットギフトは9月に2.7倍</h1>
  <div class="cap">e-Gift 販売実績（缶スイーツ／お茶×季節の花のセット）</div>
  <div class="two" style="margin-top: 20px; align-items: flex-start;">
    <div style="flex: 0 0 420px;">
      <div class="lbl">9月の販売件数</div>
      <div class="big" style="font-size: 76px;">46<small>件</small></div>
      <div class="yoy" style="margin-top: 12px;"><div class="yl">前月比</div><div class="yv pos">2.7倍</div><div class="yn">8月 17件 → 9月 46件</div></div>
      <div class="yoy" style="margin-top: 12px;"><div class="yl">販売額</div><div class="yv" style="font-size: 44px;">27.6<span style="font-family: var(--font-ja); font-size: 24px;">万円</span></div><div class="yn">8月 14.0万円</div></div>
    </div>
    <div style="flex: 1;">{single_bars(['7月','8月','9月'],[14.0,14.0,27.6],w=560,h=380,highlight=2,fmt=f_1,unit='万円')}</div>
  </div>
  <div class="line" style="margin-top: 8px;">giftee for Business にも「パキラS」のギフトチケットを掲載。配送ステータス更新・長期不在時の運用も整備</div>
  <div class="note">※ 販売額は販売料ベース。7月 27件／8月 17件／9月 46件</div>
</section>''')

# 協業テーマ
P('''<section class="page">
  <h1>協業テーマの進捗</h1>
  <div class="cap">10/7 のお打ち合わせを踏まえた、現時点の論点と次のアクション</div>
  <div class="pillars tight" style="margin-top: 16px;">
    <div class="p"><div class="i">1</div><div><div class="t">カード型カタログギフト＋お花の同梱（Giftee.com／スタジオギフト）</div><div class="s">10/7 に素案を協議し、箱・商品化の具体検討へ。Domuz側で箱プロトタイプ（60サイズ・ポストサイズ）とサンプル写真を用意。次回 10/19 17:30</div></div></div>
    <div class="p"><div class="i">2</div><div><div class="t">BVLGARI様 ミモザ案件（Gift Creation）</div><div class="s">2,000個規模。花材ロスのリスク分担と予約発注の設計を協議中（Domuzは初年度コミットの姿勢）。ラッピング紙サンプルを 10/8 発送</div></div></div>
    <div class="p"><div class="i">3</div><div><div class="t">母の日PoCの振り返り → 3,000〜5,000円帯へ</div><div class="s">10/5 にいただいた振り返り資料をもとに、価格帯とフルフィルメントの設計を次回に向けて整理</div></div></div>
    <div class="p"><div class="i">4</div><div><div class="t">LINEギフト・高付加価値3PL</div><div class="s">LINEギフト向け協業資料を作成（10/1）。ご紹介企業の受け皿として花オプション付き3PLを整備。3PL担当者の採用面談をギフティ様経由で実施、11月に入社予定</div></div></div>
  </div>
</section>''')

# その他
P('''<section class="page">
  <h1>その他</h1>
  <div class="pillars mt">
    <div class="p"><div class="i">1</div><div><div class="t">みなし臨時株主総会の同意書（定款変更）をお送りしたので、ご確認をお願いしたいです</div></div></div>
    <div class="p"><div class="i">2</div><div><div class="t">Giptさんの連絡</div></div></div>
    <div class="p"><div class="i">3</div><div><div class="t">9月決算で現状決算処理で諸々動いております</div></div></div>
    <div class="p"><div class="i">4</div><div><div class="t">2026年10月以降の会計方針に関して</div></div></div>
  </div>
</section>''')

# ページ番号
out=[]
for i,p in enumerate(pages,1):
    if 'class="page sec"' in p or 'class="page cover"' in p:
        out.append(p)
    else:
        out.append(p.replace('</section>', f'  <div class="pn">{i}</div>\n</section>'))
html = head + '</head>\n<body>\n\n' + '\n\n'.join(out) + '\n\n</body>\n</html>\n'
open(HERE+'/index.html','w',encoding='utf-8').write(html)
print('pages', len(pages))
