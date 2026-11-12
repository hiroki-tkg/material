"""ギフティ社長定例 2026年11月（10月実績）— Domuz「発表スライド」型で pptx を生成する。

    python3 build_deck.py out/giftee_2026-11.pptx
    bash <skill>/scripts/render.sh out/giftee_2026-11.pptx "ギフティ定例 2026年11月" "2026.11 株式会社DOMUZ"
"""
import os
import sys

SKILL = os.path.expanduser("~/.claude/skills/synced/c877595e-9c45-49a9-8ea7-19fa3e366349_909874ba-85e7-4fba-9ee5-df754fdb136c/domuz-deck/scripts")
sys.path.insert(0, SKILL)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deck_lib import *  # noqa: E402,F401
from deck_lib import _drop_style  # noqa: E402
from data_giftee import *  # noqa: E402,F401

out = sys.argv[1] if len(sys.argv) > 1 else "out/giftee_2026-11.pptx"
use_theme("ap")
i9, i10 = 0, 1  # 9月, 10月


def pct(a, b):
    """前月比などの率。マイナスは ▲。"""
    v = (a / b - 1) * 100
    return f"▲{-v:.1f}%" if v < -0.05 else f"+{v:.1f}%"


def mom_pt(a, b):
    v = a - b
    return f"▲{-v:.1f}pt" if v < -0.05 else f"+{v:.1f}pt"


def m(v):
    """百万円・小数1桁。マイナスは ▲。"""
    return yen(v)


def bullets(s, x, y, w, items, size=16, color=MOSS, gap=6, dot=None, spacing=1.4):
    """四角の点＋本文の箇条書き。items は文字列（[[強調]] 可）。行数は幅から見積もって y を進める。"""
    dot = dot or T.accent
    per_line = max(1, int((w - 16) / (size * 1.1)))
    for it in items:
        vis = sum(1.0 if ord(ch) > 0x7F else 0.55 for ch in it.replace("[[", "").replace("]]", "").replace("**", ""))
        n = max(1, -(-int(vis + 0.999) // per_line))
        h = int(size * spacing * n) + 2
        rect(s, x, y + int(size * 0.55), 7, 7, dot)
        text(s, x + 16, y, w - 16, h, it, size=size, color=color, spacing=spacing)
        y += h + gap
    return y



def outfit(tb):
    """テキストボックス内の英数字ランのフォントを Outfit に（前回資料の数字と同じ見た目）。"""
    for para in tb.text_frame.paragraphs:
        for r in para.runs:
            r.font.name = "Outfit"
            rpr = r._r.get_or_add_rPr()
            cs = rpr.find(qn("a:cs"))
            if cs is not None:
                cs.set("typeface", "Outfit")
    return tb

def panel(s, x, y, w, title, color=None, size=20):
    """色帯＋見出し。戻り値は本文の開始 y。"""
    color = color or T.accent
    rect(s, x, y, w, 5, color)
    text(s, x, y + 18, w, 32, title, size=size, bold=True)
    return y + 60


def grid(s, x, y, col_w, header, rows, size=13, row_h=40, bold_col0=True, pad=0):
    """左寄せの文章表。rows の各セルは文字列（\\n で改行可）。"""
    xs = [x]
    for cw in col_w[:-1]:
        xs.append(xs[-1] + cw)
    w = sum(col_w)
    for j, hd in enumerate(header):
        text(s, xs[j] + pad, y, col_w[j] - 8 - pad, 22, hd, size=12, color=SECONDARY, bold=True)
    hline(s, x, y + 26, w, MOSS, 1.5)
    y += 32
    for row in rows:
        rh = row_h if isinstance(row_h, (int, float)) else row_h[rows.index(row)]
        for j, v in enumerate(row):
            text(s, xs[j] + pad, y, col_w[j] - 10 - pad, rh - 4, v.split("\n"), size=size, bold=(j == 0 and bold_col0),
                 anchor=MSO_ANCHOR.MIDDLE, spacing=1.3)
        y += rh
        hline(s, x, y - 2, w)
    return y


# =====================================================================
# 1. 表紙・構成・要約（要約は最後に埋める）
# =====================================================================
cover("株式会社ギフティ様 定例資料", ["2026年10月の振り返りと", "各事業のトピックス"],
      "売上・限界利益・広告費込み限界利益と、AF／ハナイチ／イネイブラー／カインズ／資本の論点",
      ["2026年11月", "株式会社DOMUZ", "髙木 弘貴"])

summary = content_slide("サマリー")

# =====================================================================
# 2. 10月の数字
# =====================================================================
divider("01", "OCTOBER RESULTS", "10月の数字", "試算表ベースの売上高・限界利益・全体ROAS　2026年10月（税抜・百万円）")

s = content_slide("10月の事業進捗", "試算表ベース　※税抜・暫定数字")
i_t, i_p, i_y = -1, -2, 0  # 10月, 9月, 昨年10月
cols = [(56, "売上高", f"{TB_SALES[i_t]:.1f}", "百万円", "昨年対比", pct(TB_SALES[i_t], TB_SALES[i_y]), f"昨年10月 {TB_SALES[i_y]:.1f} → {TB_SALES[i_t]:.1f}"),
        (564, "限界利益", f"{TB_MP[i_t]:.1f}", "百万円", "昨年対比", pct(TB_MP[i_t], TB_MP[i_y]), f"昨年10月 {TB_MP[i_y]:.1f} → {TB_MP[i_t]:.1f}")]
for x, label, val, unit, sub1label, sub1, sub2 in cols:
    text(s, x, 150, 300, 30, label, size=22, color=SECONDARY)
    outfit(big_number(s, x, 176, "", val, unit, size=64, w=320))
    text(s, x, 266, 300, 22, sub1label, size=15, color=SECONDARY)
    neg = sub1.startswith("▲")
    outfit(text(s, x, 286, 300, 44, sub1, size=32, bold=True, color=(STRONG if neg else T.accent), en=True, spacing=1.0))
    outfit(text(s, x, 330, 320, 22, sub2, size=14, color=SECONDARY))
vline(s, 540, 150, 200)
hline(s, 56, 372, 1016)
topics = [
    ("ハナイチ（生花）はリピートが積み上がり、出荷能力の強化へ",
     f"生花のリピート注文は昨年10月{HY_REPEAT[0]}件 → 今年10月{HY_REPEAT[-1]}件（率{HY_REPEAT_RATE[0]:.0f}%→{HY_REPEAT_RATE[-1]:.0f}%）と積み上がり、売上は{HY_SALES[-1] / HY_SALES[0]:.1f}倍の{m(HY_SALES[-1])}百万円です。"
     "9月中旬から毎日発送上限に達しているため、11/9から体制を組み替え、OP効率化と卸・輸入による原価調整で1月までに出荷能力を引き上げます。"),
    ("生花イネイブラーがギフティ社との共同案件で本格化",
     f"箱（11/27入稿）や同梱手数料300円など主要条件は合意済みです。ギフティ社経由の日立ビルシステム（1万件・{HITACHI['sales'][0]:.1f}〜{HITACHI['sales'][2]:.1f}百万円）と"
     "TENTIAL（母の日〜父の日で1万件見込み）が進み、野菜をMOTTOも来年母の日のテストに前向きです。HAKUBA CRAFTなど生花3案件は12月にローンチします。"),
    ("AFは価格調整で件数+27%。カインズとはECOPOTS卸から協業へ",
     f"10/16の価格調整で注文数{pct(AF['orders'][i10], AF['orders'][i9])}・売上{pct(AF['sales'][i10], AF['sales'][i9])}。競合他社との価格に対して価格競争力があるような金額に調整中です。"
     "カインズとは来春30店舗でのECOPOTS卸が決まり、リアル店舗・EC受託・関東の生産拠点まで含む協業の話が出ています。"),
]
y = 386
for head, body in topics:
    text(s, 56, y, 1016, 34, head, size=22, bold=True, color=T.accent)
    vis = sum(1.0 if ord(ch) > 0x7F else 0.55 for ch in body)
    n = max(1, -(-int(vis + 0.999) // 62))  # 16px・幅1016pxで実測 約64字/行
    bh = int(16 * 1.4 * n) + 4
    text(s, 56, y + 48, 1016, bh, body, size=16, spacing=1.4)
    y += 48 + bh + 18
footnote(s, f"※ 限界利益＝売上総利益 − 荷造運賃 − 支払手数料。前月比は売上{pct(TB_SALES[i_t], TB_SALES[i_p])}・限界利益{pct(TB_MP[i_t], TB_MP[i_p])}。広告宣伝費 {TB_AD[i_t]:.1f}百万円（昨年10月 {TB_AD[i_y]:.1f}）")

# 月次推移（試算表）
s = content_slide("月次推移：売上は前年同月比+13%、利益の山は母の日", "試算表ベースの売上高と限界利益　2025年10月〜2026年10月　単位：百万円")
legend(s, 214, 154, [("売上高", T.accent)])
legend(s, 340, 154, [("限界利益（右軸）", T.dark)], line=True)
ax = bar_chart(s, 200, 180, 720, 330, TB_LABELS, [("売上高", TB_SALES)], vmax=250, ticks=(0, 40, 80, 120), value_labels=True)
ry = ax.yv2(50)
polyline(s, [(ax.x(i), ry(TB_MP[i])) for i in range(len(TB_MP))], T.dark, 2.0)
for i in (0, 7, len(TB_MP) - 1):
    text(s, ax.x(i) - 30, ry(TB_MP[i]) - 22, 60, 16, f"{TB_MP[i]:.1f}", size=10, bold=True, color=T.dark, align=PP_ALIGN.CENTER, en=True)
ann_s, ann_mp = sum(TB_SALES[1:]), sum(TB_MP[1:])
text(s, 56, 548, 1016, 100, [
    f"直近12か月の売上高は{ann_s:.0f}百万円、限界利益は{ann_mp:.0f}百万円（{ann_mp / ann_s * 100:.0f}%）。10月の限界利益率{TB_MP[i_t] / TB_SALES[i_t] * 100:.0f}%は12か月平均並み。",
    f"10月は広告宣伝費を{pct(TB_AD[i_t], TB_AD[i_p])}増やして売上は{pct(TB_SALES[i_t], TB_SALES[i_p])}にとどまり、全体ROASは{TB_ROAS[i_p]:.0f}%→{TB_ROAS[i_t]:.0f}%。"],
     size=17, bold=True, spacing=1.5)
footnote(s, "※ 試算表（月次推移）。限界利益＝売上総利益 − 荷造運賃 − 支払手数料。9月以前は10/10時点、10月は11/11時点の暫定値。決算整理は含まない")

# =====================================================================
# 3. 事業のトピックス
# =====================================================================
divider("02", "BUSINESS TOPICS", "事業のトピックス", "アンドフラワー ／ ハナイチ ／ イネイブラー")

# --- AF: 価格調整 ---
s = content_slide("AF：価格を下げて件数+27%、売上は前月比+18%", accent=FLOWER)
message(s, f"10/16の値下げが効き、広告費込み限界利益は{m(AF['net'][i10])}百万円（前月比{pct(AF['net'][i10], AF['net'][i9])}）。客単価の低下が課題")
kpi_table(s, 56, 160, 470, ["AF 自社EC", "9月", "10月", "前月比"], [
    ["売上（百万円）", m(AF["sales"][i9]), m(AF["sales"][i10]), pct(AF["sales"][i10], AF["sales"][i9])],
    ["注文数", f"{AF['orders'][i9]:,}", f"{AF['orders'][i10]:,}", pct(AF["orders"][i10], AF["orders"][i9])],
    ["客単価", f"{AF['aov'][i9]:,}円", f"{AF['aov'][i10]:,}円", pct(AF["aov"][i10], AF["aov"][i9])],
    ["限界利益", m(AF["mp"][i9]), m(AF["mp"][i10]), pct(AF["mp"][i10], AF["mp"][i9])],
    ["　限界利益率", f"{AF['mp'][i9] / AF['sales'][i9] * 100:.0f}%", f"{AF['mp'][i10] / AF['sales'][i10] * 100:.0f}%",
     mom_pt(AF["mp"][i10] / AF["sales"][i10] * 100, AF["mp"][i9] / AF["sales"][i9] * 100)],
    ["広告費", m(AF["ad"][i9]), m(AF["ad"][i10]), pct(AF["ad"][i10], AF["ad"][i9])],
    ["広告費込み限界利益", m(AF["net"][i9]), m(AF["net"][i10]), pct(AF["net"][i10], AF["net"][i9])],
    ["　同率", f"{AF['net'][i9] / AF['sales'][i9] * 100:.0f}%", f"{AF['net'][i10] / AF['sales'][i10] * 100:.0f}%",
     mom_pt(AF["net"][i10] / AF["sales"][i10] * 100, AF["net"][i9] / AF["sales"][i9] * 100)],
], col_w=[200, 90, 90, 90], bold_rows=(6,), row_h=36)
vline(s, 556, 160, 480)
y = panel(s, 584, 160, 488, "10月に行った価格・商品の調整", FLOWER)
bullets(s, 584, y, 488, [
    "10/2　そのまま飾れる花束S 3,980→3,480円、S/Mの送料 1,100→990円。売上ベースで[[+25%]]",
    "10/16　8商品群を10〜20%値下げ（おまかせ花束S/M/L、そのまま飾れる花束S/M、アレンジ3品）。件数[[+27%]]",
    "効いた：そのまま飾れるS/M・花束L。効かず：花束S/M・お供えアレンジ",
    "10/26　お供え商品の写真を取り直し。閲覧+44%・件数+18%",
    "10/29〜　商品ページの改善をテスト中",
], size=15, dot=FLOWER)
text(s, 56, 676, 1016, 70, ["値下げで件数は増えたが、客単価が下がり利益の伸びは小さい。",
                            "11月は価格・写真の適正化を横展開し、クリスマス・成人の日、CRM、レビュー増施策で利益率を戻す。"],
     size=17, bold=True, spacing=1.45)
footnote(s, "※ AF自社EC（モールは含まない）。価格は税込、売上・利益は税抜")

# --- AF: OP問題 ---
s = content_slide("AF：OP問題。貢献利益の赤字は4か月続けて縮小", accent=FLOWER)
message(s, f"10月の貢献利益は{m(AF_CONTRIB['contrib'][-1])}百万円。OPEX比率は{AF_CONTRIB['opex'][0]}%→{AF_CONTRIB['opex'][-1]}%、ロス率は{AF_CONTRIB['loss'][2]}%→{AF_CONTRIB['loss'][3]}%")
kpi_table(s, 56, 160, 470, ["AF（モール含む）", *AF_CONTRIB["months"]], [
    ["広告費込み限界利益", "—", "—", "—", m(AF_CONTRIB["net_oct"])],
    ["貢献利益", *[m(v) for v in AF_CONTRIB["contrib"]]],
    ["OPEX比率", *[f"{v}%" for v in AF_CONTRIB["opex"]]],
    ["ロス率（仕入額比）", *["—" if v is None else f"{v}%" for v in AF_CONTRIB["loss"]]],
    ["（参考）AP 貢献利益", *[m(v) for v in AP_CONTRIB["contrib"]]],
], col_w=[190, 70, 70, 70, 70], bold_rows=(1,), row_h=38)
text(s, 56, 400, 470, 150, [
    "貢献利益＝広告費込み限界利益 − 拠点のアルバイト人件費等。",
    f"10月のAFはアルバイト給与・法定福利・交通費で{2.735333 + 0.303102 + 0.181778:.1f}百万円。",
    "OPEX比率は7月38%から毎月下がり、10月は20%。"], size=15, color=SECONDARY, spacing=1.5)
vline(s, 556, 160, 480)
y = panel(s, 584, 160, 488, "何が起きているか・どう解くか", FLOWER)
bullets(s, 584, y, 488, [
    "9月中旬からハナイチが毎日発送上限に達し、AF社員がハナイチのOPに入っている。花拠点の機動力が落ち、新しい売上施策が出しづらい",
    "11月：AFとハナイチの組織を分離。ハナイチのOPには経営陣・他事業の社員・インターンが入り、AFを本業に戻す（11/9〜）",
    "採用：AF梱包 11/9入社、花事務 11/1入社。フローリストは面接中。紹介で3万円のリファラル制度を開始",
    "ロス削減：余った花材に即日割引を付け、花材の声掛けを増やしてロス率10.3%→8.3%",
], size=15, dot=FLOWER)
text(s, 56, 676, 1016, 70, ["母の日までの3か月が踏ん張りどころ。OPの効率化と組織分離で、貢献利益を黒字圏に近づける。"],
     size=17, bold=True, spacing=1.45)
footnote(s, "※ 貢献利益・OPEX比率・ロス率はリーダーMTG（11/5）の管理数値。モール・LINEギフトを含む")

# --- ハナイチ: KPI ---
s = content_slide("ハナイチ生花：リピート率は昨対比で24%→47%", accent=HANA)
L, Y = -1, 0  # 今年10月, 昨年10月
message(s, f"10月は注文{HY_ORDERS[L]}件・リピート{HY_REPEAT[L]}件（率{HY_REPEAT_RATE[L]:.0f}%、昨年{HY_REPEAT_RATE[Y]:.0f}%）。生花商品の客単価は{HY_FAOV_3K[L]:,}円（+{(HY_FAOV_3K[L] / HY_FAOV_3K[Y] - 1) * 100:.0f}%）")
text(s, 56, 154, 460, 24, "生花の注文数（新規・リピート）とリピート率　2025年10月〜", size=14, color=SECONDARY, bold=True)
legend(s, 56, 182, [("新規", HANA_LIGHT), ("リピート", HANA)])
legend(s, 262, 182, [("リピート率（右軸）", HANA_DARK)], line=True)
ax = bar_chart(s, 56, 206, 520, 300, HY_LABELS, [("新規", HY_FIRST), ("リピート", HY_REPEAT)], stacked=True,
               colors=[HANA_LIGHT, HANA], vmax=700, ticks=(0, 200, 400))
ry = ax.yv2(60)
polyline(s, [(ax.x(i), ry(HY_REPEAT_RATE[i])) for i in range(len(HY_LABELS))], HANA_DARK, 2.0)
for i in (0, 6, len(HY_LABELS) - 1):
    text(s, ax.x(i) - 30, ry(HY_REPEAT_RATE[i]) - 22, 60, 16, f"{HY_REPEAT_RATE[i]:.0f}%", size=10, bold=True, color=HANA_DARK, align=PP_ALIGN.CENTER, en=True)
for i in (0, len(HY_LABELS) - 1):
    text(s, ax.x(i) - 24, ax.yv(HY_ORDERS[i]) - 18, 48, 16, f"{HY_ORDERS[i]}", size=9, bold=True, align=PP_ALIGN.CENTER, en=True)
vline(s, 596, 154, 440)
kpi_table(s, 616, 160, 456, ["生花", "昨年10月", "今年10月", "昨年対比"], [
    ["売上（百万円）", m(HY_SALES[Y]), m(HY_SALES[L]), f"{HY_SALES[L] / HY_SALES[Y]:.1f}倍"],
    ["注文数", f"{HY_ORDERS[Y]}", f"{HY_ORDERS[L]}", f"{HY_ORDERS[L] / HY_ORDERS[Y]:.1f}倍"],
    ["購入顧客数", f"{HY_CUSTOMERS[Y]}", f"{HY_CUSTOMERS[L]}", f"{HY_CUSTOMERS[L] / HY_CUSTOMERS[Y]:.1f}倍"],
    ["リピート注文数", f"{HY_REPEAT[Y]}", f"{HY_REPEAT[L]}", f"{HY_REPEAT[L] / HY_REPEAT[Y]:.1f}倍"],
    ["リピート率", f"{HY_REPEAT_RATE[Y]:.1f}%", f"{HY_REPEAT_RATE[L]:.1f}%", mom_pt(HY_REPEAT_RATE[L], HY_REPEAT_RATE[Y])],
    ["客単価（3,000円超）", f"{HY_FAOV_3K[Y]:,}円", f"{HY_FAOV_3K[L]:,}円", pct(HY_FAOV_3K[L], HY_FAOV_3K[Y])],
    ["客単価（全注文）", f"{HY_FAOV[Y]:,}円", f"{HY_FAOV[L]:,}円", pct(HY_FAOV[L], HY_FAOV[Y])],
    ["1注文あたり本数", f"{HY_STEMS[Y]:.1f}本", f"{HY_STEMS[L]:.1f}本", pct(HY_STEMS[L], HY_STEMS[Y])],
], col_w=[176, 90, 100, 90], bold_rows=(3,), row_h=40)
text(s, 56, 650, 1016, 100, [
    f"リピート注文は昨年10月{HY_REPEAT[Y]}件 → {HY_REPEAT[L]}件（{HY_REPEAT[L] / HY_REPEAT[Y]:.1f}倍）。率は{HY_REPEAT_RATE[Y]:.0f}%→{HY_REPEAT_RATE[L]:.0f}%で、新規に頼らず積み上がる構造に変わった。",
    f"生花商品のみの客単価は{HY_FAOV[Y]:,}→{HY_FAOV[L]:,}円（{pct(HY_FAOV[L], HY_FAOV[Y])}）。3,000円以下の小口注文（{HY_FSMALL[Y] / HY_ORDERS[Y] * 100:.0f}%→{HY_FSMALL[L] / HY_ORDERS[L] * 100:.0f}%）を除くと{HY_FAOV_3K[Y]:,}→{HY_FAOV_3K[L]:,}円（{pct(HY_FAOV_3K[L], HY_FAOV_3K[Y])}）。",
    "9月中旬から毎日発送上限に達し、売れているのに送れない状態。出荷能力がボトルネック。"], size=16, bold=True, spacing=1.45)
footnote(s, "※ BigQuery（ハナイチ注文データ）で集計。生花を含む注文・注文日ベース・税抜、キャンセル・返金・スキップは除く。売上は送料込み（リーダーMTGの生花KPIと一致）、客単価は生花商品の明細のみ（送料・鉢・資材を除く）")

# --- ハナイチ: 今後のステップ ---
s = content_slide("ハナイチ：体制を変え、1月までに出荷能力を上げる", accent=HANA)
message(s, "9月中旬から毎日発送上限に達している。上限を外せば売上は伸びる")
cols = [(56, "① 体制を大きく変更（〜1月）", [
            "11/9から体制を組み替え、社長・事業責任者・ハナイチ社員・インターン・Bizが本来の役割を超えてOPに入る",
            "AFのメンバーがハナイチOPに入らなくても回る状態をつくり、AFとハナイチの組織を分離",
            "採用：ハナイチ梱包 2名入社（10/16・11/4）。派遣スタッフ・他拠点メンバーも期間限定で活用",
            "2027年3月に物流責任者（3PL拠点の立上げ・運営 約20年）が入社予定"]),
        (396, "② OP効率化で工数を減らす", [
            "水揚げ不要の運用、水付けを保水材に変更、納品書の廃止",
            "仕入れ・CSの発注システムを導入済み",
            "即日発送を11/20頃から一部の葉物で開始。12月に赤バラを追加し、AFとの在庫共通化へ",
            "11月のスローガン「一人当たりの出荷数を2倍に」、12月「1日100箱の日をつくる」"]),
        (736, "③ 原価を調整する（卸と輸入）", [
            "市場外の卸仕入れと輸入花材を活用し、花材原価を下げる",
            "卸の余剰在庫はタイムセール寄りの施策でさばく仕組みをつくる",
            f"生花の限界利益率は{HF_MP[-1] / HF_SALES[-1] * 100:.0f}%にとどまる。卸込みのエコノミクスを計算し、年内に判断",
            "AFとの組織分離後も、生花の仕入れ・配送は共同で効率化"])]
for x, title_, items in cols:
    y = panel(s, x, 160, 336, title_, HANA, size=18)
    bullets(s, x, y, 336, items, size=14, dot=HANA_DARK, gap=8)
text(s, 56, 676, 1016, 70, ["出荷上限を外して注文を売上に変える。並行して卸・輸入で粗利率を戻し、年内に卸込みの採算を判断する。"],
     size=17, bold=True, spacing=1.45)
footnote(s, "※ リーダーMTG（11/5）・経営MTG（11/9）の決定事項。10月の限界利益はSBS費（倉庫）の請求前")

# --- イネイブラー: 案件一覧 ---
s = content_slide("イネイブラー：多くの案件が卸と生花で進捗")
active = EN_PIPE["before"] + EN_PIPE["undated"] + EN_PIPE["first"] + EN_PIPE["negotiating"] + EN_PIPE["won"] + EN_PIPE["producing"]
message(s, f"進行中{active}件（商談・交渉{EN_PIPE['before'] + EN_PIPE['undated'] + EN_PIPE['first'] + EN_PIPE['negotiating']}、受注・制作中{EN_PIPE['won'] + EN_PIPE['producing']}）。ギフティ経由の1万件規模の案件が2本")
deals = [
    ["PAPABUBBLE", "生花", "キャンディ×花 16SKU（10/13〜）", "稼働中。新箱版を提案", True],
    ["HAKUBA CRAFT", "プリ卸＋生花", "プリ200個納品済。ビール×生花", "生花は12月ローンチ", True],
    ["野菜をMOTTO", "生花", "母の日テスト 2,000〜3,000個", "価格・箱を再提案", True],
    ["TENTIAL", "生花", "BAKUNE×花、母の日1万件", "11月中に企画決定", True],
    ["日立ビルシステム", "プリ卸", f"1万件、{HITACHI['sales'][0]:.1f}〜{HITACHI['sales'][2]:.1f}百万円", "見積3案、11/27発注", True],
    ["SILK THE RICH", "生花＋プリ", "ガラス一輪M 100個〜＋ブーケ", "12月中旬リリース", False],
    ["Color Your Life", "生花", "チョコ×ミニブーケM", "12月開始、サンプル着", False],
    ["Mr. CHEESECAKE", "プリ卸", "ボックス1,000個 1.75百万円", "制作中、1月下旬納品", False],
    ["エール・エル", "プリ卸", "ドーム1,500個 1.76百万円", "最終分 11/27納品", False],
    ["UCC・BAKE", "プリ卸", "2027年母の日、1,200個〜", "見積・サンプル検討中", False],
    ["遠鉄百貨店", "生花", "百貨店EC 66SKU、1/12公開", "受注確定、連携確認中", False],
]
gy, grh = 170, 40
for i, row in enumerate(deals):
    if row[4]:  # ギフティ経由は網掛け
        rect(s, 56, gy + 32 + i * grh, 1016, grh - 2, PALE)
gy2 = grid(s, 56, gy, [210, 140, 400, 266], ["案件", "種別", "内容・規模", "状況"], [r[:4] for r in deals], size=14, row_h=grh, pad=12)
IN_TABLE_ACTIVE = 10  # 表の中で営業進捗リスト上「進行中」の行数（HAKUBA生花・MOTTO・SILK・CYL・Mr.C①・エール①②・UCC・BAKE・遠鉄）
others = active - IN_TABLE_ACTIVE
text(s, 56, gy2 + 4, 1004, 26, f"その他　進行中{others}件", size=15, bold=True, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
rect(s, 68, gy2 + 10, 18, 14, PALE)
text(s, 94, gy2 + 6, 400, 22, "網掛け＝ギフティ様よりご紹介いただいた案件", size=12, color=SECONDARY)
footnote(s, f"※ 営業進捗リスト（11/11時点）。その他{others}件の内訳：商談・交渉中{EN_PIPE['first'] + EN_PIPE['negotiating'] - 5}件（GREEN SPOON・JTB・BENAMOR・グレープストーンなど）、"
            f"商談待ち{EN_PIPE['before'] + EN_PIPE['undated']}件（コーセー・ゴントランシェリエなど）、制作中2件。納品済み{EN_PIPE['delivered']}件・継続取引{EN_PIPE['ongoing']}件は含まない。金額は税抜")

# --- イネイブラー: 同梱イメージ ---
def picture(s, path, x, y, w, h):
    """画像を枠いっぱいに（縦横比を保って）配置する。"""
    from PIL import Image as _Im
    iw, ih = _Im.open(path).size
    sc = min(w / iw, h / ih)
    pw, ph = iw * sc, ih * sc
    s.shapes.add_picture(path, px(x + (w - pw) / 2), px(y + (h - ph) / 2), px(pw), px(ph))

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
s = content_slide("同梱イメージ：こんな形でお届けします")
message(s, "ギフト用の専用ボックス（60サイズ）に、先方の商品と弊社のミニブーケを一つに収めて出荷")
for x, img, name, cap in [
        (56, "papabubble_box.jpg", "PAPABUBBLE", "キャンディ2瓶＋ミニブーケ＋ギフトカード。2027年1月から現行セットに追加予定"),
        (564, "motto_box.jpg", "野菜をMOTTO", "スープ2個＋生花ミニブーケ。来年の母の日向けに11/11提案。花代980円＋送料・同梱作業750円")]:
    picture(s, os.path.join(ASSETS, img), x, 160, 508, 380)
    text(s, x, 552, 508, 30, name, size=20, bold=True)
    text(s, x, 586, 508, 60, [cap], size=14, color=SECONDARY, spacing=1.4)
text(s, 56, 666, 1016, 50, ["1つの箱でモノギフト・giftee.comのカード・冊子など複数のものに対応できる箱を開発中。開封の瞬間まで含めてギフト体験を高め、他の案件にも同じ箱で展開する。"],
     size=17, bold=True, spacing=1.45)
footnote(s, "※ 画像は塚本作成の提案資料（PAPABUBBLE様 11/12、モンマルシェ様 11/11）より。箱はデザイン・寸法が変わる可能性あり。商品写真は各社サイトを基に作成したイメージ")

# --- イネイブラー: 今後の大きな方針（自社ECでも販売） ---
def arrow(s, x1, y1, x2, y2, color=None, weight=2.0, dash=False):
    """矢印（終点に三角）。"""
    from pptx.oxml import parse_xml
    color = color or T.dark
    ln = s.shapes.add_connector(1, px(x1), px(y1), px(x2), px(y2))
    ln.line.color.rgb = color
    ln.line.width = Emu(int(weight * 12700))
    if dash:
        ln.line.dash_style = 4
    ln.line._get_or_add_ln().append(parse_xml('<a:tailEnd xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" type="triangle" w="med" len="med"/>'))
    _drop_style(ln)
    return ln

def node(s, x, y, w, h, title, lines, fill=None, line=None, title_color=None, size=13):
    rect(s, x, y, w, h, fill if fill is not None else WHITE, line=line or BORDER_LIGHT, weight=1.5)
    text(s, x + 16, y + 14, w - 32, 28, title, size=17, bold=True, color=title_color or MOSS)
    text(s, x + 16, y + 46, w - 32, h - 54, lines, size=size, color=MOSS, spacing=1.4)

s = content_slide("今後の大きな方針：イネイブラー商品を自社ECでも販売")
message(s, "取引先の商品を弊社が在庫として預かり、取引先ECと AND FLOWER の両方で同じセットを売る")
# 図：取引先 → Domuz拠点（在庫・データ） → 取引先EC／AND FLOWER EC → お客様
def chip(s, x, y, w, label, fill=None, line=None, color=None, size=13, h=30):
    rect(s, x, y, w, h, fill if fill is not None else WHITE, line=line or BORDER_LIGHT, shape=MSO_SHAPE.ROUNDED_RECTANGLE, weight=1.25)
    text(s, x, y, w, h, label, size=size, bold=True, color=color or MOSS, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)

DY, DH = 156, 256  # 図の上端と高さ（3ブロックとも同じ高さ）
# 左：取引先（細く）
node(s, 56, DY, 200, DH, "取引先", ["商品を弊社拠点へ", "まとめて納品"], size=14)
for i, p_ in enumerate(["キャンディ", "スープ", "コスメ", "スイーツ"]):
    chip(s, 72, DY + 108 + i * 34, 168, p_, size=13, h=28)
# 中央：Domuz拠点（大きく・センタリング）
CX, CW = 334, 460  # 中心 564
rect(s, CX, DY - 12, CW, DH + 24, T.light, line=T.accent, weight=2.5)
text(s, CX + 20, DY + 2, CW - 40, 30, "Domuz 川崎拠点", size=20, bold=True, color=T.dark)
text(s, CX + 20, DY + 36, CW - 40, 22, "取引先の商品と生花を在庫として保有し、セット制作・同梱・出荷", size=13, color=MOSS)
text(s, CX + 20, DY + 66, 120, 22, "取引先の商品", size=12, color=SECONDARY, bold=True)
for i, p_ in enumerate(["キャンディ", "スープ", "コスメ", "スイーツ"]):
    chip(s, CX + 20 + i * 106, DY + 90, 98, p_, size=13)
text(s, CX + 20, DY + 128, 200, 22, "＋ 弊社の生花", size=12, color=SECONDARY, bold=True)
chip(s, CX + 20, DY + 152, 204, "ミニブーケ・一輪ブーケ", fill=T.accent, line=T.accent, color=WHITE, size=13)
chip(s, CX + 236, DY + 152, 204, "ギフトボックスに同梱", fill=WHITE, line=T.accent, color=T.dark, size=13)
text(s, CX + 20, DY + 196, CW - 40, 48, ["受注・顧客データも弊社に蓄積。", "PAPABUBBLE・HAKUBA CRAFTで既に運用中の流れ"], size=13, color=MOSS, spacing=1.4)
# 右：2つの販路
RX, RW = 834, 238
node(s, RX, DY, RW, 120, "取引先のEC", ["イネイブラー。取引先が販売し、", "弊社が代理出荷（現在の形）"], fill=None, line=BORDER_LIGHT, size=13)
node(s, RX, DY + DH - 120, RW, 120, "AND FLOWER EC", ["自社EC。全く同じセット商品を", "弊社が販売・出荷"], fill=None, line=T.accent, title_color=T.dark, size=13)
# 矢印
arrow(s, 256, DY + DH / 2, CX, DY + DH / 2)
text(s, 256, DY + DH / 2 - 28, CX - 256, 22, "納品", size=12, color=SECONDARY, align=PP_ALIGN.CENTER)
arrow(s, CX + CW, DY + 60, RX, DY + 60)
arrow(s, CX + CW, DY + DH - 60, RX, DY + DH - 60)
text(s, CX + CW, DY + 34, RX - CX - CW, 22, "出荷", size=12, color=SECONDARY, align=PP_ALIGN.CENTER)
text(s, CX + CW, DY + DH - 86, RX - CX - CW, 22, "販売", size=12, color=SECONDARY, align=PP_ALIGN.CENTER)
text(s, RX, DY + DH + 16, RW + 10, 22, "→ どちらも弊社拠点からお客様へ直接お届け", size=11, color=SECONDARY)
# 下段：意味合い
hline(s, 56, 444, 1016)
cols3 = [(56, "追加の仕組みは不要", ["在庫・出荷は既に弊社側に置く運用。", "AND FLOWERの商品として登録すれば", "すぐ販売できる"]),
         (396, "取引先は販路が増える", ["弊社の会員43.5万人・SNS32.1万人に", "商品が届く。取引先の出荷作業は", "発生しない"]),
         (736, "弊社は品揃えと粗利が増える", ["セット商品が AND FLOWER の", "ラインナップになり、顧客データも", "弊社に残る"])]
for x, t_, ls in cols3:
    y = panel(s, x, 466, 336, t_, size=17)
    text(s, x, y - 6, 336, 80, ls, size=14, spacing=1.45)
text(s, 56, 630, 1016, 60, ["イネイブラー事業を卸・代理出荷で終わらせず、弊社ECの品揃えも充実させる。これをフックに中長期の売上をつくる。"],
     size=17, bold=True, spacing=1.45)
footnote(s, "※ PAPABUBBLE様には11/12の提案（ご提案2「御社商品とのブーケセットの弊社EC販売」）で提示済み。今後の生花案件は原則この形で提案する")

# --- イネイブラー: 1件あたりのエコノミクス ---
s = content_slide("イネイブラー：1件あたりのエコノミクス")
message(s, "新料金（送料込み）で、生花の貢献利益率は20〜35%。小さいブーケほど作業費の比重が重い")
text(s, 56, 154, 560, 24, "1件あたりのエコノミクス（新料金・送料込み・税抜）", size=14, color=SECONDARY, bold=True)
ey, erh = 184, 42
rect(s, 56, ey + 38 + (len(EN_ECON) - 1) * erh, 1016, erh - 3, PALE)  # 日立の試算は例なので網掛け
kpi_table(s, 56, ey, 1016, ["", "B2B下代", "限界利益率", "貢献利益率"], [
    [n_, f"{p_:,}円", f"{r_:.0f}%", f"{cr_:.0f}%"] for n_, p_, r_, c_, cr_ in EN_ECON
], col_w=[556, 150, 150, 160], row_h=erh)
ly = ey + 38 + len(EN_ECON) * erh + 6
rect(s, 56, ly + 4, 18, 14, PALE)
text(s, 82, ly, 500, 22, "網掛け＝プリザーブド卸の試算例（日立ビルシステム向け）", size=12, color=SECONDARY)
y = panel(s, 56, ly + 40, 1016, "前提", size=17)
bullets(s, 56, y - 4, 1016, [
    "卸値はEC価格の8掛け。送料は別建てで、送料差益率は33〜44%",
    "先方ラベルで出荷する場合は同梱作業費300円（ギフティ様と合意済み）",
    "通年は月20件、イベントは100件以上の最小ロットを契約に明記",
    "貢献利益＝下代＋送料収入 − 花材・資材・送料実費 − 作業費。貢献利益率は下代＋送料収入に対する比率",
], size=14, gap=6)
footnote(s, "※ Notion「新料金・エコノミクス（2026年10月以降）」の通常配送（送料含む）ベース。作業費は分給ベース。プリ卸は下代1,150円・貢献利益392円の試算")

# --- イネイブラー: 案件の詳細 ---
s = content_slide("案件の詳細：既存3社の進捗と次の一手")
cards = [(56, "PAPABUBBLE", [
            "7/15 ギフティ同席で商談開始 → 10/13 リリース。キャンディ2種×花4種、ギフトカード有無で16SKU（上代3,280〜10,980円）",
            "受注は週2回（月・木15時）の手動連携 → Domuzが代理注文し翌日発送",
            "11/12 EC事業部長に提案：1月から新ギフトボックス版を追加、商品ページを刷新、AND FLOWER ECでもブーケセットを販売",
            "母の日は先方の考えを確認（こちらから新セットは出さない）"]),
         (396, "HAKUBA CRAFT", [
            "プリザーブド（ガラスL 1,500円×200個＝0.3百万円）を10/28に納品済み。3本セットの撮影を無償で対応し、PR TIMESで告知予定",
            "ビール×生花のギフトセットは11/11にキックオフ。最短12月ローンチ",
            "酒類蔵置所の登録、冷蔵保管と中量ラックを川崎拠点に用意",
            "初回は20セット前後。140サイズ段ボール3箱分の冷蔵保管"]),
         (736, "野菜をMOTTO（モンマルシェ）", [
            "ギフティ川崎さんのご紹介。9/4 初回 → 11/11 常務（決裁者）と商談",
            "母の日はスープ×カーネーションで約5万セット。生花セット（3,980円）は2,000前後で途中完売 → [[来年の母の日に2,000〜3,000個のテスト]]に前向き",
            "提示3案（プリ卸700円／筒入り一輪 花700＋同梱750円／ミニブーケ 980＋750円）は「原価1,450円では採算が合わない」",
            "先方の箱とスープを受け取り、箱の形・1SKUか2SKUか・同梱費用を詰めて再提案。1月の企画開始に間に合わせる"])]
for x, title_, items in cards:
    y = panel(s, x, 150, 336, title_, size=19)
    bullets(s, x, y, 336, items, size=13, gap=8)
text(s, 56, 690, 1016, 50, ["販路は LINEギフト限定3,000個＋自社EC 1,000個を想定。貢献利益1.5百万円を残せるかが分水嶺。"],
     size=16, bold=True, spacing=1.45)
footnote(s, "※ 価格は税抜。野菜をMOTTOの試算は5,000個×1,700円＝売上8.5百万円、貢献利益20%で1.6〜1.7百万円（社内の仮置き）")

# --- イネイブラー: ギフティ経由の案件 ---
s = content_slide("ギフティ経由の案件：TENTIAL と 日立ビルシステム")
message(s, f"どちらも1万件規模。日立は売上{HITACHI['sales'][0]:.1f}〜{HITACHI['sales'][2]:.1f}百万円、TENTIALは2,000円×1万件なら20百万円")
y = panel(s, 56, 160, 488, "TENTIAL（BAKUNE）：母の日〜父の日で1万件")
bullets(s, 56, y, 488, [
    "10/26 ギフティと事前MTG → 10/28 商談（Omori様・Doguchi様）",
    "BAKUNE DRY（母の日の売れ筋、XS〜5XL）×花。上代5,000円前後、ギフティの取り分は600〜700円",
    "母の日から父の日までのCPNで1万件は出る見込み。希少性を持たせて早めに締め切る案も",
    "11月中に企画を決定。先行してバレンタインにプリザーブド、LINEギフトへの展開も可能",
    "Domuzは送料・箱・同梱作業込み2,000円の花で提示（ギフティ田渕さんに回答中）",
    "論点：一般医療機器の取扱い、ギフトカード有効化の方式（Domuz保管なら外部システム）、在庫・システム費",
], size=14)
vline(s, 564, 160, 500)
y = panel(s, 584, 160, 488, f"日立ビルシステム：70周年ギフト {HITACHI['qty']:,}件")
bullets(s, 584, y, 488, [
    "300拠点に配送し拠点長から手渡し。プラケース入りプリザーブド（赤バラ・白、ボトルにシール）。箱はShizaiと直接",
    f"見積3案：① 卸のみ {HITACHI['price'][0]:,}円 ② 箱詰めまで {HITACHI['price'][1]:,}円 ③ カタログとのセット組み＋300拠点配送 {HITACHI['price'][2]:,}円＋送料・段ボール",
    f"売上 {HITACHI['sales'][0]:.1f}／{HITACHI['sales'][1]:.1f}／{HITACHI['sales'][2]:.1f}百万円、貢献利益 {HITACHI['contrib'][0]:.1f}／{HITACHI['contrib'][1]:.1f}／{HITACHI['contrib'][2]:.1f}百万円。③は自社の作業が増えない",
    "11/27 発注・数量確定 → ①② 2/26、③ 3/5 納品。色違い3案のサンプルを送付済み",
    f"論点：花材の先行購入{HITACHI['prepay']:.1f}百万円（着手金のお願い）、外注先（3,000〜5,000個）の配分、佐川の正式見積",
], size=14)
text(s, 56, 690, 1016, 50, ["ギフティの法人チャネルと、Domuzの制作・同梱・配送を組み合わせた形。受注後の生産体制（社内＋外注）を先に固める。"],
     size=16, bold=True, spacing=1.45)
footnote(s, "※ 税抜。日立は受注前の社内試算（11/9時点）。ギフティ様は③を希望、日立様は「カタログのみ」か「カタログ＋花」かを検討中")

# --- 箱 ---
s = content_slide("箱：60サイズ1種類＋キャッチ2種で、12月に営業開始")
message(s, f"11/27 入稿 → 12/11頃 納品。初回は両社で約{BOX['qty'][2]:,}個、1個あたり{BOX['unit'][2]:.0f}円（初期費用込み{BOX['per'][2]}円）")
y = panel(s, 56, 160, 488, "仕様（11/5 3社打合せで確定）")
bullets(s, 56, y, 488, [
    "60サイズ横型 約30×19×10cm。白段ボール・両面2色のフレキソ印刷。両社のロゴを出さない共通デザイン、伝票は外箱に直貼り",
    "キャッチ①（Domuz用・1パーツ）：ミニブーケS〜M＋小物。AND FLOWER・イネイブラーで共用",
    "キャッチ②（ギフティ専用・2パーツ）：ミニブーケS＋ギフトブック（15×15×2cm）＋カード。形はギフティ様とShizaiで直接決める",
    "ギフティ様の商品は4展開で開始：生花×カード／生花×ギフトブック／プリ×カード／プリ×ギフトブック",
    "ネコポス（ポスト投函）箱は保留。プリはプラ筒入りでも実施可",
    "流れ：ギフティ様がキャッチを組み同梱物を入れて納品 → Domuzが花を入れて封緘 → ギフティ様手配の配送で引き取り",
], size=14)
vline(s, 564, 160, 500)
text(s, 584, 160, 488, 24, "費用の目安（Shizai見積・税抜・箱＋Domuz用キャッチ）", size=14, color=SECONDARY, bold=True)
kpi_table(s, 584, 190, 488, ["", *[f"{q:,}個" for q in BOX["qty"]]], [
    ["単価", *[f"{u:.1f}円" for u in BOX["unit"]]],
    ["合計（初期費用込み）", *[f"{t:.2f}百万円" for t in BOX["total"]]],
    ["1個あたり（初期費用込み）", *[f"{p}円" for p in BOX["per"]]],
], col_w=[218, 90, 90, 90], row_h=34)
text(s, 584, 326, 488, 60, [f"初期費用 約{BOX['initial'] * 100:.0f}万円（木型・フレキソ版）。ギフティ専用キャッチは別途（初期費用+約{BOX['giftee_catch_extra'] * 100:.0f}万円の見込み）",
                            "数量は両社合計で発注し、納品・請求は各社に分ける"], size=13, color=SECONDARY, spacing=1.4)
text(s, 584, 400, 488, 24, "スケジュール", size=14, color=SECONDARY, bold=True)
grid(s, 584, 430, [110, 378], ["日付", "内容"], [
    ["11/16", "3社打合せ@川崎。作り直した試作でキャッチの形を確認"],
    ["11/24", "配送テストを経てキャッチ2種の形式を確定"],
    ["11/27", "Shizaiへ入稿。初回数量・納品先を確定（ギフティ様 約3,000個、Domuz 2,000〜3,000個）"],
    ["12/11頃", "納品 → 12月 営業開始 → 1月 実施開始"],
], size=12, row_h=40)
text(s, 56, 690, 1016, 50, ["箱を共通にして資材を増やさず、送料は80→60サイズで1件あたり約300円下がる。母の日に向けた商品づくりにも使う。"],
     size=16, bold=True, spacing=1.45)
footnote(s, "※ 費用は10/21の見積（①通常仕様）。ギフティ専用キャッチの追加費用は見積待ち")

# --- 価格・プラン ---
s = content_slide("価格・プラン：花下代700〜2,400円、同梱300円")
message(s, "10/7のディスカッションペーパーの5つの形（全9パターン）をもとに、11/5までに主要条件を合意")
grid(s, 56, 160, [60, 236, 100, 170, 100, 350], ["No.", "花", "花下代", "貴社同梱物", "サイズ", "備考"], [
    ["1・2", "ミニブーケ（S）", "980円", "カード／カタログ", "60", "ギフト感が出る。カタログは箱へのフィット要検討"],
    ["3・4", "プラケース入り生花", "700円", "カード／カタログ", "60", "上代1,000円以下も見込める。夏季は造花に差替え可"],
    ["5・6", "プラケース入りプリザーブド", "1,300円", "カード／カタログ", "60", "日持ちするため完成品の卸で貴社保管が可能"],
    ["7", "おまかせブーケS", "2,400円", "カードのみ", "60", "ボリューム感。カタログは入らない"],
    ["8・9", "プリザーブドブーケ（貼付型）", "980円", "カード／カタログ", "ネコポス", "送料を下げられる。箱は保留中"],
], size=13, row_h=44)
y = panel(s, 56, 450, 1016, "合意した条件（10/29・11/5）", size=18)
bx = bullets(s, 56, y, 488, [
    "同梱手数料 [[300円／件（税抜）]]。生花はDomuzが同梱・出荷",
    "送料はギフティ様の運送契約で、ギフティ様から直接支払い",
    "プリザーブドは完成品の卸（同梱手数料なし）。最小ロット300個、色分けは300個から。年内請求も可",
], size=14)
bullets(s, 584, y, 488, [
    "夏季（7〜9月）のクール便はOK。費用の見せ方はギフティ様が決める",
    "花材・色はおまかせ。リボン・ラッピングは1色固定（色はギフティ様）",
    "金券・信書の扱いはクライアントの責任で問題なし。ギフティ様は2027年に花 約4,500個（最低3,000個）を計画",
], size=14)
footnote(s, "※ 花下代に送料・同梱手数料・段ボール代は含まない。プラケース代・ラッピング代は含む。金額はエコノミクスや役務分岐で変動の可能性あり")

# --- 付加価値と拠点 ---
s = content_slide("イネイブラー以外の付加価値と、拠点・体制")
y = panel(s, 56, 150, 488, "ギフティグループに提供できる価値")
bullets(s, 56, y, 488, [
    "グリーンレンタル／オフィスコーディネート（8/6ご提案。150〜180cmを月3,500円以下で）",
    "フラワー・グリーンコンシェルジュ（法人の祝い花・胡蝶蘭。胡蝶蘭100SKU・14ラッピングを今月追加）",
    "Domuz eGift（giftee eGift Systemで運用中。10月は14件・61,500円）",
    "ケアアプリ／CRM（購入後の水やり通知・育て方・植え替え提案。他社への機能提供も可）",
    "共同仕入れ：リファはドロップシップ掛率65%→倉庫納品で50%台。グループでまとめれば40%台を狙える",
    "グループ営業：結婚式場向けにスワッグ・カード・金券・eギフトの4商材を一緒に提案",
    "LINEギフト等での花バンドル（GODIVAなどの実績）。Domuzの面でも販売可能",
], size=14)
vline(s, 564, 150, 520)
y = panel(s, 584, 150, 488, "拠点と体制")
bullets(s, 584, y, 488, [
    "川崎 花拠点（約500㎡）：生花・イネイブラーの同梱、60サイズ箱の保管。12月開始3社の商品（冷蔵含む）をここに置く",
    "横浜 観葉ハウス（約3,000㎡）・仲町台・三和園芸（委託）・SBS（汎用3PL。連携機能を11/16リリース）",
    "GFC（川崎SRC）との同居案：横持ちコストの最小化と鮮度維持。日立③は佐川の倉庫でセット組み",
    "事業開発 11/1入社（村上）。2027年3月に物流責任者（SBS出身・3PL立上げ20年）が入社予定",
    "観葉の生産拠点：加藤拠点は借りず、現ハウスを維持しつつ隣のハウスを交渉。関東（埼玉・群馬）の用地も情報収集",
    "イネイブラー向けの保管スペースは川崎のネステナー改善で確保。クリスマス前に整理",
], size=14)
footnote(s, "※ 共同仕入れの掛率は11/8の打合せでの先方提示値。体制は入社前の予定を含む")

# =====================================================================
# 4. カインズ
# =====================================================================
divider("03", "CAINZ", "カインズとの協業", "ECOPOTS卸から、リアル店舗・EC・生産拠点へ")

s = content_slide("カインズ：ECOPOTS卸が決まり、協業範囲は「全部」")
message(s, "来春 約30点×30店舗（全250店舗）から。カインズは種苗〜生産〜物流〜販売の全領域で組みたい意向")
grid(s, 56, 160, [90, 190, 736], ["日付", "形式", "内容と決まったこと"], [
    ["9/4", "初回（オンライン）", "Live Green構想、ECOPOTS、ケアアプリ。ECOPOTS卸を「やる前提」で進める。産地の話はNDA後"],
    ["10/2", "2回目（オンライン）", "NDA締結へ（10/16締結）。関東の供給確保が課題、One ID戦略、「植物ECを丸ごと委託」の可能性に初めて言及"],
    ["10/29", "本庄本部 訪問", "ECOPOTS卸：来春30点×30店舗で試験展開、5.5掛け、センター一括か問屋経由、2月納品。APグッズ・花瓶も見積"],
    ["11/6", "3回目（オンライン）", "協業範囲は「全部」。OMO・ワンデータ、関東の共同生産施設、資本を含む「契り」の打診。次回はDomuzが具体案"],
    ["11/13・17", "4回目・5回目", "Domuzから足元の具体案2〜3と全体ストーリーを提案（11/13 14:00、11/17 14:00）"],
], size=13, row_h=56)
y = panel(s, 56, 500, 488, "ECOPOTS／オリジナル園芸商品の卸", size=18)
bullets(s, 56, y, 488, [
    "上代はAP ECと同じ。カインズ向け5.5掛け（下代3万円以上は送料無料）",
    "園芸コーナーに「島」で置き、半年見て良ければ次の春から拡大（最後まで残ると255店舗）",
    "APオリジナルグッズ・花瓶・土／肥料の卸も提案中。中長期ではPB化の話も",
], size=13)
y = panel(s, 584, 500, 488, "カインズが本当に欲しいもの", size=18)
bullets(s, 584, y, 488, [
    "新しい客（20代女性）、続く客（CRM）、店の外で売る場所（植物ECは売上ゼロ）",
    "土台はタマ（商品）。2027年の第一優先は在庫確保、関東に生産基盤がない",
    "自前で作ると3〜5年。花博に間に合わせるため、APと組んで時間を買いたい",
], size=13)
footnote(s, "※ カインズ：ペット・ガーデン事業本部（清水本部長・武川グリーン部MC・バイヤー2名）。Domuz：髙木・小松・佐藤・大杉")

s = content_slide("カインズ：リアル店舗から始め、ECと生産拠点へ広げる")
message(s, "花博（2027年3〜9月・横浜）までに受け皿を用意し、CRMでつなぎ続ける")
steps = [(56, "STEP 1　〜2027年3月", "リアル店舗（提案中）", [
            "ECOPOTS・APグッズを30店舗にトライアル展開し、APブースとして販売",
            "店頭でのライブ販売、一点ものの販売会、植え替えサービスの受付、ワークショップ",
            "店頭QR→ケアアプリ登録。カインズ経由の印を付け、店舗キャンペーンを通知して戻ってきてもらう"]),
         (396, "STEP 2　2027年上期〜", "カインズEC＆アプリ連携", [
            "カインズECの植物カテゴリーをDomuzが受託（運営・発送・購入後サポート）",
            "ケアアプリの機能提供とCRM。IDは統合ではなく連携、匿名・集計データをカインズに返す",
            "運営の範囲・手数料・データの線引きを先に決める"]),
         (736, "STEP 3　2027年下期〜", "生産拠点＆発送拠点の共同開発", [
            "主戦場（埼玉・神奈川・群馬・栃木）で安定供給できる施設を共同でつくり、腕のいい生産者を囲う",
            "沖縄・指宿の観葉を関東で生産できないか調査中（物流費・生産者の減少）",
            "発送拠点も共同で。需要予測を三者で共有して計画生産"])]
for x, step, title_, items in steps:
    text(s, x, 160, 336, 20, step, size=12, color=T.dark, bold=True, en=True)
    y = panel(s, x, 184, 336, title_, size=18)
    bullets(s, x, y, 336, items, size=13, gap=8)
y = panel(s, 56, 470, 488, "花博がアツい", size=18)
bullets(s, 56, y, 488, [
    "カインズは157店舗で公式グッズ・チケットを販売し、会期中の5月と9月に出展。社内のグリーン熱量は過去最高",
    "横浜市との連携案はカインズ側で考えられていない。横浜に拠点を持つDomuzから提案できる余地",
], size=13)
y = panel(s, 584, 470, 488, "資本の話", size=18)
bullets(s, 584, y, 488, [
    "清水本部長から、口約束でなく契約・資本を含む「契り」の打診。ベイシアグループ入りの話も（冗談ベースで2回）",
    "まず少数出資で業務連携を進め、生産を本格化するなら共同出資会社、という順番を想定。ギフティとの関係と合わせて整理したい",
], size=13)
footnote(s, "※ 11/6の商談（Circleback）とカインズ投影資料、社内の協業方針（11/11）をもとに作成。STEP 2・3はカインズ側の資料のロードマップ案")

# =====================================================================
# 5. 資本の論点と今後の関わり方
# =====================================================================
divider("04", "CAPITAL & NEXT STEPS", "資本の論点と今後の関わり方", "49%のケースの資金調達条件、ギフティと進めること")

s = content_slide("資本：49%のケースで追加資金が要るときの条件")
message(s, "49%で止めた後に資金が不足し、CBで調達すると既存株主の持分が大きく減る。その条件を確認したい")
y = panel(s, 56, 160, 488, "前提")
bullets(s, 56, y, 488, [
    "累計エクイティ調達 7.4億円（うち優先株 7.0億円、ギフティ様 4.3億円）",
    f"10月は売上が計画比{(1 - TOTAL['sales'][i10] / PLAN_OCT['total']) * 100:.0f}%未達で、営業赤字が想定より拡大。母の日（4〜5月）までの運転資金を確認中",
    "AP/AFは営業・インターン・コンシェルジュの人員を減らし、売上とROASが想定どおりなら今期はトントンの見込み",
    "ファイナンスは既存投資家・ギフティ様と協議中。カインズからも資本参加の打診",
], size=14)
vline(s, 564, 160, 440)
y = panel(s, 584, 160, 488, "確認したいこと")
bullets(s, 584, y, 488, [
    "① 49%取得後に資金が不足した場合の対応方針（追加出資／CB／デット／グループ内融資）と、ギフティ様の引受可否",
    "② CBとする場合の条件：転換価格、ディスカウント、バリュエーションキャップ、転換時期、既存株主（優先株）との優先関係",
    "③ 49%で止める場合のガバナンス（取締役派遣・事前承認事項）と、100%の場合との違い",
    "④ カインズ（ベイシアグループ）の資本参加の可能性との整理（排他性・競合の扱い）",
], size=14)
text(s, 56, 620, 1016, 90, ["希薄化を抑えつつ運転資金を確保する順番を、今月中に合意したい。",
                            "ハナイチの採算（卸込み）は年内に判断し、資本の話と合わせて来期の計画に反映する。"],
     size=17, bold=True, spacing=1.5)
footnote(s, "※ 調達額は過去の共有資料の値。10月の損益は発送ベースの暫定値で、試算表の確定後に差分を照合")

s = content_slide("今後の関わり方：12月の営業開始から母の日まで")
grid(s, 56, 150, [130, 886], ["時期", "ギフティ様と進めること／Domuzの動き"], [
    ["11月", "60サイズ箱の入稿（11/27）、日立の見積提示と発注確定（11/27）、TENTIALの企画決定、野菜をMOTTOへ再提案、カインズ提案（11/13・11/17）"],
    ["12月", "giftee.comで各社の営業開始、箱の納品（12/11頃）、生花3案件のローンチ（HAKUBA CRAFT・SILK THE RICH・Color Your Life）、ハナイチ採算の判断"],
    ["1月", "ギフティ様施策の実施開始（4展開）、プリザーブドの卸納品（バレンタイン向け）、母の日企画の開始（野菜をMOTTO・TENTIAL）、花博準備"],
    ["2〜3月", "日立の納品（①② 2/26、③ 3/5）、ECOPOTS 30店舗への納品、花博開幕（3月）、カインズ店舗でのAPブース実証"],
    ["4〜5月", "母の日（AP/AFは約93百万円の見込み、目標1億円）。TENTIAL 1万件、野菜をMOTTO 2,000〜3,000個、ギフティ様の母の日施策"],
], size=13, row_h=52)
y = panel(s, 56, 470, 488, "ギフティグループとして一緒にやりたいこと", size=18)
bullets(s, 56, y, 488, [
    "共同仕入れ（リファなど）で掛率を10%下げる。式場向けのグループ営業",
    "法人チャネル（2,276社）・LINEギフトとの連携に、花バンドルを載せる",
    "GFC（川崎SRC）との同居で横持ちを最小化し、通年オケージョンへ",
], size=13)
y = panel(s, 584, 470, 488, "Domuzからのお願い", size=18)
bullets(s, 584, y, 488, [
    "初回の箱の数量・納品先（11/27）、専用キャッチの形（11/16）、ラッピングの色",
    "日立：③の配送形態（五月雨か3/5一括か）、予算感、ロゴ・指定色",
    "資本：49%のケースの資金調達条件（前ページ）",
], size=13)
footnote(s, "※ 母の日の見込みは経営MTG（11/9）の暫定値。スケジュールは11/9時点")

# =====================================================================
# 6. 要約（数字が出そろったので埋める）・用語
# =====================================================================
draw_claims(summary, [
    ("1", f"10月の売上高は{TB_SALES[-1]:.1f}百万円（昨年対比{pct(TB_SALES[-1], TB_SALES[0])}）、限界利益{TB_MP[-1]:.1f}百万円（{pct(TB_MP[-1], TB_MP[0])}）", [
        f"広告宣伝費{TB_AD[-1]:.1f}百万円（前月比{pct(TB_AD[-1], TB_AD[-2])}）に対し売上は前月比{pct(TB_SALES[-1], TB_SALES[-2])}。全体ROASは{TB_ROAS[-2]:.0f}%→{TB_ROAS[-1]:.0f}%",
        f"AP/AF自社EC＋モールは{m(TOTAL['sales'][i10])}百万円で計画比{TOTAL['sales'][i10] / PLAN_OCT['total'] * 100:.0f}%。広告費込み限界利益は計画の{TOTAL['net'][i10] / PLAN_OCT['net_total'] * 100:.0f}%"]),
    ("2", "AFは値下げで件数+27%。ハナイチ生花はリピートが積み上がり、出荷能力を強化", [
        f"AFは10/16の価格調整で売上{pct(AF['sales'][i10], AF['sales'][i9])}。貢献利益は▲4.8→▲3.8百万円に縮小。組織分離でOPを立て直す",
        f"生花のリピート注文は昨年10月{HY_REPEAT[0]}→{HY_REPEAT[-1]}件（率{HY_REPEAT_RATE[0]:.0f}%→{HY_REPEAT_RATE[-1]:.0f}%）。発送上限がボトルネックで、体制変更と卸・輸入で強化"]),
    ("3", "イネイブラーは12月から本格稼働。ギフティ経由で1万件規模の案件が2本", [
        f"箱は11/27入稿、同梱手数料300円で合意。日立（{HITACHI['sales'][0]:.1f}〜{HITACHI['sales'][2]:.1f}百万円）とTENTIAL（1万件）"]),
    ("4", "カインズはECOPOTS卸が決定。資本を含む協業の打診も", [
        "来春30店舗から。リアル店舗→EC受託→生産拠点の順で提案し、花博（2027年3月〜）に備える"]),
], y=116)
footnote(summary, "※ 税抜・百万円。用語の定義と集計の前提は最終ページ")

terms_page("用語と集計の前提", [
    ("期", "9月決算。第9期＝2026年10月〜2027年9月。10月は第9期の最初の月"),
    ("売上高", "10月の数字は試算表（マネーフォワード・税抜・暫定）。事業別のページは管理画面（税抜・送料込み・注文日ベース）"),
    ("限界利益", "試算表：売上総利益 − 荷造運賃 − 支払手数料。管理画面：売上 − 商品原価・送料・資材・決済手数料"),
    ("広告費", "媒体別の広告費（Meta・Google・Yahoo!・Criteo・Microsoft・Amazon・楽天）。植物→AP、花→AF、Amazon・楽天→モール、残りは共通"),
    ("広告費込み限界利益", "限界利益 − 広告費。社内の主要KPI"),
    ("貢献利益", "広告費込み限界利益 − 拠点のアルバイト人件費等（直接固定費）。本社の人件費・共通費は含まない"),
    ("計画", "【社内共有】事業計画_AP/AF（2026/10の列）。ハナイチの計画は仮のため使わない"),
    ("リピート率", "ハナイチ生花：リピート注文÷全注文（リーダーMTGのKPI、納品・発送日ベース）"),
    ("イネイブラー", "Domuz以外が主体となり、Domuzの花・植物を提供する形態。売上は発送日ベース（KPI管理表）"),
    ("出典", "試算表（Notion 月次試算表）、admin315（2026/11/11取得）、リーダーMTG 9/4・10/8・11/5、経営MTG 11/9、各商談のNotion・Circleback"),
])

os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
save(out)
