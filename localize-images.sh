#!/usr/bin/env bash
# Copies every image/PDF the site still loads from the old WordPress site
# (iyerlaboratory.org/wp-content/uploads/...) into assets/img/, and rewrites
# the HTML to use the local copies. Run once, from this folder, BEFORE you
# shut down the WordPress site:
#
#     bash localize-images.sh
#
# Works on macOS and Linux (needs curl, grep and perl, all preinstalled).
set -euo pipefail
cd "$(dirname "$0")"

BASE="https://iyerlaboratory.org/wp-content/uploads/"
urls=$(grep -ohE "https://iyerlaboratory\.org/wp-content/uploads/[^\"') ]+" *.html | sort -u)

for url in $urls; do
  rel="${url#$BASE}"
  dest="assets/img/$rel"
  mkdir -p "$(dirname "$dest")"
  if [ ! -s "$dest" ]; then
    echo "Downloading $rel"
    curl -fsSL "$url" -o "$dest" || { echo "  ! failed: $url"; rm -f "$dest"; continue; }
  fi
done

# Point the pages at the local copies (only for files that downloaded).
for url in $urls; do
  rel="${url#$BASE}"
  if [ -s "assets/img/$rel" ]; then
    perl -pi -e "s#\Q$url\E#assets/img/$rel#g" *.html
  fi
done

echo "Done. Images now live in assets/img/."
