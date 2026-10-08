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
GP   =[34518279,36312551,36781343,50680508,39623270,36529439,58913945,55111962,42422761,39554867,33890923,41394428]
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
QL=['Q1','Q2','Q3','Q4','Q1','Q2','Q3','Q4']   # 第7期（FY2025）→ 第8期（FY2026）
Q_SALES={'AP':[110.04,145.46,171.03,128.23,118.20,141.25,172.04,131.73],
         'AF':[33.09,36.46,56.31,35.68,41.09,37.06,66.48,27.80],
         'HI':[2.92,5.73,10.77,10.96,7.44,9.86,13.85,15.67]}
Q_MP   ={'AP':[51.45,66.18,79.41,58.88,54.88,65.35,81.45,60.20],
         'AF':[14.78,16.24,28.43,16.05,18.19,16.52,37.26,13.30],
         'HI':[0.97,1.61,3.16,3.46,1.95,3.42,5.09,4.62]}
Q_COLOR={'AP':LIGHT,'AF':PINK,'HI':MOSS}; Q_TEXT={'AP':'var(--text-primary)','AF':'var(--text-on-fill)','HI':'var(--text-on-fill)'}
Q_NAME={'AP':'AND PLANTS','AF':'AND FLOWER','HI':'ハナイチ'}
def fy(d,i0): return sum(sum(d[k][i0:i0+4]) for k in d)
print('FY25 売上',round(fy(Q_SALES,0),1),'FY26 売上',round(fy(Q_SALES,4),1),'FY25 限利',round(fy(Q_MP,0),1),'FY26 限利',round(fy(Q_MP,4),1))
for k in Q_SALES: print(k, 'sales', round(sum(Q_SALES[k][:4]),1), round(sum(Q_SALES[k][4:]),1), 'mp', round(sum(Q_MP[k][:4]),1), round(sum(Q_MP[k][4:]),1))

def quarterly_stack(data, w=480, h=400, unit='百万円'):
    """8四半期×事業別の積み上げ棒。合計ラベルは棒の上、帯の中は20px以上のときだけ値を出す"""
    segs=['AP','AF','HI']; n=len(QL)
    totals=[sum(data[k][i] for k in segs) for i in range(n)]
    mx=max(totals)*1.2; pb=72; pt=36; ch=h-pb-pt; gw=(w-16)/n; bw=gw*0.64
    o=[_open(w,h),f'<line x1="0" y1="{h-pb}" x2="{w}" y2="{h-pb}" stroke="{LINE}" stroke-width="2"/>']
    for i in range(n):
        x=16+i*gw+(gw-bw)/2; y=h-pb
        for k in segs:
            v=data[k][i]; hh=ch*v/mx; y-=hh
            o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{hh:.1f}" fill="{Q_COLOR[k]}"/>')
            if hh>=20: o.append(f'<text x="{x+bw/2:.1f}" y="{y+hh/2+5:.1f}" text-anchor="middle" font-size="13" font-weight="700" fill="{Q_TEXT[k]}" style="{EN}">{v:.0f}</text>')
        o.append(f'<text x="{x+bw/2:.1f}" y="{h-pb-ch*totals[i]/mx-8:.1f}" text-anchor="middle" font-size="16" font-weight="700" fill="{MOSS}" style="{EN}">{totals[i]:.0f}</text>')
        o.append(f'<text x="{x+bw/2:.1f}" y="{h-pb+24}" text-anchor="middle" font-size="16" fill="{SUB}" style="{EN}">{QL[i]}</text>')
    # 期のラベルと区切り
    mid=16+4*gw
    o.append(f'<line x1="{mid:.1f}" y1="{pt}" x2="{mid:.1f}" y2="{h-pb+40}" stroke="{LINE}" stroke-width="1" stroke-dasharray="4 4"/>')
    o.append(f'<text x="{16+2*gw:.1f}" y="{h-pb+54}" text-anchor="middle" font-size="16" fill="{SUB}" style="{JA}">第7期（2024年10月〜）</text>')
    o.append(f'<text x="{16+6*gw:.1f}" y="{h-pb+54}" text-anchor="middle" font-size="16" fill="{SUB}" style="{JA}">第8期（2025年10月〜）</text>')
    o.append(f'<text x="0" y="20" font-size="15" fill="{SUB}" style="{JA}">単位: {unit}</text></svg>')
    return ''.join(o)
QLEGEND=''.join(f'<span style="display:inline-flex;align-items:center;gap:8px;margin-right:24px;font-size:18px;color:var(--text-secondary);"><i style="display:inline-block;width:18px;height:18px;border-radius:3px;background:{Q_COLOR[k]};"></i>{Q_NAME[k]}</span>' for k in ['AP','AF','HI'])
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
  <h1>9月の主要KPI</h1>
  <div class="cap">試算表ベース　※税抜・暫定数字</div>
  <div class="kpi3">
    <div>
      <div class="lbl">売上高</div>
      <div class="big" style="font-size: 76px;">65.7<small>百万円</small></div>
      <div class="yoys"><div class="yoy"><div class="yl">前月比</div><div class="yv pos">+11.9%</div><div class="yn">8月 58.7 → 65.7</div></div></div>
    </div>
    <div>
      <div class="lbl">限界利益</div>
      <div class="big" style="font-size: 76px;">27.9<small>百万円</small></div>
      <div class="yoys"><div class="yoy"><div class="yl">前月比</div><div class="yv pos">+42%</div><div class="yn">8月 19.6 → 27.9</div></div></div>
    </div>
    <div>
      <div class="lbl">全体ROAS</div>
      <div class="big" style="font-size: 76px;">487<small>%</small></div>
      <div class="yoys"><div class="yoy"><div class="yl">前月</div><div class="yv">494%</div><div class="yn">広告宣伝費 11.9 → 13.5</div></div></div>
    </div>
  </div>
  <div class="hr" style="margin-top: 40px;"></div>
  <div class="line" style="margin-top: 0;">売上高・限界利益ともに8月から回復。限界利益率は 33% → <span class="arrow">42%</span> に改善し、広告費込み限界利益は 14.4百万円（8月 7.7）</div>
  <div class="note">※ 限界利益＝売上総利益−荷造運賃−支払手数料。全体ROAS＝売上高÷広告宣伝費。広告費込み限界利益＝限界利益−広告宣伝費。試算表（10/8 時点）のため確定値と差異が出ます</div>
</section>''')

STACK=stacked_mm({'2026年8月':{'Shopify':35.9,'モール':12.2,'その他':10.6},'2026年9月':{'Shopify':39.9,'モール':13.9,'その他':12.0}},['2026年8月','2026年9月'],totals=[58.7,65.7])
# P-4 売上の内訳（チャネル別・前月比）
P(f'''<section class="page">
  <h1>売上高の内訳（チャネル別・前月比）</h1>
  <div class="cap">試算表の売上高　※税抜・単位: 百万円</div>
  <div class="two" style="margin-top: 12px; align-items: flex-start; gap: 32px;">
    <div style="flex: 0 0 480px;">
      <div class="lbl">2026年9月 合計</div>
      <div class="big" style="font-size: 76px;">65.7<small>百万円</small></div>
      <div class="yoy" style="margin-top: 4px;"><div class="yv pos" style="font-size: 48px;">+11.9%</div><div class="yn">前月 58.7百万円 → 65.7百万円</div></div>
      <div style="margin-top: 20px;">
        <div class="segrow"><i style="background:var(--brand-secondary);"></i><span class="nm">Shopify</span><span class="yv2 pos">+11%</span><span class="fr">35.9 → 39.9</span></div>
        <div class="segrow"><i style="background:var(--brand-primary);"></i><span class="nm">モール</span><span class="yv2 pos">+14%</span><span class="fr">12.2 → 13.9</span></div>
        <div class="segrow"><i style="background:var(--bg-dull-green);"></i><span class="nm">その他</span><span class="yv2 pos">+13%</span><span class="fr">10.6 → 12.0</span></div>
      </div>
    </div>
    <div style="flex: 1;">{STACK}</div>
  </div>
  <div class="line" style="margin-top: 0;">自社EC・モール・法人／卸のすべてのチャネルが前月から1割以上伸びた</div>
  <div class="note">※ モール＝Amazon Japan＋楽天市場。その他＝LINE・キナリノ・補助科目なし（法人・卸・ハナイチ等）</div>
</section>''')

# P-5 月次推移（第8期・単系列）
P(f'''<section class="page">
  <h1>第8期の月次売上高</h1>
  <div class="cap">2025年10月〜2026年9月　試算表ベース　※税抜</div>
  <div style="margin-top: 12px;">{single_bars(MONTHS,S8,w=1000,h=440,highlight=7,fmt=f_1,label_size=18)}</div>
  <div class="line" style="margin-top: 4px;">第8期は売上高 8.34億円、限界利益 3.28億円、広告費込み限界利益 1.73億円で着地。5月が過去最高の月商 1.11億円</div>
  <div class="note">※ 年間値は決算整理（売上高 −4.0百万円等）を含む。限界利益＝売上総利益−荷造運賃−支払手数料</div>
</section>''')

# 事業別 四半期 売上・限界利益
P(f'''<section class="page">
  <h1>事業別の四半期 売上・限界利益（第7期 → 第8期）</h1>
  <div class="cap">AND PLANTS／AND FLOWER／ハナイチ　※税抜・マーケティングマスター集計</div>
  <div style="margin-top: 4px;">{QLEGEND}</div>
  <div class="two" style="margin-top: 8px; gap: 40px; align-items: flex-start;">
    <div><div class="sub" style="font-size: 26px;">売上</div>{quarterly_stack(Q_SALES)}</div>
    <div><div class="sub" style="font-size: 26px;">限界利益</div>{quarterly_stack(Q_MP)}</div>
  </div>
  <div class="line" style="margin-top: 4px; font-size: 24px;">第8期は売上 7.83億円（前期比 +4.8%）、限界利益 3.62億円（+6.3%）。母の日の Q3 が AND FLOWER の山、ハナイチは Q4 に過去最高の 15.7百万円</div>
  <div class="note">※ 第7期＝2024年10月〜2025年9月、第8期＝2025年10月〜2026年9月。Q1＝10〜12月。ハナイチは限界利益の代わりに粗利。モール売上は AND PLANTS に含む。試算表とは集計基準が異なる</div>
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
    <div class="p"><div class="i">3</div><div><div class="t">値札約750点分を集計中。10/2 の振り返りを経て継続開催へ</div><div class="s">運営負荷・レジ運用・出店者の収益など、次回に活かす課題を整理中</div></div></div>
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
    <div><div class="sub">アプリ累計ユーザー</div><div class="big" style="font-size: 72px;">2,464<small>人</small></div><div class="body" style="font-size: 25px; margin-top: 12px;">9月の新規 421人<br>MAU 1,241人<br>翌月継続率 49.5%</div></div>
  </div>
  <div class="line" style="margin-top: 16px;">観葉アプリは7月のEC連携開始から3ヶ月で月48件に。10/6に秋限定のアプリ商品6SKUを追加</div>
  <div class="note">※ 観葉アプリの注文はアプリチャネル注文、生花アプリは Appify＋花アプリチャネル注文（受注管理画面集計）。ユーザー数は社内スタッフ除く</div>
</section>''')

# 法人コンシェルジュ
P('''<section class="page">
  <h1>フラワー・グリーンコンシェルジュ（法人向け）</h1>
  <div class="cap">8月に本格開始した法人向けサービス。9月は営業の型づくりの月</div>
  <div class="two" style="margin-top: 16px; align-items: flex-start; gap: 40px;">
    <div style="flex: 0 0 400px;">
      <div class="lbl">営業代行の架電（9/16時点）</div>
      <div class="big" style="font-size: 72px;">291<small>件</small></div>
      <div class="yoys" style="margin-top: 8px; gap: 24px;">
        <div class="yoy" style="min-width: 0;"><div class="yl">担当者接触率</div><div class="yv pos" style="font-size: 44px;">25.6%</div></div>
        <div class="yoy" style="min-width: 0;"><div class="yl">アポ獲得率（目標7%）</div><div class="yv neg" style="font-size: 44px;">2.9%</div></div>
      </div>
      <div class="small" style="margin-top: 16px;">社内コール30件 → 資料送付4件・登録1件<br>ミヨシ油脂様は商談当日に登録完了</div>
    </div>
    <div style="flex: 1;">
      <ul class="li">
        <li><b>開発Ph4を9/18にリリース。</b>専用コレクションで商品ラインナップを増強、胡蝶蘭・スタンド花を拡充中</li>
        <li><b>アポ率が課題。</b>訴求スクリプトを見直し 9/28 から架電を再開</li>
        <li><b>10月から既存取引法人へのローラー。</b>名刺 3,000件＋法人リスト 12,000件を整備、過去取引7,000社から登録案内</li>
        <li>フォーム営業を仕組み化（インターン1名で80件/日）。年内10万社へのアプローチを計画</li>
        <li>note記事・ニュースリリースを準備中</li>
      </ul>
    </div>
  </div>
  <div class="note">※ 法人チャネルの注文数は 9月 286件（8月 286件）。コンシェルジュ経由の売上は10月から計上ルールを整理して報告します</div>
</section>''')

# AP/AF その他の動き
P('''<section class="page">
  <h1>9月のその他の動き（AP/AF）</h1>
  <div class="pillars tight mt">
    <div class="p"><div class="i">1</div><div><div class="t">敬老の日：生花 Autumn シリーズを発売</div><div class="s">狙いどおりの結果には届かず。初動を見てレシピ変更・撮り直しを検討中</div></div></div>
    <div class="p"><div class="i">2</div><div><div class="t">秋セールを 9/25 から開始</div><div class="s">最終日 10/4 に伸び、税込 500万円を突破。10月は楽天お買い物マラソンへ</div></div></div>
    <div class="p"><div class="i">3</div><div><div class="t">グリーンレンタル：コアラマットレス様のオフィス受注が決定</div><div class="s">ギフティ様オフィスの現地調査も実施。リビングハウス様は店舗・ECで受注が動き始めた</div></div></div>
    <div class="p"><div class="i">4</div><div><div class="t">中国・昆明の花き展示会を視察（9/18〜21）</div><div class="s">品質は高く単価は安い（バラ小売1本40円）。昆明からの直輸入ルートを本格検討。大谷商会様とも意見交換</div></div></div>
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

# P-14 10月の見通し
P('''<section class="page">
  <h1>10月の見通し</h1>
  <div class="vcenter">
    <div class="stmt">10月は、B2Bの案件が<span class="g">形になる</span>月。</div>
    <ul class="li" style="margin-top: 32px;">
      <li><b>10/13</b> PAPABUBBLE様 リリース／<b>10/15</b> フレッシュロースター珈琲問屋様 納品</li>
      <li><b>10/19</b> ギフティ様 次回お打ち合わせ（箱・商品化）／<b>10/29</b> カインズ様 訪問</li>
      <li>秋セール（10/4 時点で税込 500万円超）、楽天お買い物マラソン、楽天生花の本格始動</li>
    </ul>
    <div class="stmt mt2">引き続き、よろしくお願いいたします。</div>
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
