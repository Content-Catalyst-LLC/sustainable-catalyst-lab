"""FIG-02A Graph Studio preview acceptance against a live Lab WordPress staging site.

Drives a local headless Chrome over the DevTools protocol (no browser-automation dependency
beyond `websockets`), opens the real Lab page, opens Graph Studio, feeds the exact Workbench
staging responses (tests/fixtures/fig02a-staging-amd64) through the module's
`sc-lab:fig02a:preview` event, and checks rendering, hashes, labels, accessibility semantics and
every network request the page makes.

    python tests/staging/fig02a_wordpress_acceptance.py http://127.0.0.1:18190/lab/ <out dir>
        [--preview on|off] [--expect-release 0.163.1.4] [--label staging|production]

With --preview off it checks the switched-off state instead: no preview config, no plotly.js, no
preview section, and the existing Graph Studio still opens and renders. Both modes require the
Lab release-integrity route to report "verified" (and the expected release, when given), and fail
on any uncaught page exception attributable to the preview or plotly.js.

The staging site must be reachable at the URL (for example via an SSH tunnel). Nothing is posted
to the site; the preview never contacts Workbench.
"""
import argparse
import asyncio
import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

import websockets

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "fig02a-staging-amd64"
CHROME_CANDIDATES = [os.getenv("CHROME_BIN", ""), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                     "google-chrome", "google-chrome-stable", "chromium"]


class Cdp:
    def __init__(self, ws):
        self.ws, self.next_id, self.pending, self.events = ws, 0, {}, []

    async def pump(self):
        async for raw in self.ws:
            msg = json.loads(raw)
            if "id" in msg and msg["id"] in self.pending:
                self.pending.pop(msg["id"]).set_result(msg)
            elif "method" in msg:
                self.events.append(msg)

    async def call(self, method, **params):
        self.next_id += 1
        fut = asyncio.get_running_loop().create_future()
        self.pending[self.next_id] = fut
        await self.ws.send(json.dumps({"id": self.next_id, "method": method, "params": params}))
        msg = await asyncio.wait_for(fut, 60)
        if "error" in msg:
            raise RuntimeError(f"{method}: {msg['error']}")
        return msg.get("result", {})

    async def js(self, expression):
        r = await self.call("Runtime.evaluate", expression=expression, awaitPromise=True, returnByValue=True)
        if r.get("exceptionDetails"):
            raise RuntimeError(json.dumps(r["exceptionDetails"])[:600])
        return r["result"].get("value")

    async def wait_for(self, expression, timeout=60):
        end = time.time() + timeout
        while time.time() < end:
            if await self.js(expression):
                return True
            await asyncio.sleep(0.25)
        return False


def _chrome():
    for c in CHROME_CANDIDATES:
        if c and (os.path.exists(c) or shutil.which(c)):
            return c if os.path.exists(c) else shutil.which(c)
    raise SystemExit("no Chrome found; set CHROME_BIN")


CHECK_RENDER = r"""
(() => {
  const out = document.querySelector('[data-fig02a-preview] .sc-lab-fig02a-output');
  const card = out && out.querySelector('[data-fig02a-state="rendered"]');
  if (!card) { return {rendered: false, refused: !!(out && out.querySelector('[data-fig02a-state="refused"]'))}; }
  const plot = card.querySelector('.js-plotly-plot');
  const ev = card.querySelector('.sc-lab-fig02a-evidence');
  const tables = Array.from(card.querySelectorAll('.sc-lab-fig02a-tables table'));
  const notReported = Array.from(card.querySelectorAll('.sc-lab-fig02a-tables td, .sc-lab-fig02a-tables tbody th'))
    .filter(c => c.textContent === 'not reported').length;
  return {
    rendered: true,
    specSha256: card.getAttribute('data-spec-sha256'),
    evidenceClass: ev && ev.getAttribute('data-evidence-class'),
    evidenceText: ev && ev.textContent,
    reviewText: (card.querySelector('.sc-lab-fig02a-review') || {}).textContent || '',
    subtitleInFigure: !!(plot && plot.querySelector('.gtitle') && /Evidence:/.test(plot.querySelector('.gtitle').textContent)),
    svgDrawn: !!(plot && plot.querySelector('svg.main-svg')),
    traces: plot && plot.data ? plot.data.length : 0,
    plotRole: plot && plot.getAttribute('role'),
    plotLabelLength: plot ? (plot.getAttribute('aria-label') || '').length : 0,
    tableCount: tables.length,
    tablesHaveCaption: tables.every(t => !!t.querySelector('caption')),
    headersScoped: tables.every(t => Array.from(t.querySelectorAll('thead th')).every(th => th.getAttribute('scope') === 'col')),
    rowHeadersScoped: tables.every(t => Array.from(t.querySelectorAll('tbody th')).every(th => th.getAttribute('scope') === 'row')),
    bodyRows: card.querySelectorAll('.sc-lab-fig02a-tables tbody tr').length,
    notReported,
    linksOrMedia: card.querySelectorAll('a[href], img, iframe, script, object, embed').length,
    provenanceRows: card.querySelectorAll('.sc-lab-fig02a-provenance dt').length,
  };
})()
"""


GRAPH_STUDIO_STATE = r"""
(() => {
  const m = document.querySelector('[data-lab-module="graph-studio"]');
  const root = document.getElementById('sc-lab-graph-studio-renderer-root');
  return {module: !!m, visible: !!m && m.offsetHeight > 0 && getComputedStyle(m).display !== 'none',
          rendererRoot: !!root, rendererChildren: root ? root.querySelectorAll('*').length : 0,
          drawn: m ? m.querySelectorAll('svg, canvas').length : 0};
})()
"""


async def run(url, outdir, preview="on", expect_release=None, label="staging"):
    outdir.mkdir(parents=True, exist_ok=True)
    origin = "{0.scheme}://{0.netloc}".format(urlparse(url))
    port = 9333
    profile = tempfile.mkdtemp(prefix="fig02a-cdp-")
    proc = subprocess.Popen([_chrome(), "--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars",
                             f"--remote-debugging-port={port}", f"--user-data-dir={profile}",
                             "--window-size=1280,1600", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    report = {"url": url, "previewMode": preview, "expectRelease": expect_release, "checks": {}, "cases": {}, "network": {}}

    def check(name, cond, detail=None):
        report["checks"][name] = {"ok": bool(cond), "detail": detail}

    try:
        for _ in range(100):
            try:
                targets = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=2))
                page = next(t for t in targets if t.get("type") == "page")
                break
            except Exception:  # noqa: BLE001 - browser still starting
                time.sleep(0.2)
        async with websockets.connect(page["webSocketDebuggerUrl"], max_size=64 * 1024 * 1024) as ws:
            cdp = Cdp(ws)
            pump = asyncio.create_task(cdp.pump())
            await cdp.call("Network.enable")
            await cdp.call("Page.enable")
            await cdp.call("Runtime.enable")
            report["chrome"] = (await cdp.call("Browser.getVersion")).get("product")
            await cdp.call("Page.navigate", url=url)
            check("page.loaded", await cdp.wait_for("document.readyState === 'complete'", 90))
            integrity = json.load(urllib.request.urlopen(origin + "/wp-json/sc-lab/v1/runtime/v02632/health", timeout=30))
            report["integrity"] = {k: integrity.get(k) for k in ("ok", "state", "releaseVersion", "partialInstallRisk")}
            check("lab.integrityVerified", integrity.get("ok") is True and integrity.get("state") == "verified"
                  and (expect_release is None or integrity.get("releaseVersion") == expect_release), report["integrity"])
            await asyncio.sleep(2)
            if preview == "off":
                await check_off(cdp, check, report, outdir, origin, label)
                pump.cancel()
                return finish(report, outdir, label)
            cfg = await cdp.js("JSON.stringify(window.SCLabFig02aPlotlyPreviewConfig || null)")
            check("config.typedEnabled", json.loads(cfg or "null") and json.loads(cfg).get("enabled") is True, cfg)
            check("plotly.version", await cdp.js("window.Plotly && Plotly.version") == "3.3.1",
                  await cdp.js("window.Plotly && Plotly.version"))
            # Open Graph Studio through the Lab's own module navigation.
            opened = await cdp.js("""(() => { const b = document.querySelector('[data-lab-module-button="graph-studio"]');
                                     if (b) { b.click(); return 'button'; } return null; })()""")
            report["graphStudioOpenedVia"] = opened
            mounted = await cdp.wait_for("!!document.querySelector('[data-fig02a-preview]')", 60)
            where = await cdp.js("""(() => { const s = document.querySelector('[data-fig02a-preview]'); if (!s) return null;
                return {stage: !!s.closest('#sc-lab-graph-studio-renderer-root [data-gs13583-stage]'),
                        graphStudio: !!s.closest('[data-lab-module="graph-studio"]'),
                        sectionsOnPage: document.querySelectorAll('[data-fig02a-preview]').length}; })()""")
            report["graphStudio"] = await cdp.js(GRAPH_STUDIO_STATE)
            check("graphStudio.visible", report["graphStudio"]["visible"], report["graphStudio"])
            check("preview.mountedInGraphStudio", mounted and where and where["graphStudio"] and where["sectionsOnPage"] == 1, where)
            check("preview.fileInputKeyboardReachable", await cdp.js(
                "(() => { const i = document.querySelector('[data-fig02a-preview] input[type=file]'); return !!i && i.tabIndex >= 0 && !!i.getAttribute('aria-label'); })()"))
            check("preview.liveRegion", await cdp.js(
                "(() => { const o = document.querySelector('[data-fig02a-preview] .sc-lab-fig02a-output'); return !!o && o.getAttribute('aria-live') === 'polite'; })()"))

            source = json.loads((FIXTURES / "SOURCE.json").read_text())
            cases = [(name, (FIXTURES / name).read_text(encoding="utf-8")) for name in source["files"]]
            tampered = cases[0][1].replace('"y":[5.0,', '"y":[5.1,', 1)
            cases.append(("tampered-points.json", tampered))
            for name, text in cases:
                await cdp.js("document.querySelector('[data-fig02a-preview] .sc-lab-fig02a-output').textContent = ''")
                await cdp.js("document.dispatchEvent(new CustomEvent('sc-lab:fig02a:preview', {detail: {responseText: %s}}))"
                             % json.dumps(text))
                await cdp.wait_for("!!document.querySelector('[data-fig02a-preview] [data-fig02a-state]')", 60)
                await asyncio.sleep(0.5)
                state = await cdp.js(CHECK_RENDER)
                if name.startswith("tampered"):
                    report["cases"][name] = {"state": state}
                    check("tampered.refused", state.get("refused") and not state.get("rendered"), state)
                    continue
                resp = json.loads(text)
                rows = sum(len(p["rows"]) for p in resp["accessibleAlternative"]["panels"])
                nulls = sum(1 for p in resp["accessibleAlternative"]["panels"] for r in p["rows"] for v in r.values() if v is None)
                ok = (state["rendered"] and state["specSha256"] == resp["plotly"]["specSha256"]
                      and state["evidenceClass"] == resp["figureBundle"]["evidenceClass"] and state["subtitleInFigure"]
                      and "Not publication-approved" in state["reviewText"] and "pending" in state["reviewText"]
                      and state["svgDrawn"] and state["traces"] == len(resp["plotly"]["figure"]["data"])
                      and state["plotRole"] == "img" and state["plotLabelLength"] > 20
                      and state["tablesHaveCaption"] and state["headersScoped"] and state["rowHeadersScoped"]
                      and state["bodyRows"] == rows and state["notReported"] == nulls and state["linksOrMedia"] == 0
                      and state["provenanceRows"] >= 6)
                report["cases"][name] = {"ok": ok, "state": state, "expectedRows": rows, "expectedNotReported": nulls}
                check(f"case.{name}", ok)
                clip = await cdp.js("""(() => { const r = document.querySelector('[data-fig02a-preview]').getBoundingClientRect();
                    return {x: r.left + scrollX, y: r.top + scrollY, width: r.width, height: r.height, scale: 1}; })()""")
                shot = await cdp.call("Page.captureScreenshot", format="png", clip=clip, captureBeyondViewport=True)
                (outdir / f"{label}-{name.replace('.json', '')}.png").write_bytes(base64.b64decode(shot["data"]))

            await asyncio.sleep(1)
            network_checks(cdp, check, report, origin)
            pump.cancel()
    finally:
        proc.terminate()
        proc.wait(10)
        shutil.rmtree(profile, ignore_errors=True)
    return finish(report, outdir, label)


def network_checks(cdp, check, report, origin):
    urls = [e["params"]["request"]["url"] for e in cdp.events if e["method"] == "Network.requestWillBeSent"]
    remote = sorted({u.split("?")[0] for u in urls if not (u.startswith(origin) or u.startswith("data:") or u.startswith("blob:"))})
    report["network"] = {"requests": len(urls), "remote": remote,
                         "plotlyFromSite": [u.split("?")[0] for u in urls if "plotly" in u]}
    check("network.plotlyOnlyFromSite", all(u.startswith(origin) for u in urls if "plotly" in u.lower()))
    check("network.noWorkbenchCalls", not any("workbench" in u.lower() and not u.startswith(origin) for u in urls), remote)
    # Pre-existing site exceptions are recorded; only ones from the preview or plotly.js fail the run.
    exc = []
    for e in cdp.events:
        if e["method"] == "Runtime.exceptionThrown":
            d = e["params"]["exceptionDetails"]
            exc.append(((d.get("exception") or {}).get("description") or d.get("text") or "")[:300] + " @ " + (d.get("url") or ""))
    report["pageExceptions"] = exc
    check("page.noPreviewExceptions", not any(("fig02a" in x.lower() or "plotly" in x.lower()) for x in exc), exc)


async def check_off(cdp, check, report, outdir, origin, label):
    """Preview switched off: nothing of FIG-02A is served and Graph Studio behaves as before."""
    check("off.noConfig", await cdp.js("window.SCLabFig02aPlotlyPreviewConfig === undefined"))
    check("off.noPlotly", await cdp.js("typeof window.Plotly === 'undefined'"))
    opened = await cdp.js("""(() => { const b = document.querySelector('[data-lab-module-button="graph-studio"]');
                             if (b) { b.click(); return 'button'; } return null; })()""")
    report["graphStudioOpenedVia"] = opened
    await cdp.wait_for("(() => { const m = document.querySelector('[data-lab-module=\"graph-studio\"]'); return !!m && m.offsetHeight > 0; })()", 60)
    await asyncio.sleep(3)
    report["graphStudio"] = await cdp.js(GRAPH_STUDIO_STATE)
    check("graphStudio.opened", opened == "button" and report["graphStudio"]["visible"], report["graphStudio"])
    check("graphStudio.rendererPresent", report["graphStudio"]["rendererRoot"] and report["graphStudio"]["rendererChildren"] > 0, report["graphStudio"])
    check("off.noPreviewSection", await cdp.js("document.querySelectorAll('[data-fig02a-preview]').length === 0"))
    clip = await cdp.js("""(() => { const r = document.querySelector('[data-lab-module="graph-studio"]').getBoundingClientRect();
        return {x: r.left + scrollX, y: r.top + scrollY, width: Math.min(r.width, 1280), height: Math.min(r.height, 2400), scale: 1}; })()""")
    shot = await cdp.call("Page.captureScreenshot", format="png", clip=clip, captureBeyondViewport=True)
    (outdir / f"{label}-graph-studio-preview-off.png").write_bytes(base64.b64decode(shot["data"]))
    await asyncio.sleep(1)
    network_checks(cdp, check, report, origin)
    check("off.noPlotlyRequests", not report["network"]["plotlyFromSite"], report["network"]["plotlyFromSite"])


def finish(report, outdir, label):
    failed = [k for k, v in report["checks"].items() if not v["ok"]]
    report["result"] = "FAIL" if failed else "PASS"
    report["failed"] = failed
    (outdir / f"{label}-acceptance{'-preview-off' if report.get('previewMode') == 'off' else ''}.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps({k: report.get(k) for k in ("result", "failed", "chrome", "integrity", "graphStudioOpenedVia", "graphStudio", "network", "pageExceptions")}, indent=1))
    return 0 if not failed else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("outdir", type=Path)
    ap.add_argument("--preview", choices=("on", "off"), default="on")
    ap.add_argument("--expect-release")
    ap.add_argument("--label", default="staging")
    a = ap.parse_args()
    sys.exit(asyncio.run(run(a.url, a.outdir, a.preview, a.expect_release, a.label)))
