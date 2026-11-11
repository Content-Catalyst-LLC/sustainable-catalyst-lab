"""SC-FIG-01 generic figure-bundle renderer acceptance against a live Lab WordPress staging site.

Reuses the FIG-02A DevTools driver. Opens the real Lab page and Graph Studio, then feeds the
synthetic generic packages (tests/fixtures/figure-bundle-generic) through the module's
`sc-lab:figure-bundle:render` event and checks view states, hashes, labels, accessibility semantics
and every network request the page makes.

    python tests/staging/figure_bundle_wordpress_acceptance.py http://127.0.0.1:18190/lab/ <out dir>
        [--expect-release 0.163.1.5] [--label staging|production] [--package DIR]

--package renders an externally produced package (e.g. a Workspace notebook run's figure bundle)
as an extra case; DIR holds the files plus EXPECTED.json {"bundle", "bundleSha256"} naming the
registered bundle hash the renderer must verify.

Nothing is posted to the site.
"""
import argparse
import asyncio
import base64
import json
import subprocess
import sys
import shutil
import tempfile
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

import websockets

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fig02a_wordpress_acceptance import GRAPH_STUDIO_STATE, Cdp, _chrome, finish, network_checks  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "figure-bundle-generic"

STATE = r"""
(() => {
  const out = document.querySelector('[data-figure-bundle-renderer] .sc-lab-fig02a-output');
  const card = out && out.querySelector('.sc-lab-figure-bundle-card');
  const refused = !!(out && out.querySelector('[data-figure-bundle-state="refused"]'));
  if (!card) { return {state: refused ? 'refused' : 'none'}; }
  const views = Array.from(card.querySelectorAll('[data-view-state]')).map(v => v.getAttribute('data-view-state'));
  const plot = card.querySelector('.js-plotly-plot');
  const img = card.querySelector('img.sc-lab-figure-bundle-static');
  const tables = Array.from(card.querySelectorAll('.sc-lab-fig02a-tables table'));
  return {
    state: card.getAttribute('data-figure-bundle-state'),
    bundleSha256: card.getAttribute('data-bundle-sha256'),
    views,
    evidenceClass: (card.querySelector('.sc-lab-fig02a-evidence') || {getAttribute: () => null}).getAttribute('data-evidence-class'),
    reviewText: (card.querySelector('.sc-lab-fig02a-review') || {}).textContent || '',
    releaseText: (card.querySelector('.sc-lab-figure-bundle-release') || {}).textContent || '',
    releaseState: card.getAttribute('data-release-state'),
    svgDrawn: !!(plot && plot.querySelector('svg.main-svg')),
    plotRole: plot && plot.getAttribute('role'),
    pngBlob: !!(img && /^blob:/.test(img.src) && img.complete && img.naturalWidth > 0 && img.alt.length > 15),
    tablesHaveCaption: tables.every(t => !!t.querySelector('caption')),
    headersScoped: tables.every(t => Array.from(t.querySelectorAll('thead th')).every(th => th.getAttribute('scope') === 'col')),
    tableRows: card.querySelectorAll('.sc-lab-fig02a-tables tbody tr').length,
    limitations: card.querySelectorAll('.sc-lab-figure-bundle-limitations li').length,
    unavailable: card.querySelectorAll('.sc-lab-figure-bundle-unavailable').length,
    linksOrFrames: card.querySelectorAll('a[href], iframe, script, object, embed').length,
  };
})()
"""


def files(*names, mutate=None):
    out = []
    for n in names:
        data = (FIXTURES / n).read_bytes()
        if mutate and n in mutate:
            data = mutate[n](data)
        out.append({"name": n, "b64": base64.b64encode(data).decode()})
    return out


async def render(cdp, package, expected=None):
    await cdp.js("document.querySelector('[data-figure-bundle-renderer] .sc-lab-fig02a-output').textContent = ''")
    await cdp.js("""(() => { const files = %s.map(f => ({name: f.name, bytes: Uint8Array.from(atob(f.b64), c => c.charCodeAt(0))}));
        document.dispatchEvent(new CustomEvent('sc-lab:figure-bundle:render', {detail: {files, expectedBundleSha256: %s}})); })()"""
                 % (json.dumps(package), json.dumps(expected)))
    await cdp.wait_for("!!document.querySelector('[data-figure-bundle-renderer] [data-figure-bundle-state]')", 60)
    await asyncio.sleep(1.0)
    return await cdp.js(STATE)


def external_package(directory):
    expected = json.loads((directory / "EXPECTED.json").read_text())
    package = [{"name": f.name, "b64": base64.b64encode(f.read_bytes()).decode()}
               for f in sorted(directory.iterdir()) if f.is_file() and f.name != "EXPECTED.json"]
    return package, expected["bundleSha256"]


async def run(url, outdir, expect_release=None, label="staging", package_dir=None):
    outdir.mkdir(parents=True, exist_ok=True)
    origin = "{0.scheme}://{0.netloc}".format(urlparse(url))
    port = 9334
    profile = tempfile.mkdtemp(prefix="figbundle-cdp-")
    proc = subprocess.Popen([_chrome(), "--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars",
                             f"--remote-debugging-port={port}", f"--user-data-dir={profile}",
                             "--window-size=1280,1600", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    report = {"url": url, "expectRelease": expect_release, "checks": {}, "cases": {}, "network": {}}

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
            integrity = json.loads(await cdp.js("fetch('/wp-json/sc-lab/v1/runtime/v02632/health', {credentials: 'omit'})"
                                                ".then(r => r.text())") or "{}")
            report["integrity"] = {k: integrity.get(k) for k in ("ok", "state", "releaseVersion", "partialInstallRisk")}
            check("lab.integrityVerified", integrity.get("ok") is True and integrity.get("state") == "verified"
                  and (expect_release is None or integrity.get("releaseVersion") == expect_release), report["integrity"])
            health = json.loads(await cdp.js("fetch('/wp-json/sc-lab/v1/graph-studio/figure-bundle-renderer/health', {credentials: 'omit'})"
                                             ".then(r => r.text())") or "{}")
            report["health"] = health
            check("health.enabledAndBounded", health.get("enabled") is True and health.get("plotlyJsSha256Verified") is True
                  and health.get("publicationPerformed") is False and health.get("uploadPerformed") is False, health)
            await asyncio.sleep(2)
            cfg = json.loads(await cdp.js("JSON.stringify(window.SCLabFigureBundleRendererConfig || null)") or "null")
            check("config.typedEnabled", bool(cfg) and cfg.get("enabled") is True, cfg)
            check("plotly.version", await cdp.js("window.Plotly && Plotly.version") == "3.3.1")
            report["graphStudioOpenedVia"] = await cdp.js("""(() => { const b = document.querySelector('[data-lab-module-button="graph-studio"]');
                                     if (b) { b.click(); return 'button'; } return null; })()""")
            mounted = await cdp.wait_for("!!document.querySelector('[data-figure-bundle-renderer]')", 60)
            report["graphStudio"] = await cdp.js(GRAPH_STUDIO_STATE)
            where = await cdp.js("""(() => { const s = document.querySelector('[data-figure-bundle-renderer]'); return s && {
                graphStudio: !!s.closest('[data-lab-module="graph-studio"]'), count: document.querySelectorAll('[data-figure-bundle-renderer]').length,
                multiple: s.querySelector('input[type=file]').multiple, label: s.querySelector('input[type=file]').getAttribute('aria-label')}; })()""")
            check("viewer.mountedInGraphStudio", mounted and where and where["graphStudio"] and where["count"] == 1 and where["multiple"], where)

            source = json.loads((FIXTURES / "SOURCE.json").read_text())
            cases = {
                "points-pinned": (files("points.bundle.json", "points.plotly.json"), source["files"]["points.bundle.json"]),
                "mixed-views": (files("mixed.bundle.json", "points.plotly.json", "static.png", "view.vega-lite.json"), None),
                "bundle-only": (files("points.bundle.json"), None),
                "tampered-spec": (files("points.bundle.json", "points.plotly.json",
                                        mutate={"points.plotly.json": lambda b: b.replace(b"5.0,", b"5.1,", 1)}), None),
                "wrong-registered-hash": (files("points.bundle.json", "points.plotly.json"), "0" * 64),
                "promoted-to-observed": (files("points.bundle.json", "points.plotly.json", mutate={
                    "points.bundle.json": lambda b: b.replace(b'"evidenceClass": "literature-derived"', b'"evidenceClass": "observed"', 1)}), None),
            }
            if package_dir:
                cases["external-package"] = external_package(package_dir)
            for name, (package, expected) in cases.items():
                state = await render(cdp, package, expected)
                report["cases"][name] = state
                if name == "external-package":
                    ok = (state["state"] == "rendered" and state["views"] == ["rendered-plotly"] and state["svgDrawn"]
                          and state["bundleSha256"] == expected and state["plotRole"] == "img"
                          and state["releaseState"] == "none" and "Not released here" in state["releaseText"]
                          and "not release authority" in state["reviewText"] and state["linksOrFrames"] == 0)
                elif name == "points-pinned":
                    ok = (state["state"] == "rendered" and state["views"] == ["rendered-plotly"] and state["svgDrawn"]
                          and state["bundleSha256"] == expected and state["evidenceClass"] == "literature-derived"
                          and state["releaseState"] == "none" and "not release authority" in state["reviewText"]
                          and state["plotRole"] == "img"
                          and state["tableRows"] > 0 and state["tablesHaveCaption"] and state["headersScoped"]
                          and state["limitations"] > 0 and state["linksOrFrames"] == 0)
                elif name == "mixed-views" and (health.get("fig02b") or {}).get("served"):
                    # With FIG-02B on, a Vega-Lite view must carry usermeta.sc; this generic one does not.
                    ok = state["state"] == "refused"
                elif name == "mixed-views":
                    ok = (state["state"] == "rendered" and state["views"] == ["rendered-plotly", "static-png", "unsupported", "missing"]
                          and state["svgDrawn"] and state["pngBlob"] and state["unavailable"] == 2 and state["linksOrFrames"] == 0)
                elif name == "bundle-only":
                    ok = state["state"] == "metadata-only" and state["views"] == ["missing"] and not state["svgDrawn"]
                else:
                    ok = state["state"] == "refused"
                check(f"case.{name}", ok, state)
                if name in ("points-pinned", "mixed-views", "external-package"):
                    clip = await cdp.js("""(() => { const r = document.querySelector('[data-figure-bundle-renderer]').getBoundingClientRect();
                        return {x: r.left + scrollX, y: r.top + scrollY, width: r.width, height: Math.min(r.height, 3000), scale: 1}; })()""")
                    shot = await cdp.call("Page.captureScreenshot", format="png", clip=clip, captureBeyondViewport=True)
                    (outdir / f"{label}-figure-bundle-{name}.png").write_bytes(base64.b64decode(shot["data"]))
            await asyncio.sleep(1)
            network_checks(cdp, check, report, origin)
            check("network.noRemoteRequests", not report["network"]["remote"], report["network"]["remote"])
            pump.cancel()
    finally:
        proc.terminate()
        proc.wait(10)
        shutil.rmtree(profile, ignore_errors=True)
    report["previewMode"] = "figure-bundle"
    return finish(report, outdir, label + "-figure-bundle")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("outdir", type=Path)
    ap.add_argument("--expect-release")
    ap.add_argument("--label", default="staging")
    ap.add_argument("--package", type=Path)
    a = ap.parse_args()
    sys.exit(asyncio.run(run(a.url, a.outdir, a.expect_release, a.label, a.package)))
