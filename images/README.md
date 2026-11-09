# モノの写真

写真は `images/<slug>.jpg` に置けば出る。`slug` は `build_items.py` の
`ROWS` / `WANTS` の一列目。**`items.json` は `build_items.py` の生成物なので、
写真の有無はファイルの側で決まる**（`img` を手で書く必要はないし、書いても消える）。

2026-11-09 より前は管理パネル（`http://localhost:8787/favorites`）から編集できたが、
いまは `build_items.py` が正典になったので、その画面は案内だけになっている。

## 置き方

1. 写真を `images/_inbox/<slug>.jpg` に置く
   - 拡張子は `.jpg` `.png` `.heic` `.webp` などそのままでよい（iPhone の HEIC も可）
2. 取り込む

```bash
cd ~/Claude/favorites && python3 add_images.py
```

3. 短辺を 1000px に合わせて中央を正方形に切り抜き、`images/<slug>.jpg` になる
4. `items.json` に反映する

```bash
cd ~/Claude/favorites && python3 build_items.py
```

5. 確認して `git add -A && git commit && git push`

slug の一覧と、写真が入っているかの確認:

```bash
cd ~/Claude/favorites && python3 add_images.py --list
```

写真を外したいときは `images/<slug>.jpg` を消して `python3 build_items.py` を走らせる。

## 決めごと

- **非公開という状態は持たない。** `items.json` は公開リポジトリに入り、
  `https://m-note.uk/favorites/items.json` で誰でも全文を読める。
  表示上だけ隠す仕組みは「隠したつもりで隠れていない」状態になるので作らない。
  **公開していいものだけを書く。** 人に見せたくないものは、そもそもここに書かない
  （書くなら vault など私的な場所へ）
- **自分で撮った写真だけを置く。** 製品写真やメーカーのサイトの画像、他人の写真は
  公開サイトに載せない（著作権）
- 正方形に切り抜かれるので、**真ん中に主役が来るように**撮っておくと扱いやすい
- 写真が無いものは領域のアイコンが出る。**一枚ずつ増やしていけて、
  途中でも見た目が崩れない**
- サービス（ChatGPT、Netflix など）はロゴになってしまうので、無理に入れなくてよい。
  他社のロゴを載せるのは避ける
- 撮影が難しい場所（ジムの浴室など）も、無理に入れない

## 写真がないとき

写真は必須ではない。**リンクとひとことだけで登録してよい。**
`build_items.py` の `ROWS` に一行足すだけで出る。

```
donabe|ご飯を炊く土鍋||||
```

`url` の列（五列目）を書くと、カードの名前がその外部リンクになる（http / https のみ）。
気に入っている理由は `PICKS` の側に一行書くと、お気に入りのページに出る。

写真を撮る手間で登録が止まるより、まず名前だけ入れておいて、
撮れたときに `_inbox` へ置くほうが続く。
