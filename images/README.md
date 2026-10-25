# お気に入りの写真

## 置き方

1. 写真を `images/_inbox/<slug>.jpg` に置く
   - `slug` は `items.json` の各項目に入っている。一覧は下のコマンドで出る
   - 拡張子は `.jpg` `.png` `.heic` `.webp` などそのままでよい（iPhone の HEIC も可）
2. 取り込む

```bash
cd ~/Claude/favorites && python3 add_images.py
```

3. 短辺を 1000px に合わせて中央を正方形に切り抜き、`images/<slug>.jpg` になる。
   `items.json` の `img` も自動で設定される
4. 確認して `git add -A && git commit && git push`

slug の一覧と、写真が入っているかの確認:

```bash
cd ~/Claude/favorites && python3 add_images.py --list
```

## 決めごと

- **自分で撮った写真だけを置く。** 製品写真やメーカーのサイトの画像、他人の写真は
  公開サイトに載せない（著作権）。フッターにも「写真は自分で撮ったものだけ」と書いてある
- 正方形に切り抜かれるので、**真ん中に主役が来るように**撮っておくと扱いやすい
- 写真が無い項目は、頭文字のプレースホルダーが出る。**一枚ずつ増やしていけて、
  途中でも見た目が崩れない**
- サービス（ChatGPT、Netflix など）はロゴになってしまうので、無理に入れなくてよい。
  他社のロゴを載せるのは避ける
- 撮影が難しい場所（ジムの浴室など）も、無理に入れない

## 手で書く場合

スクリプトを使わず、自分で正方形の画像を用意して `images/` に置き、
`items.json` に直接書いてもよい。

```json
{ "title": "RICOH GR III", "memo": "カメラ。", "slug": "ricoh-gr3", "img": "images/ricoh-gr3.jpg" }
```
