#!/usr/bin/env python3
"""Build the static site into _site/.

Resolves every data-include="<path>" attribute by inlining that file's contents,
so the shared header and footer end up as real HTML in each page instead of
being fetched by the browser at runtime. Also stamps the current-page class onto
the nav link matching each page's <body data-page="...">.

No dependencies -- just `python3 build.py`.
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "_site"

PAGES = sorted(p for p in ROOT.glob("*.html"))
COPY_DIRS = ["assets"]
COPY_FILES = ["CNAME", ".nojekyll"]

INCLUDE_RE = re.compile(
    r'(<(\w+)[^>]*?\sdata-include="([^"]+)"[^>]*>)(\s*)(</\2>)', re.DOTALL)


def resolve_includes(html, page_name):
    """Replace <tag data-include="f"></tag> with the contents of f."""
    missing = []

    def sub(m):
        open_tag, tag, src, _ws, close_tag = m.groups()
        part = ROOT / src
        if not part.is_file():
            missing.append(f"{page_name}: data-include=\"{src}\" not found")
            return m.group(0)
        body = part.read_text(encoding="utf-8").strip()
        # Drop the data-include attribute; it has served its purpose.
        open_tag = re.sub(r'\s*data-include="[^"]*"', "", open_tag)
        return f"{open_tag}\n{body}\n{close_tag}"

    html = INCLUDE_RE.sub(sub, html)
    for problem in missing:
        print(f"  ERROR {problem}", file=sys.stderr)
    return html, missing


def mark_current_page(html):
    """Add .current-page to nav links matching <body data-page="...">."""
    m = re.search(r'<body[^>]*\sdata-page="([^"]+)"', html)
    if not m:
        return html
    page = m.group(1)
    return re.sub(
        r'(<a\b[^>]*?)\sdata-nav="%s"' % re.escape(page),
        r'\1 data-nav="%s" class="current-page" aria-current="page"' % page,
        html,
    )


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    errors = []
    for page in PAGES:
        html = page.read_text(encoding="utf-8")
        html, missing = resolve_includes(html, page.name)
        errors += missing
        html = mark_current_page(html)
        (OUT / page.name).write_text(html, encoding="utf-8")
        print(f"  built {page.name}")

    for d in COPY_DIRS:
        if (ROOT / d).is_dir():
            shutil.copytree(ROOT / d, OUT / d)
            print(f"  copied {d}/")
    for f in COPY_FILES:
        if (ROOT / f).is_file():
            shutil.copy2(ROOT / f, OUT / f)
            print(f"  copied {f}")

    if errors:
        print(f"\nBuild failed: {len(errors)} unresolved include(s)", file=sys.stderr)
        return 1
    print(f"\nBuilt {len(PAGES)} pages into {OUT.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
