#!/usr/bin/env python3
"""Read-only inspection of a saved Lab HTML response; never prints cookies/nonces.
Usage: python3 scripts/diagnose_lab_script_delivery.py ~/sc-lab-graph-hotfix/served-lab.html
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import sys

class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.styles = []
    def handle_starttag(self, tag, pairs):
        a = dict(pairs)
        if tag == "script":
            self.scripts.append(a)
        elif tag == "link" and "stylesheet" in (a.get("rel") or ""):
            self.styles.append(a)

path = Path(sys.argv[1]).expanduser() if len(sys.argv)>1 else Path.home()/"sc-lab-graph-hotfix"/"served-lab.html"
if not path.is_file():
    raise SystemExit(f"Not found: {path}")
page = path.read_text(errors="replace")
p = Tags()
p.feed(page)

print("saved_html_bytes:", path.stat().st_size)
print("script_tags:", len(p.scripts))
print("stylesheet_links:", len(p.styles))
print("lab_app_present:", 'class="sc-lab-app"' in page)
print("wp_footer_marker:", 'id="wpadminbar"' in page or 'wp-emoji-release.min.js' in page)

expected = (
 "sc-lab-safe-bootstrap-v015206.js",
 "scientific-visualization-engine-v0440.js",
 "graph-studio-v0470.js",
)
for name in expected:
    print("expected_asset:", name,
          "html_occurrences=", page.count(name),
          "src_tags=", sum(name in a.get("src","") for a in p.scripts))

print("\nSCRIPT SOURCES (pathname only; query strings omitted):")
for i,a in enumerate(p.scripts):
    src = a.get("src","")
    if src:
        u=urlsplit(src)
        # Basename only: avoid printing tokens/query params and account-specific paths.
        basename=unquote(u.path).rstrip("/").split("/")[-1]
        print(f"{i:02d}: {basename[:120]}")
    else:
        attrs=','.join(k for k in a if k.startswith("data-") or k=="type")
        print(f"{i:02d}: [inline script] attrs={attrs[:80]}")

print("\nLAB STYLESHEETS (basenames):")
for a in p.styles:
    href=a.get("href","")
    if any(k in href.lower() for k in ("lab","optimize","cache","minify","assets")):
        print(unquote(urlsplit(href).path).rstrip("/").split("/")[-1][:120])

print("\nPotential optimization markers (presence only):")
for k in ("autoptimize","litespeed","wp-rocket","rocket-loader","cloudflare",
          "data-src","data-rocket-src","data-cfasync","defer","delay_js","async"):
    print(k,":",k.lower() in page.lower())
