# TENTIAL × GFC 提案資料 4ページ目（株式会社Domuzについて）

- `TENTIAL_GFC_proposal_V1_p4-Domuz.pdf` … giftee 社の提案資料（V1）の4ページ目に Domuz 紹介を差し込んだ完成版
- `page4-preview.png` … 4ページ目のプレビュー
- `page4-src/` … 4ページ目の本文レイヤー（HTML）と Chromium で PDF 化するスクリプト

## 再生成

```sh
cd page4-src
# フォント: Noto Sans JP（可変フォント）を同じフォルダに置く
# https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/Variable/TTF/Subset/NotoSansJP-VF.ttf
node render.js            # → overlay.pdf
# 元PDFの4ページ目に overlay.pdf を pypdf の merge_page で重ねる
```
