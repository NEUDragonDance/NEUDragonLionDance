# NEUDragonLionDance
The official website of the Northeastern University Dragon and Lion Dance Troupe!
<br>Live at neudragonliondance.org
<br>Created by Serena Ng
<br><br>
<strong>Version 3.0 Updates:</strong>
- Loading animations/transitions
- Updated the Our Team page for 2024-25
- Updated the Gallery page with recent performances and new copy
- Added webp file format for faster loading
- Updated copy
- Updated Join Us page to have the 2024-25 interest form link
- Design updates (e.g. CSS styling, Client logos, more interactions, etc.)

## Project structure

```
build.py            Build script: inlines partials, writes _site/ (--serve to preview)
index.html          Home
Gallery.html        Performance gallery
JoinUs.html         Our Team + Join Us
partials/
  header.html       Logo, nav bar and overlay menu  (shared by all 3 pages)
  footer.html       Join prompt, social links, credits (shared by all 3 pages)
assets/
  css/styles.css
  js/nav.js         Overlay menu open/close
  js/main.js        Scroll fade-in animations
  img/brand/        Logos, icons, client logos
  img/gallery/      Performance photos, by year
  img/members/      Team photos, by year
```

The header and footer live in `partials/` and are inlined into each page at
build time by `build.py`, which replaces any element carrying a
`data-include="<path>"` attribute with that file's contents. Edit those two
files once rather than changing the same markup in three pages.

Each page sets `<body data-page="...">` (`home`, `gallery` or `team`). The
build uses that to add the `current-page` class to the matching nav link,
which is what highlights the current page in orange.

Because this happens at build time, the nav ships as real HTML -- no
JavaScript is needed to render it. `assets/js/nav.js` only handles opening
and closing the overlay menu on narrow screens.

## Running it locally

The header and footer live in `partials/` and are stamped into each page by
`build.py`, so you need to build before you preview. Serving the repository
root directly will show pages with no nav and no footer.

```sh
python3 build.py --serve
```

That builds, serves <http://localhost:8000/>, and watches `*.html`,
`partials/` and `assets/` — editing any of them rebuilds automatically, so you
just refresh the browser. Ctrl-C stops it. Add a port number to change it:
`python3 build.py --serve 9000`.

Other modes:

| Command | What it does |
| --- | --- |
| `python3 build.py` | Build once into `_site/` |
| `python3 build.py --watch` | Rebuild on change, no server |
| `python3 build.py --serve` | Build, serve and watch (what you usually want) |

It needs nothing beyond Python 3 — no npm, no bundler, no file-watcher package.
Rebuilds are incremental: assets are synced rather than re-copied, so only the
first build touches the image directories.

`_site/` is generated output and is gitignored; never edit it by hand.

## Deployment

Pushing to `main` triggers `.github/workflows/deploy-pages.yml`, which runs
`python3 build.py` and deploys the resulting `_site/` to GitHub Pages. The
build needs no dependencies beyond the runner's bundled Python.

The Pages source is set to "GitHub Actions" in the repository settings, and the
custom domain (neudragonliondance.org) is configured there as well.
