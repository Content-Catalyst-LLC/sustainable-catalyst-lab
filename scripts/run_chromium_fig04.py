#!/usr/bin/env python3
"""Run tests/chromium-fig04-maplibre.html in headless Chrome over a loopback HTTP server.

    python3 scripts/run_chromium_fig04.py <out-dir>

The page has a strict CSP (no inline script or style, worker only from a verified blob). WebGL comes from
SwiftShader. Writes <out-dir>/fig04-chromium.json and screenshots; exits non-zero on any failure.
Needs the `websockets` package.
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


async def main(out):
    worker = ROOT / "assets/lib/maplibre-gl-5.24.0/maplibre-gl-csp-worker.js"
    integrity = "sha384-" + base64.b64encode(hashlib.sha384(worker.read_bytes()).digest()).decode()
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{httpd.server_port}"
    url = f"{origin}/tests/chromium-fig04-maplibre.html#integrity={integrity}"
    port = 9700 + os.getpid() % 200
    profile = tempfile.mkdtemp(prefix="sc-fig04-")
    proc = subprocess.Popen([chrome(), "--headless=new", "--no-first-run", "--no-default-browser-check", "--disable-extensions",
                             "--enable-unsafe-swiftshader", "--use-angle=swiftshader", "--window-size=1280,1800",
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
            shot_taken = False
            for _ in range(1200):
                if not shot_taken and await js("!!(window.__fig04 && window.__fig04.ready)"):
                    await asyncio.sleep(1.5)
                    shot = await call("Page.captureScreenshot", format="png", captureBeyondViewport=True)
                    (out / "fig04-chromium-compare.png").write_bytes(base64.b64decode(shot["data"]))
                    await js("window.__fig04.continue = true")
                    shot_taken = True
                if await js("document.body && document.body.getAttribute('data-cert') !== 'running'"):
                    break
                await asyncio.sleep(0.1)
            state = await js("document.body.getAttribute('data-cert')")
            for key, name in (("exportB64", "fig04-export.png"), ("compareB64", "fig04-export-compare.png")):
                b64 = await js(f"window.__fig04 && window.__fig04.{key} || ''")
                if b64:
                    (out / name).write_bytes(base64.b64decode(b64))
            receipt = await js("window.__fig04 && window.__fig04.exportReceipt ? JSON.stringify(window.__fig04.exportReceipt, null, 1) : ''")
            if receipt:
                (out / "fig04-export.receipt.json").write_text(receipt + "\n", encoding="utf-8")
            log = await js("document.getElementById('cert-log').textContent")
            await asyncio.sleep(1.0)
            shot = await call("Page.captureScreenshot", format="png", captureBeyondViewport=True)
            (out / "fig04-chromium-final.png").write_bytes(base64.b64decode(shot["data"]))
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
    extra = [("ok   " if not foreign else "FAIL ") + "network: every request same-origin, blob: or data: (" + str(len(reqs)) + " requests)",
             ("ok   " if not console else "FAIL ") + "no console errors " + json.dumps(console[:3])]
    lines += extra
    report = {"schema": "sc-lab-fig04-chromium/1.0", "state": state if not foreign and not console else "fail",
              "passed": sum(l.startswith("ok") for l in lines), "total": len(lines), "log": lines,
              "requests": sorted({u.replace(origin, "") for u in reqs})}
    (out / "fig04-chromium.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"{report['passed']}/{report['total']} {report['state']}")
    return report["state"] == "pass"


if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    out.mkdir(parents=True, exist_ok=True)
    sys.exit(0 if asyncio.run(main(out)) else 1)
