"""
Domuz 発表スライド用 SVGグラフ生成ヘルパー（presentation.template.html 用）
- 色は必ずCSS変数（HEX直書きしない）。発表スライドの色ルール:
    全体（単系列）= --brand-primary（Moss Green）
    前年         = --bg-gray（グレー）
    強調（最高月など）= --brand-secondary（ライトグリーン）
    AND PLANTS = --brand-secondary（ライトグリーン）
    AND FLOWER = --brand-flower（ピンク #EF667D）
    モール       = --brand-primary（Moss Green）
- 使い方（Claudeに任せる場合も同じ）:
    from presentation_charts import compare_bars, monthly_compare, single_bars, stacked_segments, mini_pair, dot_grid
    svg = compare_bars(['売上','限界利益'], prev=[27.4,10.6], cur=[35.4,14.7], labels=('2025','2026'))
    → 返ってきたSVG文字列をHTMLの該当スライドに貼る
- 数値はすべて棒の上に出す（数値ラベルのないグラフは禁止）。単位は左上に小さく
"""
MOSS='var(--brand-primary)'; LIGHT='var(--brand-secondary)'; PINK='var(--brand-flower)'; GRAY='var(--bg-gray)'
SUB='var(--text-secondary)'; LINE='var(--border-light)'; EN='font-family:var(--font-en);'; JA='font-family:var(--font-ja);'
SEG_COLOR={'AP':LIGHT,'AF':PINK,'モール':MOSS}
SEG_TEXT={'AP':'#004347','AF':'#FFFFFF','モール':'#FFFFFF'}   # 帯の中の数値ラベル色（ライトグリーン地はMoss文字）
SEG_NAME={'AP':'AND PLANTS','AF':'AND FLOWER','モール':'モール'}

def _fmt(v): return f'{v:.0f}' if abs(v)>=100 else f'{v:.1f}'
def _open(w,h): return f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">'
def _unit(u,x=20,y=22): return f'<text x="{x}" y="{y}" font-size="16" fill="{SUB}" style="{JA}">単位: {u}</text>'

def compare_bars(cats, prev, cur, labels=('第7期','第8期'), w=520, h=380, unit='百万円'):
    """前年 vs 当年の2本棒（カテゴリ2〜6個）。例: 初売り・母の日の売上/限界利益"""
    n=len(cats); mx=max(prev+cur)*1.18; pb=44; pt=36; gw=(w-20)/n; bw=gw*0.36; ch=h-pb-pt
    o=[_open(w,h),f'<line x1="20" y1="{h-pb}" x2="{w}" y2="{h-pb}" stroke="{LINE}" stroke-width="2"/>',_unit(unit)]
    for i,c in enumerate(cats):
        x0=20+i*gw+gw*0.12
        for j,(v,col) in enumerate(((prev[i],GRAY),(cur[i],MOSS))):
            bh=ch*v/mx; x=x0+j*(bw+4); y=h-pb-bh
            o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{col}" rx="3"/><text x="{x+bw/2:.1f}" y="{y-8:.1f}" text-anchor="middle" font-size="18" font-weight="700" fill="{MOSS}" style="{EN}">{_fmt(v)}</text>')
        o.append(f'<text x="{x0+bw+2:.1f}" y="{h-pb+30}" text-anchor="middle" font-size="20" fill="{SUB}" style="{JA}">{c}</text>')
    o.append(f'<rect x="{w-300}" y="4" width="22" height="22" fill="{GRAY}" rx="3"/><text x="{w-270}" y="22" font-size="20" fill="{SUB}" style="{JA}">{labels[0]}</text><rect x="{w-160}" y="4" width="22" height="22" fill="{MOSS}" rx="3"/><text x="{w-130}" y="22" font-size="20" fill="{SUB}" style="{JA}">{labels[1]}</text></svg>')
    return ''.join(o)

def monthly_compare(prev, cur, months=('10月','11月','12月','1月','2月','3月','4月','5月','6月','7月','8月','9月'), labels=('第7期','第8期'), w=1000, h=480, unit='百万円'):
    """12ヶ月の前年比較棒（合計値）。セグメント別の月次積み上げは見にくいので使わない"""
    mx=max(prev+cur)*1.15; pt=56; pb=44; ch=h-pt-pb; gw=(w-10)/12; bw=gw*0.38
    o=[_open(w,h),f'<line x1="0" y1="{h-pb}" x2="{w}" y2="{h-pb}" stroke="{LINE}" stroke-width="2"/>']
    for i in range(12):
        x0=10+i*gw+gw*0.08
        for j,(v,col) in enumerate(((prev[i],GRAY),(cur[i],MOSS))):
            hh=ch*v/mx; x=x0+j*(bw+3); y=h-pb-hh
            o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{hh:.1f}" fill="{col}" rx="3"/>')
            if j==1: o.append(f'<text x="{x+bw/2:.1f}" y="{y-7:.1f}" text-anchor="middle" font-size="16" font-weight="700" fill="{MOSS}" style="{EN}">{v:.1f}</text>')
        o.append(f'<text x="{x0+bw+1.5:.1f}" y="{h-pb+30}" text-anchor="middle" font-size="19" fill="{SUB}" style="{JA}">{months[i]}</text>')
    o.append(f'<rect x="0" y="4" width="20" height="20" fill="{GRAY}" rx="3"/><text x="28" y="21" font-size="18" fill="{SUB}" style="{JA}">{labels[0]}</text><rect x="110" y="4" width="20" height="20" fill="{MOSS}" rx="3"/><text x="138" y="21" font-size="18" fill="{SUB}" style="{JA}">{labels[1]}</text><text x="{w}" y="21" text-anchor="end" font-size="16" fill="{SUB}" style="{JA}">単位: {unit}</text></svg>')
    return ''.join(o)

def single_bars(cats, vals, w=1000, h=420, highlight=None, fmt=None, colors=None, unit='百万円', label_size=None):
    """単系列の棒（全体=Moss、highlightの1本だけライトグリーン）。例: 月次売上で最高月を強調、実績vs計画"""
    n=len(cats); mx=max(vals)*1.2; pb=44; pt=40; gw=(w-20)/n; bw=gw*0.62; ch=h-pb-pt
    o=[_open(w,h),f'<line x1="20" y1="{h-pb}" x2="{w}" y2="{h-pb}" stroke="{LINE}" stroke-width="2"/>',_unit(unit)]
    for i,(c,v) in enumerate(zip(cats,vals)):
        x=20+i*gw+(gw-bw)/2; bh=ch*v/mx; y=h-pb-bh; col=colors[i] if colors else (LIGHT if i==highlight else MOSS)
        o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{col}" rx="3"/><text x="{x+bw/2:.1f}" y="{y-8:.1f}" text-anchor="middle" font-size="{label_size or (22 if n<=6 else 18)}" font-weight="700" fill="{MOSS}" style="{EN}">{fmt(v) if fmt else _fmt(v)}</text><text x="{x+bw/2:.1f}" y="{h-pb+30}" text-anchor="middle" font-size="20" fill="{SUB}" style="{JA}">{c}</text>')
    return ''.join(o)+'</svg>'

def stacked_segments(data, totals=None, w=560, h=520, div=100, unit='億円'):
    """前年・当年の2本をAP/AF/モールで積み上げ。data={'第7期':{'AP':..,'AF':..,'モール':..},'第8期':{...}}（百万円）
    totals を渡すと合計ラベルにその値を使う（共通広告費などで内訳合計とずれる場合）"""
    cats=list(data); segs=['AP','AF','モール']
    totals=totals or [sum(data[c][g] for g in segs) for c in cats]
    mx=max(totals)*1.18; pb=48; pt=40; ch=h-pb-pt; gw=w/2; bw=170
    o=[_open(w,h),f'<line x1="0" y1="{h-pb}" x2="{w}" y2="{h-pb}" stroke="{LINE}" stroke-width="2"/>']
    for i,c in enumerate(cats):
        x=i*gw+(gw-bw)/2; y=h-pb
        for g in segs:
            v=data[c][g]; hh=ch*v/mx; y-=hh
            o.append(f'<rect x="{x}" y="{y:.1f}" width="{bw}" height="{hh:.1f}" fill="{SEG_COLOR[g]}"/>')
            if hh>=30: o.append(f'<text x="{x+bw/2}" y="{y+hh/2+8:.1f}" text-anchor="middle" font-size="22" font-weight="700" fill="{SEG_TEXT[g]}" style="{EN}">{v/div:.2f}</text>')
            else: o.append(f'<text x="{x+bw+10}" y="{y+hh/2+7:.1f}" font-size="18" font-weight="700" fill="{MOSS}" style="{EN}">{g} {v/div:.2f}</text>')
        o.append(f'<text x="{x+bw/2}" y="{h-pb-ch*totals[i]/mx-12:.1f}" text-anchor="middle" font-size="30" font-weight="700" fill="{MOSS}" style="{EN}">{totals[i]/div:.1f}億</text><text x="{x+bw/2}" y="{h-pb+32}" text-anchor="middle" font-size="22" fill="{SUB}" style="{JA}">{c}</text>')
    lx=20
    for g in segs:
        o.append(f'<rect x="{lx}" y="6" width="20" height="20" fill="{SEG_COLOR[g]}"/><text x="{lx+28}" y="23" font-size="19" fill="{SUB}" style="{JA}">{SEG_NAME[g]}</text>'); lx+=190
    o.append(f'<text x="{w}" y="{h-4}" text-anchor="end" font-size="16" fill="{SUB}" style="{JA}">単位: {unit}</text></svg>')
    return ''.join(o)

def mini_pair(prev, cur, labels=('第7期','第8期'), w=290, h=220):
    """小さな前年vs当年（3〜5項目を横に並べる「育った売上」スライド用）"""
    return single_bars(list(labels),[prev,cur],w=w,h=h,colors=[GRAY,MOSS],fmt=lambda v: f'{v:g}',label_size=22)

def dot_grid(total=400, on=1, cols=20):
    """ドット図（例: 400世帯に1世帯）。HTMLのdivで返す。CSSは雛形の .dots を使う"""
    return '<div class="dots">'+''.join('<i class="r"></i>' if i<on else '<i></i>' for i in range(total))+'</div>'

def segment_row(seg, yoy, frm, positive=True):
    """左カラムのセグメント行（色見本の四角＋名前＋YoY＋前年→当年）。CSSは雛形の .segrow"""
    return f'<div class="segrow"><i style="background:{SEG_COLOR[seg]};"></i><span class="nm">{SEG_NAME[seg]}</span><span class="yv2{" pos" if positive else ""}">{yoy}</span><span class="fr">{frm}</span></div>'
