"""外部の数字と出典。本文はここから f-string で組み立てる。
確認日 2026-11-17。いずれも米国の数字で、日本の実績ではない。"""

# 元資料（P1）に書かれていた数字（そのまま使う）
LINE_MAIL_K = 43.5   # LINE・メルマガ 43.5万人
SNS_K = 32.1         # SNS 32.1万人

# Adobe Digital Insights: AI-sourced traffic（米国小売サイト、2025年11〜12月）
# https://business.adobe.com/blog/ai-driven-traffic-surges-across-industries
ADOBE_PERIOD = "2025年11〜12月"
ADOBE_TRAFFIC = "+693%"   # AI経由の流入、前年同期比
ADOBE_CVR = "+31%"        # 購入率、非AI経由との比較

# 2030年の米国ECに占めるAI経由（agentic commerce）の割合の予測
# Bain: https://www.bain.com/insights/2030-forecast-how-agentic-ai-will-reshape-us-retail-snap-chart/
# Morgan Stanley: https://www.morganstanley.com/insights/articles/agentic-commerce-market-impact-outlook
FORECASTS = [
    ("Bain", 15, 25, "bain.com"),
    ("Morgan Stanley", 10, 20, "morganstanley.com"),
]
AI_SHARE_2030 = 20  # 試算で置く値（両予測の重なる範囲の中央）

SOURCES = [
    ("Adobe Digital Insights", f"米国小売サイトへのAI経由の流入は{ADOBE_PERIOD}に前年同期比{ADOBE_TRAFFIC}、購入率は非AI経由と比べて{ADOBE_CVR}（business.adobe.com「AI-driven traffic surges across industries」）"),
    ("Bain & Company", "2030年の米国の agentic commerce は3,000〜5,000億ドル、ECの15〜25%（bain.com「2030 Forecast: How Agentic AI Will Reshape US Retail」2025年12月）"),
    ("Morgan Stanley", "2030年の米国で1,900〜3,850億ドル、オンライン小売の10〜20%（morganstanley.com「Here Come the Shopping Bots」）"),
    ("OpenAI・Stripe", "2025年9月、ChatGPT 内の Instant Checkout と Agentic Commerce Protocol（ACP）を公開。Etsy・Shopify の加盟店から開始"),
    ("Google・Shopify", "2026年1月、Universal Commerce Protocol（UCP）を発表。Gemini からの商品検索・注文に使う"),
    ("Anthropic", "Model Context Protocol（MCP）。Claude 等の AI が外部のデータ・ツールに接続する共通仕様。Shopify の Storefront MCP 等が対応"),
    ("試算のイメージ", f"P4 右の図は市場＝100、AI経由{AI_SHARE_2030}%を置いた試算で、実績・社内計画の数字ではない。陳列型が AI経由を全く取れない前提も単純化"),
    ("P1 の数字", f"LINE・メルマガ{LINE_MAIL_K}万人、SNS{SNS_K}万人は元資料の記載をそのまま使用"),
]
