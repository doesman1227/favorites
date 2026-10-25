#!/usr/bin/env python3
"""images/_inbox/ に置いた写真を、正方形に整えて images/ へ入れ、items.json に反映する。

使い方:
    1. 写真を images/_inbox/<slug>.jpg（または .png / .heic など）に置く
       slug は items.json の各項目の "slug"。`python3 add_images.py --list` で一覧が出る。
    2. python3 add_images.py
    3. 取り込んだ写真は images/<slug>.jpg になり、items.json の img が設定される。

macOS の sips だけを使う（追加インストール不要）。
"""
import json, os, re, subprocess, sys, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ITEMS = os.path.join(HERE, "items.json")
IMAGES = os.path.join(HERE, "images")
INBOX = os.path.join(IMAGES, "_inbox")
SIZE = 1000
EXTS = (".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".tif", ".tiff")


def load():
    with open(ITEMS, encoding="utf-8") as fh:
        return json.load(fh)


def all_items(d):
    for key, v in d.items():
        if key == "note":
            continue
        for it in v:
            yield key, it


def sips(*args):
    r = subprocess.run(["sips", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or r.stdout.strip())
    return r.stdout


def dimensions(path):
    out = sips("-g", "pixelWidth", "-g", "pixelHeight", path)
    w = int(re.search(r"pixelWidth:\s*(\d+)", out).group(1))
    h = int(re.search(r"pixelHeight:\s*(\d+)", out).group(1))
    return w, h


def normalize(src, dst):
    """短辺を SIZE に合わせてから中央を正方形で切り抜き、jpeg で書き出す。"""
    tmp = dst + ".tmp.jpg"
    shutil.copy2(src, tmp)
    sips("-s", "format", "jpeg", tmp, "--out", tmp)
    w, h = dimensions(tmp)
    if w < h:
        sips("--resampleWidth", str(SIZE), tmp)
    else:
        sips("--resampleHeight", str(SIZE), tmp)
    sips("-c", str(SIZE), str(SIZE), tmp)          # 中央を正方形に切り抜く
    sips("-s", "formatOptions", "82", tmp)          # 画質
    os.replace(tmp, dst)


def main():
    d = load()
    by_slug = {it.get("slug"): (key, it) for key, it in all_items(d) if it.get("slug")}

    if "--list" in sys.argv:
        for key, it in all_items(d):
            mark = "済" if it.get("img") else "  "
            print(f"  {mark} {it.get('slug',''):22s} {key:11s} {it['title']}")
        print(f"\n  写真あり {sum(1 for _, it in all_items(d) if it.get('img'))} / "
              f"{sum(1 for _ in all_items(d))} 件")
        print(f"  置き場所: {INBOX}/<slug>.jpg")
        return

    os.makedirs(INBOX, exist_ok=True)
    files = sorted(f for f in os.listdir(INBOX) if f.lower().endswith(EXTS))
    if not files:
        print(f"{INBOX} に写真がありません。<slug>.jpg の名前で置いてください。")
        print("slug の一覧は python3 add_images.py --list で出ます。")
        return

    done, unknown = [], []
    for f in files:
        slug = os.path.splitext(f)[0]
        if slug not in by_slug:
            unknown.append(f)
            continue
        dst = os.path.join(IMAGES, slug + ".jpg")
        normalize(os.path.join(INBOX, f), dst)
        by_slug[slug][1]["img"] = f"images/{slug}.jpg"
        os.remove(os.path.join(INBOX, f))
        done.append(slug)

    with open(ITEMS, "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    for s in done:
        print(f"  取り込み: images/{s}.jpg  ({by_slug[s][1]['title']})")
    for f in unknown:
        print(f"  ★ slug が一致しません: {f}  → --list で確認してください")
    print(f"\n取り込み {len(done)} 件 / 残り {len(unknown)} 件")
    if done:
        print("確認したら git add -A && git commit && git push で公開されます。")


if __name__ == "__main__":
    main()
