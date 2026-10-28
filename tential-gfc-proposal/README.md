# TENTIAL × GFC 提案資料 4ページ目（株式会社Domuzについて）

giftee 社の提案資料（V1）の4ページ目に差し込む Domuz 紹介ページ。4ページ目のみ。

- `Domuz_intro_p4.pdf` … 完成版（1ページ）。元PDFの4ページ目にレイヤーを重ねたもの
- `Domuz_intro_p4.pptx` … 編集用（1枚）。文字は Yu Gothic のテキストボックス、リボンとアスタリスクは元ページからの切り出し画像
- `page4-preview.png` … PDF のプレビュー
- `page4-src/` … 本文レイヤーの HTML、Chromium で PDF 化するスクリプト、PPTX を組むスクリプト

## 再生成

```sh
cd page4-src
# フォント: Noto Sans JP（可変フォント）を同じフォルダに置く（PDF 用）
# https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/Variable/TTF/Subset/NotoSansJP-VF.ttf
node render.js                       # → overlay.pdf（元PDF 4ページ目に pypdf の merge_page で重ねる）
python3 build_pptx.py <元PDF4ページ目の300dpi PNG> ../Domuz_intro_p4.pptx
```

## P10 の次に差し込むページ（先行施策｜プリザーブドフラワーの卸販売）

- `Domuz_preserved_p11.pptx` … 編集用（1枚）。ページ番号は「11」で入れてあるので、差し込み位置に合わせて直す
- `p11-preview.png` … LibreOffice でのプレビュー（游ゴシック非搭載環境のため字間は実機と少し異なる）
- `p11-src/build_p11.py` … 組み立てスクリプト。商品写真は料金表 PDF から切り出した JPEG

```sh
cd p11-src
python3 build_p11.py <元資料の任意ページの300dpi PNG> ../Domuz_preserved_p11.pptx 11
```
