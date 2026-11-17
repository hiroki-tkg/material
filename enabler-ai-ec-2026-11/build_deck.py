"""イネイブラー → ギフトEC → AI経由の購買（MCP開放）の方針スライド。Domuz「発表スライド」型で .pptx を生成する。

    python3 build_deck.py out/enabler_ai_ec.pptx
    bash <skill>/scripts/render.sh out/enabler_ai_ec.pptx "イネイブラーとAI経由の購買" "2026.11 株式会社DOMUZ"

P1 は元資料（今後の大きな方針）を同じ内容で作り直したもの。P2 以降が追加。
外部の数字は data_sources.py にまとめ、本文は f-string で組み立てる。
"""
import os
import sys

SKILL = ("/root/.claude/skills/synced/c877595e-9c45-49a9-8ea7-19fa3e366349_909874ba-85e7-4fba-9ee5-df754fdb136c"
         "/domuz-deck/scripts")
sys.path.insert(0, SKILL)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deck_lib import *  # noqa: E402,F401
from deck_lib import _set_font  # noqa: E402
from data_sources import *  # noqa: E402,F401

use_theme("domuz")
out = sys.argv[1] if len(sys.argv) > 1 else "out/enabler_ai_ec.pptx"

PANEL = RGBColor(0xEE, 0xF1, 0xF1)       # 拠点・お客様の地（元資料の薄いグレー）
TINT = RGBColor(0xE6, 0xFA, 0xF3)        # 応答型の列の薄い緑
RED = RGBColor(0xE0, 0x00, 0x00)
C, L, R = PP_ALIGN.CENTER, PP_ALIGN.LEFT, PP_ALIGN.RIGHT
MID = MSO_ANCHOR.MIDDLE


# ---------------------------------------------------------------- 小部品
def confidential(s):
    rect(s, 996, 18, 96, 28, None, line=RED, weight=1.5)
    text(s, 996, 18, 96, 28, "Confidential", size=13, color=RED, bold=True, align=C, anchor=MID, spacing=1.0, en=True)


def page(title, msg=None, title_size=38):
    """content_slide にタイトルサイズの指定と Confidential を足したもの。"""
    s = content_slide()
    text(s, MARGIN, 44, 1000, 56, title, size=title_size, bold=True, anchor=MID, spacing=1.0)
    if msg:
        message(s, msg)
    confidential(s)
    return s


def harrow(s, x0, x1, y, color=MOSS, weight=2.0, head=12):
    """水平の矢印（x0 → x1。x1 < x0 なら左向き）。線＋三角で描く。"""
    right = x1 >= x0
    a, b = (x0, x1) if right else (x1, x0)
    hline(s, a + (0 if right else head - 2), y, (b - a) - head + 2, color, weight)
    tri = rect(s, (b - head) if right else a, y - head * 0.6, head, head * 1.2, color, shape=MSO_SHAPE.ISOSCELES_TRIANGLE)
    tri.rotation = 90.0 if right else 270.0
    return tri


def pill(s, x, y, w, h, label, fill=WHITE, line=BORDER_LIGHT, color=MOSS, size=14, bold=True, weight=1.5, round_=True):
    rect(s, x, y, w, h, fill, line=line, weight=weight,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE if round_ else MSO_SHAPE.RECTANGLE)
    text(s, x + 6, y, w - 12, h, label, size=size, color=color, bold=bold, align=C, anchor=MID, spacing=1.0)


def person(s, cx, cy, r=12, color=MOSS):
    rect(s, cx - r, cy - r, 2 * r, 2 * r, color, shape=MSO_SHAPE.OVAL)
    rect(s, cx - r * 1.6, cy + r * 1.2, r * 3.2, r * 1.9, color, shape=MSO_SHAPE.ROUND_2_SAME_RECTANGLE)


def flower(s, cx, cy, r=5, petal=FLOWER, core=HANA):
    import math
    for k in range(5):
        a = math.radians(90 + k * 72)
        rect(s, cx + math.cos(a) * r * 1.1 - r * 0.8, cy - math.sin(a) * r * 1.1 - r * 0.8, r * 1.6, r * 1.6, petal,
             shape=MSO_SHAPE.OVAL)
    rect(s, cx - r * 0.6, cy - r * 0.6, r * 1.2, r * 1.2, core, shape=MSO_SHAPE.OVAL)


def bullets(s, x, y, w, lines, size=13, color=MOSS, step=None, sq=T.accent, spacing=1.3):
    """小さな四角＋1行の箇条書き。各行の高さは step（既定は size×2）。"""
    step = step or int(size * 2)
    for i, ln_ in enumerate(lines):
        rect(s, x, y + i * step + size * 0.55, 6, 6, sq)
        text(s, x + 14, y + i * step, w - 14, step, ln_, size=size, color=color, spacing=spacing, anchor=MID)
    return y + len(lines) * step


def underline_runs(tb, needle):
    for p in tb.text_frame.paragraphs:
        for r in p.runs:
            if r.text == needle:
                r.font.underline = True


def rounded(s, x, y, w, h, fill, line=None, weight=1.5, dash=False, radius=0.06):
    sh = rect(s, x, y, w, h, fill, line=line, weight=weight, dash=dash, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    sh.adjustments[0] = radius
    return sh


# ================================================================ P1 元資料（作り直し）
s = page("今後の大きな方針：イネイブラー商品を自社ECでも販売")
text(s, MARGIN, 104, 1000, 36, "取引先の商品を弊社が在庫として預かり、取引先ECと AND FLOWER の両方で同じセットを売る",
     size=20, color=SECONDARY)

# 取引先
rect(s, 56, 156, 174, 296, WHITE, line=BORDER_LIGHT)
text(s, 72, 170, 150, 28, "取引先", size=20, bold=True, spacing=1.0)
text(s, 72, 202, 150, 40, ["商品を弊社拠点へ", "まとめて納品"], size=13, color=SECONDARY, spacing=1.3)
for i, lab in enumerate(["キャンディ", "スープ", "コスメ", "スイーツ"]):
    pill(s, 72, 256 + i * 38, 142, 30, lab, size=14)
text(s, 72, 410, 142, 24, "など", size=12, color=SECONDARY, align=R)
harrow(s, 232, 272, 304)
text(s, 228, 282, 48, 18, "納品", size=11, color=SECONDARY, align=C, spacing=1.0)

# Domuz 川崎拠点
rect(s, 274, 156, 402, 296, PANEL, line=T.accent, weight=2.5)
text(s, 274, 168, 402, 32, "Domuz 川崎拠点", size=24, bold=True, align=C, spacing=1.0)
text(s, 284, 202, 382, 20, "取引先の商品を委託在庫として保管、生花とセットで発送", size=13, color=SECONDARY, align=C, spacing=1.0)
text(s, 296, 234, 200, 18, "取引先の商品", size=12, bold=True, color=SECONDARY, spacing=1.0)
for i, lab in enumerate(["キャンディ", "スープ", "コスメ", "スイーツ"]):
    pill(s, 296 + i * 92, 256, 84, 30, lab, size=13)
text(s, 290, 298, 30, 42, "+", size=26, bold=True, align=C, anchor=MID, spacing=1.0, en=True)
pill(s, 322, 298, 334, 42, "", line=T.accent, weight=2)
flower(s, 346, 319, r=6)
text(s, 364, 300, 290, 40, ["**AND FLOWER の花**", "（ミニブーケ、フラワーボックス等）"], size=12, spacing=1.15, anchor=MID)
text(s, 290, 350, 30, 36, "=", size=26, bold=True, align=C, anchor=MID, spacing=1.0, en=True)
pill(s, 322, 350, 334, 36, "ギフトボックスにセットで同梱して出荷", fill=T.accent, line=None, color=WHITE, size=14)
text(s, 296, 396, 360, 20, "※ 受注・顧客データも弊社に蓄積", size=12, color=SECONDARY, align=R, spacing=1.0)

# 取引先のEC / AND FLOWER EC / お客様
rect(s, 746, 156, 192, 130, WHITE, line=BORDER_LIGHT)
text(s, 762, 170, 170, 28, "取引先の EC", size=20, bold=True, spacing=1.0)
text(s, 762, 202, 170, 70, ["イネイブラー", "取引先が販売し", "注文情報を弊社へ連携"], size=13, color=SECONDARY, spacing=1.3)
rect(s, 746, 322, 192, 130, WHITE, line=T.accent, weight=2)
text(s, 762, 336, 176, 28, "AND FLOWER EC", size=17, bold=True, spacing=1.0)
text(s, 762, 368, 170, 70, ["自社EC", "全く同じセット商品を", "弊社が販売・出荷"], size=13, color=SECONDARY, spacing=1.3)
rounded(s, 998, 156, 74, 296, PANEL, line=T.accent, weight=2, radius=0.12)
person(s, 1035, 282, r=12)
text(s, 998, 322, 74, 24, "お客様", size=13, bold=True, align=C, spacing=1.0)

harrow(s, 744, 680, 222)
text(s, 684, 200, 56, 18, "注文情報", size=11, color=SECONDARY, align=C, spacing=1.0)
harrow(s, 680, 996, 298)
text(s, 700, 304, 280, 16, "発送（どちらも弊社拠点から）", size=11, color=SECONDARY, align=C, spacing=1.0)
harrow(s, 680, 744, 387)
text(s, 684, 365, 56, 18, "販売", size=11, color=SECONDARY, align=C, spacing=1.0)
for yy in (222, 387):
    harrow(s, 996, 942, yy)
    text(s, 942, yy - 22, 52, 18, "購入", size=11, color=SECONDARY, align=C, spacing=1.0)

# 4つの効果
hline(s, MARGIN, 480, CONTENT_W)
effects = [
    ("仕組みの追加は不要", ["在庫・出荷は既に弊社側の運用。", "AND FLOWER の商品として", "登録すれば販売できる"]),
    ("取引先の販路が増える", [f"弊社の LINE・メルマガ {LINE_MAIL_K}万人・", f"SNS {SNS_K}万人に商品が届く。", "取引先の出荷作業は発生しない"]),
    ("品揃えと粗利が増える", ["セット商品が AND FLOWER の", "ラインナップになり、", "顧客データも弊社に残る"]),
    ("取引先ECで認知を獲得", ["プラグイン導入で取引先の EC サイト上に", "AND FLOWER の名前が出て、", "被リンクとサイテーションを獲得"]),
]
for i, (head, body) in enumerate(effects):
    x = MARGIN + i * 260
    rect(s, x, 498, 236, 6, T.accent)
    badge(s, x + 11, 531, i + 1, d=22)
    text(s, x + 30, 518, 210, 28, head, size=16, bold=True, anchor=MID, spacing=1.0)
    text(s, x + 8, 552, 232, 80, body, size=12, color=SECONDARY, spacing=1.35)
tb = text(s, MARGIN, 650, CONTENT_W, 64,
          ["イネイブラー事業を卸・代理出荷で終わらせず、花のECに限らずギフト商品がラインナップされた",
           "ギフトECへの転換を図り、これを含め中長期の売上成長を志向する。"], size=19, bold=True, spacing=1.45)
# 「ギフトECへの転換」に下線
p2 = tb.text_frame.paragraphs[1]
r0 = p2.runs[0]
r0.text = "ギフトECへの転換"
r0.font.underline = True
r1 = p2.add_run()
r1.text = "を図り、これを含め中長期の売上成長を志向する。"
_set_font(r1, 19, MOSS, True)
footnote(s, ["※ 在庫の持ち方は、イネイブラーはあくまで取引先からの委託在庫、自社ECでは消化在庫（売れた分を精算）とする形での運用を想定",
             "※ 生花以外の商品を単品で販売する等も可能（例：イネイブラーで扱う取引先の商品を、花付きではなく単体で販売する FLOWARD モデル）"])

# ================================================================ P2 AI経由の購買の流れ
s = page("AIが買い物を仲介する時代：ECの入口がAIに移る",
         "お客様はAIに相談し、AIが各社に在庫・着日・ギフト条件を問い合わせて提案、購入まで進める")

# お客様
person(s, 151, 196, r=22)
text(s, 56, 268, 190, 26, "一般のお客様", size=18, bold=True, align=C, spacing=1.0)
rounded(s, 56, 304, 190, 150, WHITE, line=BORDER_LIGHT, radius=0.08)
text(s, 66, 312, 170, 134,
     ["「母の日に、花とスイーツを", "セットで贈りたい。", "5/10 の午前に届けてほしい。", "予算は 8,000 円くらい」"],
     size=12, spacing=1.4, anchor=MID)
text(s, 56, 470, 190, 70, ["検索して比べて選ぶ", "↓", "AIに相談して任せる"], size=13, color=SECONDARY, align=C, spacing=1.3)

harrow(s, 252, 332, 300)
text(s, 246, 278, 90, 18, "① 相談", size=11, color=SECONDARY, align=C, spacing=1.0)
harrow(s, 332, 252, 346)
text(s, 246, 352, 90, 32, ["③ 提案", "④ 購入を指示"], size=10, color=SECONDARY, align=C, spacing=1.2)

# AIプラットフォーマー
rect(s, 336, 160, 310, 440, WHITE, line=MOSS, weight=2)
rect(s, 336, 160, 310, 44, MOSS)
text(s, 336, 160, 310, 44, "AIプラットフォーマー", size=18, bold=True, color=WHITE, align=C, anchor=MID, spacing=1.0)
for i, name in enumerate(["Claude", "ChatGPT", "Gemini", "Grok", "Perplexity", "…ほか"]):
    pill(s, 350 + (i % 3) * 96, 216 + (i // 3) * 36, 90, 30, name, fill=PALE, line=None, size=13,
         bold=name != "…ほか", color=MOSS if name != "…ほか" else SECONDARY)
text(s, 350, 298, 280, 20, "AIがやること", size=12, bold=True, color=SECONDARY, spacing=1.0)
for i, ln_ in enumerate(["条件に合う商品を各社に問い合わせる", "在庫・着日・ギフト対応で候補を絞り提案", "お客様の了承で注文・決済まで代行"]):
    badge(s, 360, 336 + i * 40, i + 2, d=20)
    text(s, 378, 322 + i * 40, 262, 28, ln_, size=13, anchor=MID, spacing=1.0)
hline(s, 350, 450, 282)
text(s, 350, 462, 282, 120,
     ["AIが見るのは商品ページの文章ではなく、", "MCP等で返ってくる[[構造化された答え]]。", "答えが返らない事業者は候補から外れるか、", "最後に人が確認する手間が残る"],
     size=12, spacing=1.4)

harrow(s, 652, 736, 300)
text(s, 644, 262, 100, 36, ["② 照会", "MCP / ACP / UCP"], size=10, color=SECONDARY, align=C, spacing=1.2)
harrow(s, 736, 652, 346)
text(s, 644, 352, 100, 36, ["在庫・着日・条件を", "即答"], size=10, color=SECONDARY, align=C, spacing=1.2)

# 事業者側
rect(s, 740, 160, 332, 250, WHITE, line=T.accent, weight=2.5)
text(s, 754, 170, 304, 28, "MCPで情報を開放した事業者（Domuz）", size=14, bold=True, anchor=MID, spacing=1.0)
bullets(s, 754, 204, 304, ["リアルタイム在庫（川崎拠点）", "発送日・着日・配送枠", "ギフトオプション（カード・ラッピング・同梱）",
                           "価格・送料・用途（母の日・お供え 等）", "そのまま注文確定（AI内 または 自社EC）"], size=12, step=26)
pill(s, 754, 356, 304, 34, "候補に入り、選ばれる", fill=T.accent, line=None, color=WHITE, size=14)
rect(s, 740, 426, 332, 174, WHITE, line=BORDER_LIGHT, dash=True)
text(s, 754, 436, 304, 28, "開放していない事業者（商品ページだけ）", size=14, bold=True, color=SECONDARY, anchor=MID, spacing=1.0)
bullets(s, 754, 470, 304, ["AIは商品ページの文章を読むだけ", "在庫・着日・ギフト条件はカートまで分からない", "条件つきの相談では提案に入りにくい"],
        size=12, step=26, color=SECONDARY, sq=BG_GRAY)
pill(s, 754, 554, 304, 34, "候補から外れやすい", fill=BG_GRAY, line=None, color=WHITE, size=14)

text(s, MARGIN, 630, CONTENT_W, 64,
     ["AIに聞かれて「今すぐ答えられる」事業者だけが提案に入る。", "入口がAIに移るほど、この差がそのまま売上の差になる"],
     size=19, bold=True, spacing=1.45)
footnote(s, [f"※ 米国では{ADOBE_PERIOD}のAI経由の小売サイト流入が前年比{ADOBE_TRAFFIC}、購入率は非AI経由より{ADOBE_CVR}高い（Adobe）",
             "※ ACP＝Agentic Commerce Protocol、UCP＝Universal Commerce Protocol、MCP＝Model Context Protocol（出典と提供元は P6）"])

# ================================================================ P3 陳列型 vs 応答型
s = page("勝ち筋：陳列されるECから、AIに即答できるプレイヤーへ",
         "選ばれる基準が、検索順位・広告・モール内の露出から「AIの問いに答えられる情報」に変わる", title_size=36)
x0, x1, x2, w1, w2 = 56, 206, 646, 420, 426
ty = 160
rect(s, x1, ty, w1 - 20, 56, PALE)
text(s, x1 + 12, ty + 6, w1 - 44, 24, "既存のギフトEC・楽天・Amazon", size=15, bold=True, spacing=1.0)
text(s, x1 + 12, ty + 30, w1 - 44, 20, "陳列型：商品ページを並べ、見つけてもらう", size=12, color=SECONDARY, spacing=1.0)
rect(s, x2, ty, w2, 56, T.accent)
text(s, x2 + 12, ty + 6, w2 - 24, 24, "MCPに在庫・納期・ギフト条件を開放", size=15, bold=True, color=WHITE, spacing=1.0)
text(s, x2 + 12, ty + 30, w2 - 24, 20, "応答型：AIの問いにリアルタイムで答える", size=12, color=WHITE, spacing=1.0)
rows = [
    ("見つかる場所", ["検索結果・モールのランキング・広告枠"], ["AIとの会話の中で、候補として直接提案される"]),
    ("選ばれる基準", ["検索順位・レビュー・価格・広告費"], ["「今あるか」「いつ届くか」「ギフトにできるか」に", "即答できるか"]),
    ("在庫・着日", ["カート画面まで分からない。", "AIは商品ページの文章を読むだけ"], ["リアルタイムの在庫と配送枠をAIが照会し、", "その場で確定できる"]),
    ("ギフト対応", ["オプションは人が画面で選ぶ。", "モールでは同梱・カードの自由度が低い"], ["カード・ラッピング・同梱セットを「条件」として返し、", "提案そのものに織り込まれる"]),
    ("購入の完了", ["サイトに遷移して人が入力"], ["AI内で注文確定（ACP・UCP 等）、または自社ECへ"]),
    ("顧客データ", ["モールに残り、自社では使えない"], ["自社に残る（イネイブラー経由の注文も）"]),
    ("競争のルール", ["広告費と手数料の勝負（モールの土俵）"], ["情報の鮮度と物流の実力の勝負", "（自社拠点を持つ側の土俵）"]),
]
rh = 60
y = ty + 56
for i, (lab, a, b) in enumerate(rows):
    rect(s, x2, y, w2, rh, TINT)
    hline(s, x0, y, CONTENT_W, BORDER_LIGHT if i else MOSS, 0.75 if i else 1.5)
    text(s, x0, y, 140, rh, lab, size=14, bold=True, anchor=MID, spacing=1.0)
    text(s, x1 + 12, y, w1 - 44, rh, a, size=13, color=SECONDARY, anchor=MID, spacing=1.3)
    text(s, x2 + 12, y, w2 - 24, rh, b, size=13, anchor=MID, spacing=1.3)
    y += rh
hline(s, x0, y, CONTENT_W, MOSS, 1.5)
text(s, MARGIN, 666, CONTENT_W, 40, "モールの中で順位を争うのではなく、AIが問い合わせる先として「最初に挙がる」ギフト事業者になる",
     size=19, bold=True, spacing=1.45)
footnote(s, ["※ ACP・UCP・MCP はいずれも、AIが事業者の商品データ・在庫・注文に直接つなぐための共通仕様（P2 の注記参照）。",
             "　　どの仕様が主流になっても、開放する情報（在庫・着日・ギフト条件）は同じ"])

# ================================================================ P4 グラフ
s = page("中長期の見立て：AI経由の購買は市場の1〜2割へ",
         "AI経由が増えた分は陳列型から失われ、応答型にはそのまま上乗せになる")
# 左：実績と予測
x, w = 56, 470
rect(s, x, 150, w, 6, T.accent)
text(s, x, 170, w, 30, "AI経由の購買は、すでに増え始めている", size=18, bold=True, spacing=1.0)
text(s, x, 200, w, 20, f"米国の小売サイト、{ADOBE_PERIOD}（Adobe）", size=12, color=SECONDARY, spacing=1.0)
big_number(s, x, 228, "AI経由の流入（前年同期比）", ADOBE_TRAFFIC, size=50, w=230)
big_number(s, x + 240, 228, "購入率（非AI経由との差）", ADOBE_CVR, size=50, w=230)
text(s, x, 340, w, 20, "2030年の米国ECに占めるAI経由の購買の割合（予測）", size=12, bold=True, color=SECONDARY, spacing=1.0)
cx0, cw = x + 150, 300  # 0〜30%
pv = lambda p: cx0 + cw * p / 30
for p in (0, 10, 20, 30):
    vline(s, pv(p), 368, 100, WATERMARK if p else BORDER_LIGHT)
    text(s, pv(p) - 20, 470, 40, 16, f"{p}%", size=9, color=MUTED, align=C, en=True)
for i, (name, lo, hi, src) in enumerate(FORECASTS):
    ry = 376 + i * 44
    text(s, x, ry, 140, 28, name, size=13, bold=True, anchor=MID, spacing=1.0)
    rect(s, pv(lo), ry + 4, pv(hi) - pv(lo), 20, T.accent if i == 0 else T.light)
    text(s, pv(hi) + 8, ry, 100, 28, f"{lo}〜{hi}%", size=12, bold=True, anchor=MID, spacing=1.0, en=True)
text(s, x, 492, w, 40, ["予測の幅は定義の違い（AIが購入を開始・影響・完了した取引を", "どこまで含めるか）。いずれも「数%」ではなく「1〜2割」"],
     size=12, color=SECONDARY, spacing=1.3)
# 右：取り分の試算
vline(s, 548, 150, 400)
x, w = 584, 488
rect(s, x, 150, w, 6, MOSS)
text(s, x, 170, w, 30, "市場＝100 としたときの2030年の取り分（試算）", size=18, bold=True, spacing=1.0)
text(s, x, 200, w, 20, f"AI経由が {AI_SHARE_2030}%（予測の中央値）になった場合のイメージ", size=12, color=SECONDARY, spacing=1.0)
legend(s, x, 224, [("従来の経路（検索・モール・SNS）", PALE), ("AI経由", T.accent)])
base_y, unit = 560, 2.2  # 1 = 2.2px → 120 = 264px
bw = 96
cols_x = [x + 24, x + 24 + 150, x + 24 + 300]
keep = 100 - AI_SHARE_2030
# いま
rect(s, cols_x[0], base_y - 100 * unit, bw, 100 * unit, PALE)
text(s, cols_x[0], base_y - 100 * unit - 26, bw, 22, "100", size=16, bold=True, align=C, en=True)
# 陳列型
rect(s, cols_x[1], base_y - keep * unit, bw, keep * unit, PALE)
rect(s, cols_x[1], base_y - 100 * unit, bw, AI_SHARE_2030 * unit, None, line=STRONG, dash=True, weight=1.25)
text(s, cols_x[1] - 20, base_y - 100 * unit, bw + 40, AI_SHARE_2030 * unit, [f"AI経由に", f"移る分 ▲{AI_SHARE_2030}"],
     size=11, bold=True, color=STRONG, align=C, anchor=MID, spacing=1.15)
text(s, cols_x[1], base_y - 100 * unit - 26, bw, 22, f"{keep}", size=16, bold=True, align=C, en=True)
# 応答型
rect(s, cols_x[2], base_y - keep * unit, bw, keep * unit, PALE)
rect(s, cols_x[2], base_y - 100 * unit, bw, AI_SHARE_2030 * unit, T.accent)
text(s, cols_x[2], base_y - 100 * unit, bw, AI_SHARE_2030 * unit, [f"AI経由", f"+{AI_SHARE_2030}"], size=11, bold=True,
     color=WHITE, align=C, anchor=MID, spacing=1.15)
rect(s, cols_x[2], base_y - 120 * unit, bw, 20 * unit, None, line=T.dark, dash=True, weight=1.25)
text(s, cols_x[2] - 20, base_y - 120 * unit, bw + 40, 20 * unit, ["他社の分も", "取りにいける"], size=11, bold=True,
     color=T.dark, align=C, anchor=MID, spacing=1.15)
text(s, cols_x[2], base_y - 120 * unit - 26, bw, 22, "100〜120", size=16, bold=True, align=C, en=True)
hline(s, x + 10, base_y, w - 20, MUTED)
for cx_, lab in zip(cols_x, [["いま"], ["2030年", "陳列型"], ["2030年", "応答型"]]):
    text(s, cx_ - 20, base_y + 6, bw + 40, 36, lab, size=12, color=SECONDARY, align=C, spacing=1.2)
text(s, MARGIN, 642, CONTENT_W, 64,
     [f"AI経由が{AI_SHARE_2030 // 10}割になれば、陳列型は{AI_SHARE_2030 // 10}割を失い、応答型はその{AI_SHARE_2030 // 10}割に加えて他社の分まで取りにいける。",
      "差がつくのは市場が1〜2割に達する前。いま MCP で開放しておくかどうかで決まる"],
     size=19, bold=True, spacing=1.45)
footnote(s, [f"※ {ADOBE_TRAFFIC}・{ADOBE_CVR}は Adobe Digital Insights（米国小売サイト、{ADOBE_PERIOD}）。2030年の割合は Bain と Morgan Stanley の米国EC予測",
             "※ 右の図は市場＝100、AI経由20%を置いた試算のイメージで、実績や社内計画の数字ではない"])

# ================================================================ P5 Domuz の勝ち筋
s = page("Domuzの勝ち筋：P1の仕組みが、AIに開放する情報源になる",
         "自社拠点で在庫と出荷を持ち、イネイブラーで品揃えが広がるから、AIの問いに即答できる", title_size=34)
cols = [
    ("在庫と納期", ["川崎拠点のリアルタイム在庫", "発送日・着日・配送枠", "生花の入荷予定と鮮度"]),
    ("ギフトの条件", ["花 × 取引先商品のセット（P1）", "メッセージカード・ラッピング", "用途（母の日・誕生日・お供え）と予算"]),
    ("注文の確定", ["AIからそのまま注文を受ける", "自社EC・取引先EC どちらも同じ拠点から出荷", "受注・顧客データは自社に蓄積"]),
]
text(s, MARGIN, 150, CONTENT_W, 24, "MCP で開放する情報", size=14, bold=True, color=SECONDARY, spacing=1.0)
for i, (head, items) in enumerate(cols):
    x = MARGIN + i * 347
    rect(s, x, 180, 322, 6, T.accent)
    badge(s, x + 11, 211, i + 1, d=22)
    text(s, x + 30, 198, 290, 28, head, size=18, bold=True, anchor=MID, spacing=1.0)
    bullets(s, x + 2, 236, 320, items, size=13, step=28)
text(s, MARGIN, 338, CONTENT_W, 24, "なぜ Domuz ができるか", size=14, bold=True, color=SECONDARY, spacing=1.0)
why = [
    ("自社拠点で在庫と出荷を持つ", ["モール出店者やドロップシップ型には出せない", "「今あるか・いつ届くか」をその場で返せる"]),
    ("イネイブラーで品揃えが花以外に広がる", ["「花とスイーツ」「花とコスメ」のような相談に", "1社で答えられる。P1 の取引先がそのまま品揃え"]),
    ("管理画面は既に MCP で社内接続済み", ["社内で AI が読んでいる受注・在庫のデータを、", "対外向けに開くだけ。ゼロから作らない"]),
]
for i, (head, body) in enumerate(why):
    x = MARGIN + i * 347
    rect(s, x, 368, 322, 150, WHITE, line=BORDER_LIGHT)
    text(s, x + 14, 380, 296, 44, head, size=14, bold=True, spacing=1.2, anchor=MID)
    text(s, x + 14, 430, 296, 70, body, size=12, color=SECONDARY, spacing=1.4)
text(s, MARGIN, 540, CONTENT_W, 24, "進め方", size=14, bold=True, color=SECONDARY, spacing=1.0)
steps = ["商品・在庫をAIが読める形に（API）", "MCP で在庫・着日・ギフト条件を開放", "AI 内での注文確定・決済に対応"]
sw = 316
for i, st in enumerate(steps):
    x = MARGIN + i * (sw + 34)
    pill(s, x, 568, sw, 40, "", fill=PANEL, line=None)
    badge(s, x + 22, 588, i + 1, d=22)
    text(s, x + 40, 568, sw - 48, 40, st, size=13, bold=True, anchor=MID, spacing=1.0)
    if i < len(steps) - 1:
        harrow(s, x + sw + 6, x + sw + 30, 588, color=T.accent)
text(s, MARGIN, 648, CONTENT_W, 64,
     ["卸・代理出荷 → ギフトEC → AIが最初に問い合わせる「ギフトの応答先」へ。", "P1 の方針はそのままに、AI経由の購買を中長期の売上成長の柱に加える"],
     size=19, bold=True, spacing=1.45)
footnote(s, "※ 進め方の 1〜3 は順番の整理で、時期は事業計画と合わせて別途決める")

# ================================================================ P6 出典
terms_page("出典と前提", SOURCES, row_h=66)
confidential(prs.slides[-1])

os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
save(out)
