# diary/_build.py — 開発日誌の静的生成（多言語拡張前提の最小構成）
#
# 使い方:  python _build.py   （diary/ ディレクトリ内で実行）
#
# 仕組み:
#   _src/<locale>/<num>.txt  →  <locale>/<num>.html  ＋  <locale>/index.html
#   ルートの index.html は主言語(ja)の一覧をそのまま出す。
#   英語版を足す時は _src/en/001.txt を置いて再実行するだけ。
#   同じ番号のファイルが複数言語にあれば hreflang で相互リンクされる。
#
# 原稿の形式（マークダウン不使用・素のテキスト）:
#   1行目  title: 記事の題
#   2行目  date: YYYY-MM-DD
#   以降    空行区切りの段落

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent
SRC = ROOT / "_src"
SITE = "https://sakuradevjp.github.io/diary"

PRIMARY = "ja"  # 日誌の主言語（本人の声）。LPと違い日本語が正
LOCALE_META = {
    "ja": {"lang": "ja", "site_title": "作りながら考えたこと", "site_sub": "sakuradev の開発日誌", "back": "目次へ", "home": "sakuradev", "ep": "第{n}話"},
    "en": {"lang": "en", "site_title": "Notes While Building", "site_sub": "a dev diary by sakuradev", "back": "All episodes", "home": "sakuradev", "ep": "Episode {n}"},
}

STYLE = """
:root { --fg:#2a2a2a; --bg:#fdfcfa; --sub:#8a8a8a; --line:#e8e4de; --link:#a0525f; }
@media (prefers-color-scheme: dark) {
  :root { --fg:#d8d4ce; --bg:#17181a; --sub:#7a7a7a; --line:#2c2e31; --link:#c98a95; }
}
* { margin:0; padding:0; box-sizing:border-box; }
body { background:var(--bg); color:var(--fg); font-family:"Hiragino Sans","Yu Gothic",Meiryo,sans-serif;
       line-height:2.0; font-size:16px; }
main { max-width:38em; margin:0 auto; padding:3.5em 1.4em 5em; }
header.site { margin-bottom:3em; }
header.site h1 { font-size:1.05em; font-weight:600; letter-spacing:.04em; }
header.site p  { font-size:.8em; color:var(--sub); margin-top:.3em; }
header.site a  { color:inherit; text-decoration:none; }
article .ep { font-size:.78em; color:var(--sub); letter-spacing:.06em; margin-bottom:.3em; }
article h2 { font-size:1.15em; font-weight:600; margin-bottom:.2em; letter-spacing:.02em; }
article time { font-size:.78em; color:var(--sub); display:block; margin-bottom:2.2em; }
ul.entries .ep { color:var(--sub); font-size:.85em; margin-right:.9em; white-space:nowrap; }
article p { margin-bottom:1.6em; }
ul.entries { list-style:none; }
ul.entries li { border-bottom:1px solid var(--line); }
ul.entries a { display:flex; justify-content:space-between; gap:1em; padding:1em .1em;
               color:inherit; text-decoration:none; }
ul.entries a:hover { color:var(--link); }
ul.entries time { color:var(--sub); font-size:.8em; white-space:nowrap; align-self:center; }
nav.foot { margin-top:4em; font-size:.85em; }
nav.foot a { color:var(--sub); text-decoration:none; margin-right:1.6em; }
nav.foot a:hover { color:var(--link); }
"""


def parse(path):
    lines = path.read_text(encoding="utf-8").strip().split("\n")
    meta = {}
    body_start = 0
    for i, line in enumerate(lines):
        if ":" in line and line.split(":", 1)[0] in ("title", "date"):
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
            body_start = i + 1
        else:
            break
    paras = [p.strip() for p in "\n".join(lines[body_start:]).split("\n\n") if p.strip()]
    return meta, paras


def hreflang_links(num, locales):
    if len(locales) < 2:
        return ""
    tags = []
    for loc in sorted(locales):
        tags.append(f'<link rel="alternate" hreflang="{loc}" href="{SITE}/{loc}/{num}.html">')
    tags.append(f'<link rel="alternate" hreflang="x-default" href="{SITE}/{PRIMARY}/{num}.html">')
    return "\n".join(tags)


def page(locale, num, meta, paras, locales_for_num):
    m = LOCALE_META[locale]
    body = "\n".join(f"<p>{p}</p>" for p in paras)
    return f"""<!DOCTYPE html>
<html lang="{m['lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{meta['title']} — {m['site_title']}</title>
<link rel="canonical" href="{SITE}/{locale}/{num}.html">
{hreflang_links(num, locales_for_num)}
<link rel="icon" type="image/png" href="../../avatar.png">
<style>{STYLE}</style>
</head>
<body>
<main>
<header class="site"><h1><a href="index.html">{m['site_title']}</a></h1><p>{m['site_sub']}</p></header>
<article>
<div class="ep">{m['ep'].format(n=int(num))}</div>
<h2>{meta['title']}</h2>
<time datetime="{meta['date']}">{meta['date']}</time>
{body}
</article>
<nav class="foot"><a href="index.html">{m['back']}</a><a href="https://sakuradevjp.github.io/">{m['home']}</a></nav>
</main>
</body>
</html>
"""


def index(locale, entries):
    m = LOCALE_META[locale]
    items = "\n".join(
        f'<li><a href="{num}.html"><span><span class="ep">{m["ep"].format(n=int(num))}</span>{meta["title"]}</span><time>{meta["date"]}</time></a></li>'
        for num, meta in sorted(entries.items(), reverse=True)
    )
    return f"""<!DOCTYPE html>
<html lang="{m['lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{m['site_title']} — {m['site_sub']}</title>
<link rel="canonical" href="{SITE}/{locale}/">
<link rel="icon" type="image/png" href="../../avatar.png">
<style>{STYLE}</style>
</head>
<body>
<main>
<header class="site"><h1>{m['site_title']}</h1><p>{m['site_sub']}</p></header>
<ul class="entries">
{items}
</ul>
<nav class="foot"><a href="https://sakuradevjp.github.io/">{m['home']}</a></nav>
</main>
</body>
</html>
"""


def main():
    all_entries = {}  # locale -> {num: meta}
    num_locales = {}  # num -> set(locales)
    for loc_dir in sorted(SRC.iterdir()):
        if not loc_dir.is_dir():
            continue
        loc = loc_dir.name
        for f in sorted(loc_dir.glob("*.txt")):
            num = f.stem
            meta, _ = parse(f)
            all_entries.setdefault(loc, {})[num] = meta
            num_locales.setdefault(num, set()).add(loc)

    for loc, entries in all_entries.items():
        out_dir = ROOT / loc
        out_dir.mkdir(exist_ok=True)
        for num in entries:
            meta, paras = parse(SRC / loc / f"{num}.txt")
            (out_dir / f"{num}.html").write_text(
                page(loc, num, meta, paras, num_locales[num]), encoding="utf-8")
        (out_dir / "index.html").write_text(index(loc, entries), encoding="utf-8")
        print(f"{loc}: {len(entries)} entries")

    # ルート index は主言語の一覧をそのまま（将来 en が育ったら言語選択に差し替え可）
    primary_entries = all_entries.get(PRIMARY, {})
    root_html = index(PRIMARY, primary_entries).replace(
        f'href="{SITE}/{PRIMARY}/"', f'href="{SITE}/"').replace(
        '<a href="index.html"', f'<a href="{PRIMARY}/index.html"').replace(
        'href="../../avatar.png"', 'href="../avatar.png"')
    for num in primary_entries:
        root_html = root_html.replace(f'href="{num}.html"', f'href="{PRIMARY}/{num}.html"')
    (ROOT / "index.html").write_text(root_html, encoding="utf-8")
    print("root index: ok")


if __name__ == "__main__":
    main()
