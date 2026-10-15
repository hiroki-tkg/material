---
name: domuz-deck
description: Domuz（ドムズ）のデザインシステムで発表スライドを HTML と PDF で作るスキル。「Domuz のデザインで資料を作って」「この Keynote/PowerPoint/Google スライドを Domuz の資料のデザインで作り直して」「MTG 資料」「合宿資料」「提案資料」「鳴海さん向け資料」「事業の現状共有スライド」など、Domuz 社内・社外向けのスライドやプレゼン資料を新規に作る・作り直す・直す依頼では、形式（HTML/PDF/スライド）の指定がなくても必ずこのスキルを使う。既存の deck（build_deck.py があるフォルダ）の修正にも使う。Google スライドや PowerPoint のファイル自体を編集する依頼、メールや文書の作成には使わない。
---

# domuz-deck — Domuz デザインの発表スライド（HTML + PDF）

Domuz の資料は、デザインシステム v2.1「発表スライド」型（4:3・1128×846px、Moss #004347 と Light #00D79C、Outfit + Zen Kaku Gothic New）で統一している。
このスキルは、その見た目を Python のライブラリ（`assets/domuz_deck.py`）と手順にしたもの。内容を Python で書き、HTML を生成し、同じ HTML を Playwright で PDF にする。

成果物は毎回この3つ: `deck.html`（画像埋め込みの1ファイル）、`deck.pdf`（1スライド1ページ）、`notes.md`（発表者ノート・出典）。

## 進め方

### 1. 中身を確定する（デザインの前に）
- 元資料があるときは、文言と数値をそのまま使う。変えるのは見た目と構成だけ。言い換えや数字の追加は依頼されたときだけ行い、変えた箇所は最後に報告する。
- Keynote（.key）は zip。`Index/Slide-*.iwa` を snappy で展開すると本文テキストが取れる（`iwa_text.py` は `references/keynote_extract.md` 参照）。表はセル順の復元が要るので注意。
- スライド順と章立てを決める。3章以上なら章扉（divider）を入れる。1スライド1メッセージ。詰め込みすぎたら分ける。
- 写真・図・ロゴなど、元資料に無い素材が要るときは、Google Drive / Slack を検索してから（見つからなければ）ユーザーに送ってもらう。見つかるまではその箇所を破線の枠「（届き次第差し替え）」にして先に進める。

### 2. 作業フォルダを作る
```
<deck-name>/
├── build_deck.py      # 内容。このスキルの examples/example_build.py を写して始める
├── domuz_deck.py      # assets/domuz_deck.py をコピー（デッキごとに同梱して、後から単独で再生成できるようにする）
├── render_pdf.js      # scripts/ からコピー
├── screenshots.js     # scripts/ からコピー
├── images/            # 写真・図面・アイコン（必要なものだけ）
├── deck.html / deck.pdf / notes.md   # 生成物
```
フォルダ名は `<内容>-<YYYY-MM-DD>`（例: `enabler-3pl-mtg-2026-10-15`）。リポジトリで管理しているなら生成物も一緒にコミットする（ユーザーが受け取る物なので）。

### 3. build_deck.py を書く
`from domuz_deck import Deck` して、`examples/example_build.py` の形で1枚ずつ組む。部品の選び方と値の根拠は `references/design_system.md`。要点:
- `d.cover()` → アジェンダ `d.nlist()` → 章扉 `d.divider()` → 内容 `d.slide()` … の順。
- 本文は `.body`（top 160px, 幅 1016px）の中に書く。絶対配置の部品（hbar, vbars）は高さを持った `.body` に入れる。
- 強調は `[[語]]` だけ。色を増やさない。番号・結論はライトグリーン、比較対象は灰色。
- 表は8行まで、1列目は折り返さない（`white-space:nowrap`）。
- 数字の構造（価格の内訳など）は `d.hbar()` を同じ scale で縦に並べる。例: 上段「セット全体」、中段「花の内訳」、下段「送料」、最後に式。
- フロー図はアイコン版（`d.icons()`, `d.node()`, `d.tag()`, `d.arrow()`, `d.svg()`）。横矢印のタグは矢印の上に置く。
- 出典・補足は `notes=` に。スライド上の注記は `foot=` に1行。

### 4. 生成して目で確認する（必ず）
```bash
python3 build_deck.py
NODE_PATH=$(npm root -g) node screenshots.js deck.html shots/   # 1枚ずつ PNG
```
PNG を 2×2 や 3×2 の一覧にして見る。見るポイント:
- サブタイトルと本文の重なり、下の脚注・ページ番号へのはみ出し（はみ出したら分割か縮小）。
- 棒・タグ・ラベルの重なり、表の折り返し、`[[ ]]` の変換漏れ。
- 空白が大きすぎるスライド（部品を大きくするか、情報を足す）。
直して再生成、を一覧がきれいになるまで繰り返す。

### 5. PDF を出す
```bash
NODE_PATH=$(npm root -g) node render_pdf.js deck.html deck.pdf
python3 scripts/check_fonts.py deck.pdf    # Outfit / Zen Kaku 以外が出ていないか
```
Google Fonts をネットから読むので、オフラインではフォントが代替になる。丸数字（①②③）や全角スペースは代替フォントに落ちるので使わない（`.circ` を使う）。

### 6. 渡す
`deck.pdf` と `deck.html` をユーザーに送る（SendUserFile 等）。リポジトリなら commit & push。
報告には「反映した点」「元資料から変えた点（言い換え・追加した数字）」「確認してほしい点（概算で置いた位置、仮の数値、未着の素材）」を分けて書く。

## よくある修正依頼と対応
- 「もっと見やすく」: 文字を小さくするのではなく、図を大きくして説明を下に移す。1列 320px × 3 まで。
- 「図面を使って」: 画像を 740px 幅で左、右に凡例（Moss / Light / Flower の半透明矩形）。
- 「具体例を見せたい」: スクリーンショットは必要部分だけ切り出して 1px 枠。横に EXAMPLE ラベル＋2〜3行の説明。
- 「画像も入れたい」が素材未着: 破線の枠で場所を確保し、届いたら差し替える。
- 「数字の構造が分かるように」: 上代→下代→原価/作業費/利益 を同じ目盛りの hbar で段階的に。

## ファイル
- `assets/domuz_deck.py` — ライブラリ本体（トークン・CSS・Deck クラス）。コピーして使う。
- `assets/icons/` — 線画アイコン（box / warehouse / bouquet / person × Moss・白・灰）。
- `scripts/render_pdf.js`, `scripts/screenshots.js` — Playwright（Chromium）で PDF と確認用 PNG。
- `scripts/trim_icon.py` — 新しい線画アイコンを3色の透過 PNG にする。
- `scripts/check_fonts.py` — PDF の埋め込みフォント確認。
- `examples/example_build.py` — 全スライド型の見本。`examples/deck.pdf` が出力例。
- `references/design_system.md` — 色・文字・余白・部品の使い分け・文言ルール。
- `references/keynote_extract.md` — Keynote からテキストと表を取り出す方法。
