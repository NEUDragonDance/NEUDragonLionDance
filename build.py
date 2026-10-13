#!/usr/bin/env python3
"""Build the static site into _site/.

Resolves every data-include="<path>" attribute by inlining that file's contents,
so the shared header and footer end up as real HTML in each page instead of
being fetched by the browser at runtime. Also stamps the current-page class onto
the nav link matching each page's <body data-page="...">.

No dependencies. Usage:

    python3 build.py              build once into _site/
    python3 build.py --serve      build, serve on :8000, rebuild on change
    python3 build.py --serve 9000 same, on a different port
    python3 build.py --watch      rebuild on change without serving

Assets are synced rather than re-copied, so rebuilds after the first are fast
even though assets/ is a few hundred MB.
"""
import functools
import http.server
import os
import re
import shutil
import socketserver
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
OUT = ROOT / "_site"

COPY_DIRS = ["assets"]
COPY_FILES = ["CNAME", ".nojekyll"]
# Directories whose contents are watched for changes in --watch/--serve mode.
WATCH_DIRS = ["partials", "assets"]

INCLUDE_RE = re.compile(
    r'(<(\w+)[^>]*?\sdata-include="([^"]+)"[^>]*>)(\s*)(</\2>)', re.DOTALL)


def pages():
    return sorted(p for p in ROOT.glob("*.html"))


def resolve_includes(html, page_name, errors):
    """Replace <tag data-include="f"></tag> with the contents of f."""
    def sub(m):
        open_tag, _tag, src, _ws, close_tag = m.groups()
        part = ROOT / src
        if not part.is_file():
            errors.append(f'{page_name}: data-include="{src}" not found')
            return m.group(0)
        body = part.read_text(encoding="utf-8").strip()
        # Drop the data-include attribute; it has served its purpose.
        open_tag = re.sub(r'\s*data-include="[^"]*"', "", open_tag)
        return f"{open_tag}\n{body}\n{close_tag}"

    return INCLUDE_RE.sub(sub, html)


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


def sync_file(src, dst):
    """Copy src to dst only when it differs. Returns True if copied."""
    if dst.exists():
        s, d = src.stat(), dst.stat()
        if s.st_size == d.st_size and int(s.st_mtime) <= int(d.st_mtime):
            return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def sync_tree(src_dir, dst_dir):
    """Mirror src_dir into dst_dir, copying only changes and pruning removals."""
    copied = 0
    wanted = set()
    for src in src_dir.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(src_dir)
        wanted.add(rel)
        if sync_file(src, dst_dir / rel):
            copied += 1
    removed = 0
    if dst_dir.exists():
        for dst in list(dst_dir.rglob("*")):
            if dst.is_file() and dst.relative_to(dst_dir) not in wanted:
                dst.unlink()
                removed += 1
    return copied, removed


def build(quiet=False):
    def say(msg):
        if not quiet:
            print(msg)

    OUT.mkdir(exist_ok=True)
    errors = []

    built = []
    for page in pages():
        html = page.read_text(encoding="utf-8")
        html = resolve_includes(html, page.name, errors)
        html = mark_current_page(html)
        target = OUT / page.name
        if not target.exists() or target.read_text(encoding="utf-8") != html:
            target.write_text(html, encoding="utf-8")
        built.append(page.name)
    say(f"  pages:  {', '.join(built)}")

    for d in COPY_DIRS:
        if (ROOT / d).is_dir():
            copied, removed = sync_tree(ROOT / d, OUT / d)
            if copied or removed:
                say(f"  {d}/: {copied} copied, {removed} removed")
    for f in COPY_FILES:
        if (ROOT / f).is_file():
            sync_file(ROOT / f, OUT / f)

    # Drop stale pages that no longer exist in the source.
    for stale in OUT.glob("*.html"):
        if stale.name not in built:
            stale.unlink()
            say(f"  removed stale {stale.name}")

    for e in errors:
        print(f"  ERROR {e}", file=sys.stderr)
    if errors:
        print(f"Build failed: {len(errors)} unresolved include(s)", file=sys.stderr)
        return False
    return True


def snapshot():
    """mtime+size of every source file, for change detection."""
    state = {}
    for p in pages():
        state[p] = (p.stat().st_mtime, p.stat().st_size)
    for d in WATCH_DIRS:
        for p in (ROOT / d).rglob("*"):
            if p.is_file():
                state[p] = (p.stat().st_mtime, p.stat().st_size)
    return state


def watch_loop(interval=0.5):
    prev = snapshot()
    while True:
        time.sleep(interval)
        try:
            cur = snapshot()
        except FileNotFoundError:
            continue
        if cur != prev:
            changed = [p.name for p in set(cur) ^ set(prev)] or [
                p.name for p in cur if prev.get(p) != cur[p]]
            print(f"\n→ changed: {', '.join(sorted(set(changed))[:4])} — rebuilding")
            build()
            prev = cur


def serve(port):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                directory=str(OUT))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"\nServing {OUT.name}/ at http://localhost:{port}/  (Ctrl-C to stop)")
        httpd.serve_forever()


def main(argv):
    do_serve = "--serve" in argv
    do_watch = do_serve or "--watch" in argv
    port = 8000
    for a in argv:
        if a.isdigit():
            port = int(a)

    print("Building…")
    if not build():
        return 1
    print(f"Built {len(pages())} pages into {OUT.name}/")

    if do_serve:
        threading.Thread(target=watch_loop, daemon=True).start()
        try:
            serve(port)
        except KeyboardInterrupt:
            print("\nStopped.")
        except OSError as e:
            print(f"\nCould not bind port {port}: {e}", file=sys.stderr)
            return 1
    elif do_watch:
        print("Watching for changes (Ctrl-C to stop)…")
        try:
            watch_loop()
        except KeyboardInterrupt:
            print("\nStopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
