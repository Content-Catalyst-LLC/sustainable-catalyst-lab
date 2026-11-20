#!/usr/bin/env python3
"""SC-LAB-UI-01: browser interaction acceptance for the bounded WordPress Lab front door.

Run:
  python3 -m pip install playwright
  python3 -m playwright install chromium
  python3 scripts/run_chromium_lab_frontdoor.py /tmp/sc-lab-ui-01

This runs only against a synthetic loopback fixture; it never touches production.
A separate WordPress staging clone must still validate actual plugin enqueue, CSP,
asset timing, authenticated and anonymous behavior before a production release.
"""
import functools
import http.server
import json
import os
from pathlib import Path
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
HTML = "tests/chromium-lab-safe-controls.html"


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("playwright missing: python3 -m pip install playwright") from exc
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/sc-lab-ui-01")
    out.mkdir(parents=True, exist_ok=True)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    results = []
    try:
        with sync_playwright() as p:
            kwargs = {"headless": True}
            if os.environ.get("CHROME_BIN"):
                kwargs["executable_path"] = os.environ["CHROME_BIN"]
            browser = p.chromium.launch(**kwargs)
            try:
                for width in (1280, 390):
                    page = browser.new_page(viewport={"width": width, "height": 900})
                    errors = []
                    page.on("pageerror", lambda e: errors.append(str(e)))
                    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
                    page.goto(f"http://127.0.0.1:{server.server_port}/{HTML}", wait_until="load")
                    page.wait_for_function("document.body.dataset.cert !== 'running'", timeout=20000)
                    result = page.evaluate("window.__labSafeControlsCert")
                    result = result or {"passed": [], "errors": ["No browser acceptance receipt"]}
                    result["viewport"] = width
                    result["consoleErrors"] = errors
                    result["state"] = "pass" if not (result["errors"] or errors) else "fail"
                    results.append(result)
                    page.screenshot(path=str(out / f"safe-controls-{width}.png"), full_page=True)
                    print(f"{width}px: {result['state']} ({len(result['passed'])} passed, {len(result['errors'])} failed)")
                    page.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
    state = "pass" if all(row["state"] == "pass" for row in results) else "fail"
    receipt = {"schema": "sc-lab-ui-01-browser-acceptance/1.0", "state": state,
               "fixture": HTML, "syntheticOnly": True, "results": results}
    (out / "acceptance.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("Receipt:", out / "acceptance.json")
    return 0 if state == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
