#!/usr/bin/env python3
"""Run the SC-FIG-05.3 Chromium harnesses in headless Chrome over a loopback HTTP server.

    python3 scripts/run_chromium_fig05.py <out-dir>

Pages: tests/chromium-fig05-uncertainty.html (chart: runtime bands and ensemble fan, refusals, unavailable
state) and tests/chromium-fig05-map-uncertainty.html (strict CSP map: value and uncertainty layers, legend,
export receipt, refusals). Each runs at 1280 px and at 390 px wide; at 390 px the page must not scroll
sideways. WebGL comes from SwiftShader. Writes <out-dir>/fig05-chromium.json, screenshots and the map export
PNG; exits non-zero on any failure. Needs the `websockets` package.
"""
import asyncio
import base64
import functools
import hashlib
import http.server
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request

import websockets

ROOT = pathlib.Path(__file__).resolve().parents[1]
CHROME = [os.environ.get("CHROME_BIN"), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "google-chrome", "chromium"]


def chrome():
    for c in CHROME:
        if c and (os.path.exists(c) or shutil.which(c)):
            return c if os.path.exists(c) else shutil.which(c)
    raise SystemExit("no Chrome found; set CHROME_BIN")


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


PAGES = (("chart", "tests/chromium-fig05-uncertainty.html"), ("map", "tests/chromium-fig05-map-uncertainty.html"))


async def main(out):
    results = []
    for name, page in PAGES:
        for width in (1280, 390):
            results.append(await run_page(out, name, page, width))
    lines = [f"[{r['page']} {r['width']}px] {l}" for r in results for l in r["log"]]
    report = {"schema": "sc-lab-fig05-chromium/1.0", "state": "pass" if all(r["state"] == "pass" for r in results) else "fail",
              "passed": sum(l.split("] ", 1)[1].startswith("ok") for l in lines), "total": len(lines), "runs": results}
    (out / "fig05-chromium.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"{report['passed']}/{report['total']} {report['state']}")
    return report["state"] == "pass"


async def run_page(out, name, page_path, width):
    worker = ROOT / "assets/lib/maplibre-gl-5.24.0/maplibre-gl-csp-worker.js"
    integrity = "sha384-" + base64.b64encode(hashlib.sha384(worker.read_bytes()).digest()).decode()
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{httpd.server_port}"
    url = f"{origin}/{page_path}#integrity={integrity}"
    port = 9700 + os.getpid() % 200
    profile = tempfile.mkdtemp(prefix="sc-fig05-")
    proc = subprocess.Popen([chrome(), "--headless=new", "--no-first-run", "--no-default-browser-check", "--disable-extensions",
                             "--enable-unsafe-swiftshader", "--use-angle=swiftshader", f"--window-size={width},1800",
                             f"--remote-debugging-port={port}", f"--user-data-dir={profile}", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    events, pending, nid = [], {}, [0]
    try:
        for _ in range(100):
            try:
                page = next(p for p in json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=1).read()) if p.get("type") == "page")
                break
            except Exception:
                time.sleep(0.1)
        async with websockets.connect(page["webSocketDebuggerUrl"], max_size=64 * 1024 * 1024) as ws:
            async def pump():
                async for raw in ws:
                    m = json.loads(raw)
                    if "id" in m and m["id"] in pending:
                        pending.pop(m["id"]).set_result(m)
                    elif "method" in m:
                        events.append(m)

            async def call(method, **params):
                nid[0] += 1
                fut = asyncio.get_running_loop().create_future()
                pending[nid[0]] = fut
                await ws.send(json.dumps({"id": nid[0], "method": method, "params": params}))
                m = await asyncio.wait_for(fut, 120)
                if "error" in m:
                    raise RuntimeError(m["error"])
                return m.get("result", {})

            async def js(expr):
                r = await call("Runtime.evaluate", expression=expr, awaitPromise=True, returnByValue=True)
                return r["result"].get("value")

            task = asyncio.create_task(pump())
            for d in ("Network.enable", "Log.enable", "Runtime.enable", "Page.enable"):
                await call(d)
            await call("Page.navigate", url=url)
            for _ in range(1200):
                if await js("document.body && document.body.getAttribute('data-cert') !== 'running'"):
                    break
                await asyncio.sleep(0.1)
            state = await js("document.body.getAttribute('data-cert')")
            overflow = await js("document.documentElement.scrollWidth - window.innerWidth")
            wide = await js("JSON.stringify([...document.querySelectorAll('body, body *')].filter(e => e.offsetWidth > window.innerWidth).map(e => { const c = getComputedStyle(e); return e.tagName + '.' + String(e.getAttribute('class') || '').slice(0, 30) + ':' + e.offsetWidth + ':' + c.display + ':' + c.overflowX; }).slice(0, 10))")
            b64 = await js("window.__fig05 && window.__fig05.exportB64 || ''")
            if b64:
                (out / f"fig05-{name}-{width}-export.png").write_bytes(base64.b64decode(b64))
            log = await js("document.getElementById('cert-log').textContent")
            await asyncio.sleep(1.0)
            shot = await call("Page.captureScreenshot", format="png", captureBeyondViewport=True)
            (out / f"fig05-{name}-{width}.png").write_bytes(base64.b64decode(shot["data"]))
            task.cancel()
    finally:
        proc.terminate()
        proc.wait(10)
        shutil.rmtree(profile, ignore_errors=True)
        httpd.shutdown()
    reqs = [e["params"]["request"]["url"] for e in events if e["method"] == "Network.requestWillBeSent"]
    foreign = [u for u in reqs if not (u.startswith(origin) or u.startswith("blob:") or u.startswith("data:"))]
    console = [e["params"]["entry"]["text"] for e in events if e["method"] == "Log.entryAdded" and e["params"]["entry"]["level"] == "error"]
    lines = (log or "").splitlines()
    lines += [("ok   " if not foreign else "FAIL ") + "network: every request same-origin, blob: or data: (" + str(len(reqs)) + " requests)",
              ("ok   " if not console else "FAIL ") + "no console errors " + json.dumps(console[:3])]
    if width <= 400:
        lines.append(("ok   " if overflow is not None and overflow <= 0 else "FAIL ") + f"no sideways scroll at {width} px (overflow {overflow}) {'' if overflow is not None and overflow <= 0 else wide}")
    ok = state == "pass" and all(l.startswith("ok") for l in lines)
    return {"page": name, "width": width, "state": "pass" if ok else "fail", "log": lines,
            "requests": sorted({u.replace(origin, "") for u in reqs})}


if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    out.mkdir(parents=True, exist_ok=True)
    sys.exit(0 if asyncio.run(main(out)) else 1)
