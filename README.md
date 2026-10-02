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
index.html          Home
Gallery.html        Performance gallery
JoinUs.html         Our Team + Join Us
partials/
  header.html       Logo, nav bar and overlay menu  (shared by all 3 pages)
  footer.html       Join prompt, social links, credits (shared by all 3 pages)
assets/
  css/styles.css
  js/includes.js    Injects the partials, wires up the overlay menu
  js/main.js        Scroll fade-in animations
  img/brand/        Logos, icons, client logos
  img/gallery/      Performance photos, by year
  img/members/      Team photos, by year
```

The header and footer live in `partials/` and are pulled into each page at
runtime by `assets/js/includes.js`, which fills any element carrying a
`data-include="<path>"` attribute. Edit those two files once rather than
changing the same markup in three pages.

Each page sets `<body data-page="...">` (`home`, `gallery` or `team`). The
include script uses that to add the `current-page` class to the matching nav
link, which is what highlights the current page in orange.

## Running it locally

`fetch()` is blocked on `file://` URLs, so opening a page by double-clicking it
shows the page without its header and footer. Serve the folder over HTTP
instead:

```sh
python3 -m http.server
```

Then open <http://localhost:8000/>.

## Deployment

Pushing to `main` triggers `.github/workflows/deploy-pages.yml`, which uploads
the repository root and deploys it to GitHub Pages. The Pages source is set to
"GitHub Actions" in the repository settings, and the custom domain
(neudragonliondance.org) is configured there as well.
