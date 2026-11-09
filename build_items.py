#!/usr/bin/env python3
"""モノの記録から items.json を書き出す。パーソナルデータベースの三大分類のひとつ。

持っているもの（ROWS）・お気に入りのもの（PICKS）・欲しいもの（WANTS）の三レーン。
事実と評価を分けてあるのがこの形の肝で、持っていることは ROWS に一度だけ書き、
気に入っている理由は PICKS に別で持つ。PICKS に載せた分だけ picks.html に出る。

★このファイルは公開リポジトリに入り、誰でも全文を読める。非公開という状態は
持たない方針なので、公開していいものだけを書く。見せたくないものはここに書かない。
買った値段や型番の細かいところも、書く必要がなければ書かない。
ときめかなくなったら消す。

直し方は二通り。手元で直して python3 build_items.py を走らせるか、GitHub の編集画面で
このファイルだけを直してコミットするか。後者の場合は .github/workflows/build.yml が
代わりに走らせて items.json を作り直すので、手元のパソコンは要らない。どちらの場合も、
手元で続きを直すときは先に git pull しておく（向こうのコミットが増えているため）。

写真は images/<slug>.jpg に置く（images/README.md と add_images.py）。slug が鍵なので、
一度決めた slug は変えない。リンクは公式の商品ページで、実際に開いて確かめたものだけ書く。
"""

import hashlib
import json
import re
from pathlib import Path

NOTE = ("モノ（持っているもの・お気に入りのもの・欲しいもの）。"
        "build_items.py が書き出す。直すのはあちら。")

# 持っているもの。区切りは | で、順番は
# slug | 題名 | 年 | 一行 | リンク | 元になった記録
# 年は使い始めた年。まだどれも分からないので空にしてある（一件も無いので年別の節は出ない）。
# 一行は「それが何か」の説明。気に入っている理由は PICKS の側に書く。
ROWS = """
washer|ドラム式洗濯機||||
blender|ブレンダー||||
hotcook|SHARP KN-HW10E-B|||https://jp.sharp/hotcook/products/knhw10e/|
simmons-mattress|シモンズのマットレス（シングル）|||https://www.simmons.co.jp/|
donabe|ご飯を炊く土鍋||||
gelato-pique-pajamas|ジェラートピケのパジャマ|||https://gelatopique.com/|
united-tokyo|UNITED TOKYO の服|||https://united-tokyo.com/|
suit-shirt|動きやすいスーツとシャツ||||
running-shoes|歩きやすいランニングシューズ||||
waterman|ウォーターマンのボールペン|||https://www.waterman.com/|
iphone|iPhone|||https://www.apple.com/jp/iphone/|
mac|Mac|||https://www.apple.com/jp/mac/|
logicool-mouse|ロジクールのマウス|||https://www.logicool.co.jp/ja-jp/shop/c/mice|
airpods-4|AirPods 4|||https://www.apple.com/jp/airpods/|
fitbit-air|Google Fitbit Air|||https://store.google.com/jp/category/watches_trackers?hl=ja|
chatgpt|ChatGPT|||https://chatgpt.com/|
claude|Claude|||https://claude.com/|
google-ai-pro|Google AI Pro|||https://one.google.com/about/google-ai-plans/|
youtube-premium|YouTube Premium|||https://www.youtube.com/premium|
netflix|Netflix|||https://www.netflix.com/jp/|
u-next|U-NEXT|||https://video.unext.jp/|
prime-music|Amazon Prime Music|||https://www.amazon.co.jp/music/prime|
money-forward|Money Forward|||https://moneyforward.com/|
trangia-mestin|トランギア メスティン|||https://trangia.se/en/product-category/mess-tins/|
nemo-atom-2p|ニーモ アトム 2P|||https://nemoequipment.jp/collections/tent-and-shelters-tents|
stellaridge-1|モンベル ステラリッジ テント1|||https://webshop.montbell.jp/goods/disp_fo.php?product_id=1122648|
downhugger-800|モンベル アルパイン ダウンハガー 800 #1||||
field-hopper|ソト フィールドホッパー|||https://soto.shinfuji.co.jp/products/st-630/|
ricoh-gr3|RICOH GR III|||https://www.ricoh-imaging.co.jp/japan/products/gr-3/|
shoebill-figure|ハシビロコウのフィギュア||||
shoebill-cup|ハシビロコウのコップ||||
koami-frog|小網神社のカエルのお守り|||https://www.koamijinja.or.jp/|
danboard|ダンボーのフィギュア||||
rutile-quartz|ルチルの水晶玉||||
"""

# お気に入りのもの。ここに載せた分だけ picks.html に出る。
# 文は前の items.json にあったものをそのまま移した（書き換えていない）。
PICKS = {
    "washer": "洗って乾かすまでが一度で終わる。干す工程が消えた。",
    "blender": "準備と片付けが軽いので、使う回数が落ちない。",
    "hotcook": "自動調理鍋。材料を入れて放っておける。ここも手間を引き受けてくれる側。",
    "simmons-mattress": "いちばん気に入っている家具。シングルなので、もう少し大きいものに替えたい。",
    "donabe": "炊飯器ではなく土鍋で炊く。",
    "gelato-pique-pajamas": "着ると調子がいい。肌ざわりで選んでいる。",
    "united-tokyo": "肌触りのよさで選んだもの。",
    "suit-shirt": "きちんと見えることと、体が楽であることの両立。",
    "running-shoes": "よく歩くので、靴は履き心地から選ぶ。",
    "waterman": "いま使っているペン。",
    "logicool-mouse": "手に合っている。毎日触るものほど差が出る。",
    "airpods-4": "歩きながら聴く、話す。散歩とAIとの対話が習慣なので効く。",
    "fitbit-air": "身につけるものだが、役割は体の状態を見ること。",
    "youtube-premium": "よく観ている。",
    "netflix": "よく観ている。",
    "u-next": "契約しているが、観る習慣になっていない。",
    "prime-music": "探さずに流せる。部屋で過ごす時間の背景として。",
    "money-forward": "資産を一か所で可視化する。見続けないようにしている。",
    "trangia-mestin": "キャンプ用の飯ごう。",
    "nemo-atom-2p": "テント。",
    "stellaridge-1": "テント。",
    "downhugger-800": "寝袋。",
    "field-hopper": "折りたたみのテーブル。",
    "ricoh-gr3": "カメラ。",
}

# 欲しいもの。区切りは | で、順番は
# slug | 題名 | 一行 | メモ | 領域 | 細目 | 状態 | リンク | 元になった記録
# 領域は下の USES の領域名から選ぶ（違う語はビルドで止まる）。細目は自由語でよい。
# 状態に「いま」と書くと、want.html の先頭の節に入る。空なら「これから」。
WANTS = """
dual-monitor|デュアルモニタ|PCの画面を2枚に|広く見渡しながら、考えたり作ったりしたい。|デジタルツール|モニタ|||
smart-glasses|スマートグラス||目の前の景色に、情報や記録が重なる体験をしてみたい。|デジタルツール|身につけるもの|||
"""

# 領域と細目。字下げの無い行が領域で 領域名|英字|アイコン|参照先、
# 字下げした行が細目で 細目名|slug,slug。同じものは一つの細目にだけ置く。
# アイコンは各HTMLに埋め込んである線画の名前。参照先は無ければ空。
USES = """
家電|APPLIANCES|washer|
  洗濯|washer
  調理|blender,hotcook
家具|FURNITURE|bed|
  寝具|simmons-mattress
食器|TABLEWARE|bowl|
  炊く|donabe
服|APPAREL|shirt|
  部屋着|gelato-pique-pajamas
  ふだん着|united-tokyo
  きちんとした服|suit-shirt
  靴|running-shoes
文房具|STATIONERY|pen|
  ペン|waterman
デジタルツール|DIGITAL|laptop|
  パソコンとスマホ|iphone,mac
  入力機器|logicool-mouse
  音|airpods-4
  身につけるもの|fitbit-air
サービス|SERVICES|sparkle|
  AI|chatgpt,claude,google-ai-pro
  動画|youtube-premium,netflix,u-next
  音楽|prime-music
  おかね|money-forward
趣味用品|HOBBY|tent|
  キャンプ道具|trangia-mestin,nemo-atom-2p,stellaridge-1,downhugger-800,field-hopper
  カメラ|ricoh-gr3
可愛いもの|CUTE|bird|
  ハシビロコウ|shoebill-figure,shoebill-cup
  お守りと置物|koami-frog,danboard,rutile-quartz
"""

# 領域に入れないもの。いまは無い。
OUT = """
"""

# 領域に出していないものについての一行。出していないものが無ければ空。
LEFT = ""

ASSETS = ["style.css", "app.js"]
PAGES = ["index.html", "picks.html", "want.html"]
SLUG = re.compile(r"^[a-z0-9-]+$")
YEAR = re.compile(r"^[12][0-9]{3}$")
# app.js が領域の外のものと「いま」の節に使うアイコン。どのページにも要る。
ALWAYS = ["star", "sparkle"]


def rows(block, cols):
    """| 区切りの表を読む。列の数が合わない行はその場で止める。"""
    out = []
    for n, line in enumerate(block.strip().splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != len(cols):
            raise SystemExit(f"{n}行目の列が{len(parts)}個（{len(cols)}個のはず）: {line}")
        out.append(dict(zip(cols, parts)))
    return out


def check_common(it, where):
    """slug・年・リンクの書き方を確かめる。どれも直せば通る形の間違い。"""
    if not SLUG.match(it["slug"]):
        raise SystemExit(f"{where} の slug は英小文字・数字・ハイフンだけ: {it['slug']}")
    if it.get("year") and not YEAR.match(it["year"]):
        raise SystemExit(f"{where} の年は4桁: {it['slug']} の {it['year']}")
    if it.get("url") and not it["url"].startswith(("http://", "https://")):
        raise SystemExit(f"{where} のリンクは http/https だけ: {it['slug']}")
    if it.get("source") and not it["source"].startswith(("./", "../")):
        raise SystemExit(f"{where} の元になった記録は相対パスで: {it['slug']} の {it['source']}")


def check_icons(here, names):
    """使うアイコンが三枚ぜんぶに埋まっているか確かめる。

    優待で一度やられている。want.html にアイコンを三つしか持たせないまま銘柄を足して、
    カードの丸が空のまま公開された。線画は各HTMLに埋め込む作りなので、
    一枚だけ足し忘れても他の二枚では正しく出てしまい、見落としやすい。
    """
    for page in PAGES:
        have = set(re.findall(r'<symbol id="ic-([a-z0-9-]+)"', (here / page).read_text(encoding="utf-8")))
        missing = sorted(set(names) - have)
        if missing:
            raise SystemExit(f"{page} にアイコンが埋まっていない: {missing}")


def stamp_assets(here):
    """style.css と app.js の URL に中身のハッシュを付ける。

    一度来た人のブラウザには前の app.js が残っている。ページとデータだけ新しくなると
    古いコードが新しい形の items.json を読むことになり、節がまるごと出なくなる。
    中身が変わればURLも変わるようにして、取り違えが起きないようにする。
    """
    tag = hashlib.sha256(b"".join((here / f).read_bytes() for f in ASSETS)).hexdigest()[:8]
    touched = []
    for page in here.glob("*.html"):
        t = u = page.read_text(encoding="utf-8")
        for f in ASSETS:
            u = re.sub(rf'({re.escape(f)})(\?v=[0-9a-f]+)?"', rf'\1?v={tag}"', u)
        if u != t:
            page.write_text(u, encoding="utf-8")
            touched.append(page.name)
    return f"共通ファイルの版を {tag} にした" + (f"（{'・'.join(touched)}）" if touched else "（変更なし）")


def main():
    items = rows(ROWS, ["slug", "title", "year", "note", "url", "source"])
    wants = rows(WANTS, ["slug", "title", "note", "memo", "use", "sub", "state", "url", "source"])

    for it in items:
        check_common(it, "ROWS")
    for w in wants:
        check_common(w, "WANTS")

    slugs = [i["slug"] for i in items] + [w["slug"] for w in wants]
    dup = sorted({s for s in slugs if slugs.count(s) > 1})
    if dup:
        raise SystemExit(f"slug が重なっている: {dup}")

    by_slug = {i["slug"]: i for i in items}
    unknown = sorted(set(PICKS) - set(by_slug))
    if unknown:
        raise SystemExit(f"PICKS に ROWS に無い slug がある: {unknown}")
    for slug, memo in PICKS.items():
        by_slug[slug]["memo"] = memo

    # 領域と細目。字下げの無い行が領域、字下げした行が細目。
    uses, seen = [], []
    for line in USES.strip().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  "):
            if not uses:
                raise SystemExit(f"領域より先に細目が来ている: {line.strip()}")
            sub, codes = line.strip().split("|")
            codes = [c.strip() for c in codes.split(",") if c.strip()]
            uses[-1]["subs"].append(sub)
            uses[-1]["n"] += len(codes)
            seen += codes
            for c in codes:
                if c in by_slug:
                    by_slug[c]["use"], by_slug[c]["sub"] = uses[-1]["name"], sub
        else:
            name, en, ic, ref = line.split("|")
            uses.append({"name": name, "en": en, "icon": ic, "ref": ref, "subs": [], "n": 0})

    dup = sorted({c for c in seen if seen.count(c) > 1})
    if dup:
        raise SystemExit(f"USES で二つの細目に置かれた slug がある: {dup}")

    ghost = sorted(c for c in seen if c not in by_slug)
    if ghost:
        raise SystemExit(f"USES に ROWS に無い slug がある: {ghost}")

    out_slugs = [c.strip() for c in OUT.replace("\n", "").split(",") if c.strip()]
    stray = sorted(c for c in out_slugs if c not in by_slug)
    if stray:
        raise SystemExit(f"OUT に ROWS に無い slug がある: {stray}")

    # 行を足したときの入れ忘れを防ぐ。どこかの領域に置くか、出さないと決めるか。
    nowhere = sorted(c for c in by_slug if c not in seen and c not in out_slugs)
    if nowhere:
        raise SystemExit(f"USES にも OUT にも無い slug がある: {nowhere}")

    names = {u["name"] for u in uses}
    bad = sorted({w["use"] for w in wants if w["use"] and w["use"] not in names})
    if bad:
        raise SystemExit(f"WANTS の領域が領域名に無い: {bad}")
    bad = sorted({w["state"] for w in wants if w["state"] not in ("", "いま")})
    if bad:
        raise SystemExit(f"WANTS の状態は空か「いま」だけ: {bad}")

    here = Path(__file__).resolve().parent
    check_icons(here, [u["icon"] for u in uses] + ALWAYS)

    # 写真は images/<slug>.jpg に置いてあれば拾う。items.json は生成物なので、
    # 写真があるかどうかはファイルの側で決める（誰も items.json に書き戻さない）。
    for it in items + wants:
        if (here / "images" / (it["slug"] + ".jpg")).exists():
            it["img"] = f"images/{it['slug']}.jpg"

    data = {
        "note": NOTE,
        "items": [{k: v for k, v in i.items() if v} for i in items],
        "wants": [{k: v for k, v in w.items() if v} for w in wants],
        "uses": uses,
        "left": LEFT,
    }
    (here / "items.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"items.json を書いた（{len(items)}件・お気に入り{len(PICKS)}件・これから{len(wants)}件）")
    print(stamp_assets(here))


if __name__ == "__main__":
    main()
