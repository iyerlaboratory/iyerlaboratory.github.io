#!/bin/bash
# Rebuild the site. Run from anywhere:  bash _source/news-tools/rebuild.sh [page.html ...]
# With no arguments it rebuilds all seven pages. Works on Python 3.10+ (patches build.py's
# nav f-string, which needs 3.12, in a temporary copy).
set -e
S="$(cd "$(dirname "$0")/../.." && pwd)"
T="$(mktemp -d)"
mkdir -p "$T/_source" "$T/assets"
python3 - "$S/_source/build.py" "$T/_source/build.py" <<'PY'
import sys
s=open(sys.argv[1]).read()
old="""f'        <a href="{href}"{" aria-current=\\"page\\"" if href == current else ""}>{label}</a>'"""
s=s.replace(old, """'        <a href="' + href + '"' + (' aria-current="page"' if href == current else '') + '>' + label + '</a>'""")
open(sys.argv[2],'w').write(s)
PY
cp "$S/_source/minidiagrams.py" "$T/_source/"
cp -r "$S/assets/news" "$T/assets/news"
ln -s "$S/assets/img" "$T/assets/img"
[ -d "$S/assets/gallery" ] && cp -r "$S/assets/gallery" "$T/assets/gallery"
(cd "$T" && python3 _source/build.py >/dev/null)
PAGES="$@"; [ -z "$PAGES" ] && PAGES="index.html research.html publications.html team.html news.html resources.html join.html"
for f in $PAGES; do cp "$T/$f" "$S/$f"; done
rm -rf "$T"
echo "Rebuilt: $PAGES"
