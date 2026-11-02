# Iyer Lab website

A plain HTML/CSS site (no build step) for the Iyer Lab at Rice University, ready for GitHub Pages.

```
index.html          Home
research.html       Primer, lysosomal biology, brain disorders, image gallery
publications.html   Preprints, selected and other publications
team.html           Lab members
news.html           Lab news
resources.html      Trainee resources
join.html           Join our shoal + contact
assets/css/style.css   All styling (colors and fonts are at the top)
assets/js/site.js      Mobile menu
assets/img/            Images (see "Images" below)
localize-images.sh     Copies images from the old site into assets/img/
```

To preview, double-click `index.html`.

## Images — do this first

Photos, figures and PDFs currently load from the old WordPress site. Before you turn that site off, run this once from this folder:

```bash
bash localize-images.sh
```

It downloads everything into `assets/img/` and updates the pages to use the local copies.

## Put it on GitHub Pages

1. Create a new repository on GitHub (e.g. `iyerlab/iyerlab.github.io`, or any name).
2. Upload the contents of this folder: on the repo page, **Add file → Upload files**, drag everything in (including `assets/` and `.nojekyll`), and commit.
3. **Settings → Pages → Build and deployment**: Source = *Deploy from a branch*, Branch = `main`, folder = `/ (root)`. Save.
4. In a minute or two the site is live at the address shown on that page.

### Use iyerlaboratory.org

1. **Settings → Pages → Custom domain**: enter `iyerlaboratory.org` and save (GitHub adds a `CNAME` file).
2. At your domain registrar, set DNS:
   - `A` records for `@` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - `CNAME` for `www` → `<your-github-username>.github.io`
3. Once the DNS check passes, tick **Enforce HTTPS**.

Run `localize-images.sh` before switching DNS, since the image links point at the old site.

## Everyday edits

All edits can be done in the GitHub web editor (open a file → pencil icon → commit).

- **New paper**: in `publications.html`, copy an existing `<li class="pub">…</li>` block, paste it at the top of the right list, and change the year, title, authors, journal and links. Wrap lab members in `<b>…</b>`.
- **New news item**: in `news.html`, copy an `<a class="card news-card">…</a>` block to the top of the list and change the date, text and photo. Put the photo in `assets/img/` (a wide crop, about 845×321, looks best in the card; the `href` can point to a larger version). To feature it on the home page, also update the three news cards in `index.html`.
- **New lab member**: in `team.html`, copy an `<article class="person">` block, then add their photo to `assets/img/`. Add them to the people strip in `index.html` too.
- **Colors and fonts**: change the variables at the top of `assets/css/style.css`. The site uses Rice's brand palette: Rice Blue (#00205B) for titles, Rich Blue (#0A509E) for emphasis, and Rice's approved web fonts, Lato and Cormorant Garamond.

## Moving to another computer

Everything needed to edit and rebuild the site is in this folder. Copy the whole folder
(or zip it). On the new computer you need Python 3.10 or newer, then:

```bash
pip install -r requirements.txt
bash _source/news-tools/rebuild.sh          # rebuilds all seven pages
```

- `_source/build.py` holds all page text and data (people, papers, news, resources). Edit it, then rebuild.
- `_source/minidiagrams.py` draws the home-page research figures.
- `_source/news-tools/` holds the photo tools:
  - `event.py <date> photo1 photo2 ...` makes a news collage plus web copies in `assets/news/<date>/`
  - `collage.py` handles the collage layout (justified rows, white gutters)
  - `backlight.py in.jpg out.jpg` removes backlight glare and lifts shadowed faces
  - `sharpen_tv.py in.jpg out.jpg` cleans up photos taken of a TV screen
  - `heic2jpg.py in.HEIC out.jpg` converts iPhone HEIC photos (needs `libde265`)
- `news-photos/<date> <description>/` keeps the original photos for each news item.
- `HANDOFF.md` records design decisions, style rules, and the to-do list.

Not needed for the website: `gallery-raw/` (originals of the gallery images) and any
slide decks in this folder. Keep them out of the GitHub repo.
