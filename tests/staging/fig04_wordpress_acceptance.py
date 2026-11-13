"""SC-FIG-04 MapLibre geospatial figures against a live Lab WordPress staging site.

Opens the real Lab page and Graph Studio in headless Chrome (WebGL from SwiftShader), feeds map-view
packages through the figure-bundle renderer's `sc-lab:figure-bundle:render` event and drives the map
controls: layer selection, legend, time steps, side-by-side comparison, then the refusals (edited SI
object, restricted licence, Earth-observation layer, wrong registered hash). Every network request is
recorded: only same-origin plugin files and blob: are allowed, and MapLibre itself must request nothing.

    python tests/staging/fig04_wordpress_acceptance.py http://127.0.0.1:18190/lab/ <out dir>
        [--expect-release 0.163.1.8] [--label staging] [--package DIR]

--package DIR renders an externally produced package (the Workbench MapLibre adapter's bundle and
view for the same SI package); DIR holds the files plus EXPECTED.json {"bundleSha256"}.
Nothing is posted to the site.
"""
import argparse
import asyncio
import base64
import json
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

import websockets

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fig02a_wordpress_acceptance import GRAPH_STUDIO_STATE, Cdp, _chrome, finish, network_checks  # noqa: E402
from figure_bundle_wordpress_acceptance import external_package  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "fig04-wexford"
OUTPUT = "[data-figure-bundle-renderer] .sc-lab-fig02a-output"

STATE = r"""
(() => {
  const out = document.querySelector('%s');
  const card = out && out.querySelector('.sc-lab-figure-bundle-card');
  const refusal = out && out.querySelector('[data-figure-bundle-state="refused"]');
  if (!card) { return {state: refusal ? 'refused' : 'none', reasons: refusal ? refusal.textContent.slice(0, 600) : ''}; }
  const slot = card.querySelector('[data-view-state]');
  const legend = card.querySelector('.sc-lab-fig04-legend');
  const table = card.querySelector('details:not([data-comparison-table]) table');
  const ctable = card.querySelector('[data-comparison-table] table');
  return {
    state: card.getAttribute('data-figure-bundle-state'), bundleSha256: card.getAttribute('data-bundle-sha256'),
    view: slot && slot.getAttribute('data-view-state'), map: slot && slot.getAttribute('data-map-state'),
    mapError: slot && slot.getAttribute('data-map-error'), requests: slot && slot.getAttribute('data-map-requests'),
    step: slot && slot.getAttribute('data-time-step'), layers: slot && slot.getAttribute('data-layers-visible'),
    compare: slot && slot.getAttribute('data-compare'), compareMap: slot && slot.getAttribute('data-compare-map'),
    canvases: card.querySelectorAll('canvas.maplibregl-canvas').length,
    region: !!card.querySelector('[role=region][aria-label^="Interactive map"]'),
    legendClasses: legend ? Array.from(legend.querySelectorAll('[data-legend-layer="field-soc"] li')).map(li => li.textContent) : [],
    heatNote: legend ? (legend.querySelector('[data-legend-layer="nitrate-heat"]') || {}).textContent || '' : '',
    tableRows: table ? table.querySelectorAll('tbody tr').length : 0,
    tableHeaders: table ? Array.from(table.querySelectorAll('thead th')).map(th => th.textContent) : [],
    compareRows: ctable ? ctable.querySelectorAll('tbody tr').length : 0,
    calc: (card.querySelector('.sc-lab-fig04-calculations') || {}).textContent || '',
    attribution: (card.querySelector('[data-map-attribution]') || {}).textContent || '',
    evidence: (card.querySelector('.sc-lab-fig02a-evidence') || {textContent: ''}).textContent,
    releaseState: card.getAttribute('data-release-state'),
    linksOrFrames: card.querySelectorAll('a[href^="http"], iframe, object, embed').length,
  };
})()
""" % OUTPUT


def fixture(name, mutate=None):
    data = (FIXTURES / name).read_bytes()
    return {"name": name, "b64": base64.b64encode(mutate(data) if mutate else data).decode()}


def repack(mutate_view=None, mutate_bundle=None):
    """A mutated view re-hashed into its bundle (canonical JSON hash), so only the deeper checks can refuse it."""
    import hashlib
    view = json.loads((FIXTURES / "wexford.map-view.json").read_text())
    bundle = json.loads((FIXTURES / "wexford.bundle.json").read_text())
    if mutate_view:
        mutate_view(view)
    if mutate_bundle:
        mutate_bundle(bundle)
    text = json.dumps(view, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    sha = hashlib.sha256(text.encode()).hexdigest()
    bundle["artifacts"][0]["sha256"] = sha
    bundle["rendering"]["visualizationSpecSha256"] = sha
    return [{"name": "b.json", "b64": base64.b64encode(json.dumps(bundle).encode()).decode()},
            {"name": "v.json", "b64": base64.b64encode(text.encode()).decode()}]


async def render(cdp, package, expected=None, wait_map=True):
    await cdp.js(f"document.querySelector('{OUTPUT}').textContent = ''")
    await cdp.js("""(() => { const files = %s.map(f => ({name: f.name, bytes: Uint8Array.from(atob(f.b64), c => c.charCodeAt(0))}));
        document.dispatchEvent(new CustomEvent('sc-lab:figure-bundle:render', {detail: {files, expectedBundleSha256: %s}})); })()"""
                 % (json.dumps(package), json.dumps(expected)))
    await cdp.wait_for(f"!!document.querySelector('{OUTPUT} [data-figure-bundle-state]')", 60)
    if wait_map:
        await cdp.wait_for(f"(() => {{ const s = document.querySelector('{OUTPUT} [data-map-state]'); return !s || s.getAttribute('data-map-state') !== 'loading'; }})()", 60)
    await asyncio.sleep(1.0)
    return await cdp.js(STATE)


async def act(cdp, script, settle=0.6):
    await cdp.js(f"(() => {{ const slot = document.querySelector('{OUTPUT} [data-view-state]'); {script} }})()")
    await asyncio.sleep(settle)
    return await cdp.js(STATE)


async def shot(cdp, outdir, name):
    clip = await cdp.js("""(() => { const r = document.querySelector('[data-figure-bundle-renderer]').getBoundingClientRect();
        return {x: r.left + scrollX, y: r.top + scrollY, width: r.width, height: Math.min(r.height, 2600), scale: 1}; })()""")
    img = await cdp.call("Page.captureScreenshot", format="png", clip=clip, captureBeyondViewport=True)
    (outdir / name).write_bytes(base64.b64decode(img["data"]))


async def run(url, outdir, expect_release=None, label="staging", package_dir=None):
    outdir.mkdir(parents=True, exist_ok=True)
    origin = "{0.scheme}://{0.netloc}".format(urlparse(url))
    port = 9336
    profile = tempfile.mkdtemp(prefix="fig04-cdp-")
    proc = subprocess.Popen([_chrome(), "--headless=new", "--no-first-run", "--hide-scrollbars", "--enable-unsafe-swiftshader",
                             "--use-angle=swiftshader", f"--remote-debugging-port={port}", f"--user-data-dir={profile}",
                             "--window-size=1280,1800", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
            for d in ("Network.enable", "Page.enable", "Runtime.enable", "Log.enable"):
                await cdp.call(d)
            report["chrome"] = (await cdp.call("Browser.getVersion")).get("product")
            await cdp.call("Page.navigate", url=url)
            check("page.loaded", await cdp.wait_for("document.readyState === 'complete'", 90))
            integrity = json.loads(await cdp.js("fetch('/wp-json/sc-lab/v1/runtime/v02632/health', {credentials: 'omit'}).then(r => r.text())") or "{}")
            report["integrity"] = {k: integrity.get(k) for k in ("ok", "state", "releaseVersion", "partialInstallRisk")}
            check("lab.integrityVerified", integrity.get("ok") is True and integrity.get("state") == "verified"
                  and (expect_release is None or integrity.get("releaseVersion") == expect_release), report["integrity"])
            health = json.loads(await cdp.js("fetch('/wp-json/sc-lab/v1/graph-studio/figure-bundle-renderer/health', {credentials: 'omit'}).then(r => r.text())") or "{}")
            report["health"] = health
            f4 = health.get("fig04") or {}
            check("health.fig04Served", f4.get("served") is True and f4.get("maplibreSha256Verified") is True
                  and f4.get("approvedTileProviders") == [] and f4.get("evalUsed") is False
                  and "application/vnd.sc.maplibre-view.v1+json" in (health.get("renderers") or {}), f4)
            await asyncio.sleep(2)
            cfg = json.loads(await cdp.js("JSON.stringify({r: window.SCLabFigureBundleRendererConfig || null, m: window.SCLabMapLibreFIG04Config || null, v: window.maplibregl && maplibregl.getVersion()})") or "{}")
            report["config"] = cfg
            check("config.maplibre", (cfg.get("r") or {}).get("maplibre") is True and cfg.get("v") == "5.24.0"
                  and str((cfg.get("m") or {}).get("workerIntegrity", "")).startswith("sha384-")
                  and str((cfg.get("m") or {}).get("workerUrl", "")).startswith(origin), cfg)
            await cdp.js("""(() => { const b = document.querySelector('[data-lab-module-button="graph-studio"]'); if (b) { b.click(); } })()""")
            mounted = await cdp.wait_for("!!document.querySelector('[data-figure-bundle-renderer]')", 60)
            report["graphStudio"] = await cdp.js(GRAPH_STUDIO_STATE)
            inside = await cdp.js("!!document.querySelector('[data-figure-bundle-renderer]').closest('[data-lab-module=\"graph-studio\"]')")
            check("viewer.mountedInGraphStudio", mounted and inside)

            # 1. The Lab fixture (SI-normalised synthetic Wexford): draw and drive every control.
            src = json.loads((FIXTURES / "SOURCE.json").read_text())
            pkg = [fixture("wexford.bundle.json"), fixture("wexford.map-view.json")]
            s = await render(cdp, pkg, src["files"]["wexford.bundle.json"])
            report["cases"]["wexford"] = s
            check("map.rendered", s["state"] == "rendered" and s["view"] == "rendered-maplibre" and s["map"] == "ready"
                  and s["canvases"] == 1 and s["region"] and s["bundleSha256"] == src["files"]["wexford.bundle.json"], s)
            check("map.noMapLibreRequests", s["requests"] == "0", s["requests"])
            check("legend.classesWithUnits", s["legendClasses"] == ["< 26 g kg-1", "26 to < 29 g kg-1", "29 to < 32 g kg-1", "≥ 32 g kg-1", "not reported"], s["legendClasses"])
            check("legend.heatMeaning", "not interpolated values" in s["heatNote"] and "modelled" in s["heatNote"], s["heatNote"])
            check("table.everyObjectWithUncertainty", s["tableRows"] == 56 and any("± standard error" in h for h in s["tableHeaders"])
                  and "SI digest" in s["tableHeaders"] and "Licence" in s["tableHeaders"], s["tableHeaders"])
            check("calc.uncertaintyShown", "g kg-1 yr-1 (standard error)" in s["calc"], s["calc"])
            check("attribution.noBasemap", "No basemap or imagery" in s["attribution"], s["attribution"])
            check("evidence.modelled", "Modelled" in s["evidence"] and s["releaseState"] == "none", s["evidence"])
            await shot(cdp, outdir, f"{label}-fig04-map.png")
            last = s["step"]
            t = await act(cdp, "slot.querySelector('[data-time-prev]').click();")
            t2 = await act(cdp, "const r = slot.querySelector('[data-time-range]'); r.value = '0'; r.dispatchEvent(new Event('input'));")
            check("time.controls", last.startswith("2026-11-01") and t["step"].startswith("2026-08-01") and t2["step"].startswith("2026-02-01"), [last, t["step"], t2["step"]])
            l1 = await act(cdp, "slot.querySelector('[data-layer-toggle=\"nitrate-heat\"]').click();")
            l2 = await act(cdp, "slot.querySelector('[data-layer-toggle=\"nitrate-heat\"]').click();")
            check("layers.toggle", l1["layers"] == "field-soc,nitrate-sites" and l2["layers"] == "field-soc,nitrate-heat,nitrate-sites", [l1["layers"], l2["layers"]])
            c1 = await act(cdp, "slot.querySelector('[data-compare-toggle]').click();", 0.2)
            await cdp.wait_for(f"(() => {{ const s = document.querySelector('{OUTPUT} [data-view-state]'); return s.getAttribute('data-compare-map') === 'ready'; }})()", 60)
            c1 = await cdp.js(STATE)
            check("comparison.sideBySide", c1["compare"] == "on" and c1["compareMap"] == "ready" and c1["canvases"] == 2 and c1["compareRows"] == 6, c1)
            await shot(cdp, outdir, f"{label}-fig04-compare.png")
            c2 = await act(cdp, "slot.querySelector('[data-compare-toggle]').click();")
            check("comparison.off", c2["compare"] == "off" and c2["canvases"] == 1, c2)
            check("map.stillNoMapLibreRequests", c2["requests"] == "0" and not c2["mapError"], [c2["requests"], c2["mapError"]])

            # 2. The Workbench adapter's output for the same SI package (SI -> Workbench -> Lab).
            if package_dir:
                package, expected = external_package(package_dir)
                e = await render(cdp, package, expected)
                report["cases"]["workbench-package"] = e
                check("workbench.rendered", e["state"] == "rendered" and e["view"] == "rendered-maplibre" and e["map"] == "ready"
                      and e["bundleSha256"] == expected and e["tableRows"] == 56 and e["requests"] == "0", e)
                await shot(cdp, outdir, f"{label}-fig04-workbench.png")

            # 3. Refusals: nothing is drawn.
            refusals = {
                "edited-si-object": (repack(lambda v: v["objects"][2]["properties"].update(soc=50.0)), None, "Site Intelligence digest"),
                "restricted-licence": (repack(None, lambda b: b["sourceRefs"][1].update(licenceStatus="restricted")), None, "not verified-for-use"),
                "sentinel-2-layer": (repack(lambda v: v.update(rasterLayers=[{"id": "s2", "provider": "copernicus-sentinel-2-l2a"}])), None, "not approved"),
                "wrong-registered-hash": (pkg, "0" * 64, "registered hash"),
                "promoted-to-observed": (repack(lambda v: v["objects"][0]["properties"].update(evidence_class="observed")), None, "no promotion to observed"),
            }
            for name, (package, expected, needle) in refusals.items():
                r = await render(cdp, package, expected, wait_map=False)
                report["cases"][name] = r
                check(f"refused.{name}", r["state"] == "refused" and needle in r.get("reasons", ""), r)
            await asyncio.sleep(1)
            network_checks(cdp, check, report, origin)
            urls = [ev["params"]["request"]["url"] for ev in cdp.events if ev["method"] == "Network.requestWillBeSent"]
            report["network"]["maplibreFiles"] = sorted({u.split("?")[0].replace(origin, "") for u in urls if "maplibre" in u})
            check("network.noRemoteRequests", not report["network"]["remote"], report["network"]["remote"])
            check("network.workerFetchedSameOrigin", any(u.endswith("maplibre-gl-csp-worker.js") for u in report["network"]["maplibreFiles"])
                  and any(u.startswith("blob:") for u in urls), report["network"]["maplibreFiles"])
            check("network.noTiles", not any("/tiles/" in u or "{z}" in u for u in urls))
            errors = [ev["params"]["entry"]["text"] for ev in cdp.events if ev["method"] == "Log.entryAdded" and ev["params"]["entry"]["level"] == "error"]
            report["consoleErrors"] = errors[:10]
            failed = sorted({(ev["params"]["response"]["status"], urlparse(ev["params"]["response"]["url"]).path)
                             for ev in cdp.events if ev["method"] == "Network.responseReceived" and ev["params"]["response"]["status"] >= 400})
            report["network"]["httpErrors"] = [f"{c} {p}" for c, p in failed]
            # Lab's own backend routes may answer 503 on a staging site without a Lab backend; no map file may fail.
            check("network.mapFilesServed", not [p for _c, p in failed if "maplibre" in p or "figure-bundle" in p], report["network"]["httpErrors"])
            pump.cancel()
    finally:
        proc.terminate()
        proc.wait(10)
        shutil.rmtree(profile, ignore_errors=True)
    report["previewMode"] = "fig04-maplibre"
    return finish(report, outdir, label + "-fig04")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("outdir", type=Path)
    ap.add_argument("--expect-release")
    ap.add_argument("--label", default="staging")
    ap.add_argument("--package", type=Path)
    a = ap.parse_args()
    sys.exit(asyncio.run(run(a.url, a.outdir, a.expect_release, a.label, a.package)))
