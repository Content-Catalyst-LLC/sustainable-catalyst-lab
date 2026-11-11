"""SC-FIG-02B Vega-Lite views and verified SVG export: acceptance against a live Lab WordPress staging site.

Reuses the FIG-02A DevTools driver and the SC-FIG-01 render event. Opens the real Lab page and Graph
Studio with both switches on, renders the synthetic FIG-02B packages (tests/fixtures/fig02b-vega-lite),
exports SVG from the live views through the page's own export buttons, re-verifies the exported bytes
and receipts here (Python), feeds the SVG back as a static view of a revised bundle, checks refusals,
and records every network request.

    python tests/staging/fig02b_wordpress_acceptance.py http://127.0.0.1:18190/lab/ <out dir>
        [--expect-release 0.163.1.6] [--label staging]

Nothing is posted to the site; exports stay in the browser and in <out dir>.
"""
import argparse
import asyncio
import base64
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

import websockets

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fig02a_wordpress_acceptance import Cdp, _chrome, finish, network_checks  # noqa: E402
from figure_bundle_wordpress_acceptance import STATE  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "fig02b-vega-lite"
GENERIC = ROOT / "tests" / "fixtures" / "figure-bundle-generic"
SVG_NS = "{http://www.w3.org/2000/svg}"

FIG02B_STATE = r"""
(() => {
  const card = document.querySelector('[data-figure-bundle-renderer] .sc-lab-figure-bundle-card');
  const out = document.querySelector('[data-figure-bundle-renderer] .sc-lab-fig02a-output');
  if (!card) { return {reasons: out ? out.textContent.slice(0, 600) : ''}; }
  const vl = Array.from(card.querySelectorAll('[data-view-state="rendered-vega-lite"]'));
  const text = vl.map(s => Array.from(s.querySelectorAll('.sc-lab-fig02b-plot svg text')).map(t => t.textContent).join(' | '));
  return {
    vegaReady: vl.map(s => s.getAttribute('data-vega-view')),
    vegaPaths: vl.map(s => s.querySelectorAll('.sc-lab-fig02b-plot svg path').length),
    vegaText: text,
    viewTables: vl.map(s => { const t = s.querySelector('table[data-view-table]'); return t && {
      caption: !!t.querySelector('caption'), rows: t.querySelectorAll('tbody tr').length,
      heads: Array.from(t.querySelectorAll('th[scope="col"]')).map(h => h.textContent),
      notReported: Array.from(t.querySelectorAll('td')).filter(c => c.textContent === 'not reported').length}; }),
    uncertainty: Array.from(card.querySelectorAll('.sc-lab-fig02b-uncertainty')).map(n => n.textContent),
    dataset: Array.from(card.querySelectorAll('.sc-lab-fig02b-dataset')).map(n => n.textContent),
    exportButtons: card.querySelectorAll('.sc-lab-fig02b-export-button').length,
    staticSvg: Array.from(card.querySelectorAll('[data-view-state="static-svg"] img')).map(i => !!(/^blob:/.test(i.src) && i.complete && i.naturalWidth > 0)),
  };
})()
"""

EXPORT_ALL = r"""
(async () => {
  const card = document.querySelector('[data-figure-bundle-renderer] .sc-lab-figure-bundle-card');
  const out = [];
  for (const btn of Array.from(card.querySelectorAll('.sc-lab-fig02b-export-button'))) {
    const slot = btn.closest('[data-view-state]');
    slot.removeAttribute('data-export-state');
    btn.click();
    for (let i = 0; i < 200 && !slot.getAttribute('data-export-state'); i++) { await new Promise(r => setTimeout(r, 100)); }
    const links = Array.from(slot.querySelectorAll('a.sc-lab-fig02b-download[download]'));
    const svgLink = links.find(a => /\.svg$/.test(a.getAttribute('download')));
    const recLink = links.find(a => /\.json$/.test(a.getAttribute('download')));
    const b64 = async (a) => { const buf = new Uint8Array(await (await fetch(a.href)).arrayBuffer());
      let s = ''; for (let i = 0; i < buf.length; i += 0x8000) { s += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000)); } return btoa(s); };
    out.push({view: slot.getAttribute('data-view-state'), state: slot.getAttribute('data-export-state'),
              sha256: slot.getAttribute('data-export-sha256'), files: links.map(a => a.getAttribute('download')),
              svg: svgLink ? await b64(svgLink) : null, receipt: recLink ? atob(await b64(recLink)) : null});
  }
  return JSON.stringify(out);
})()
"""


def packed(directory, *names):
    return [{"name": n, "b64": base64.b64encode((directory / n).read_bytes()).decode()} for n in names]


def blob(name, data):
    return {"name": name, "b64": base64.b64encode(data).decode()}


async def render(cdp, package, expected=None):
    await cdp.js("document.querySelector('[data-figure-bundle-renderer] .sc-lab-fig02a-output').textContent = ''")
    await cdp.js("""(() => { const files = %s.map(f => ({name: f.name, bytes: Uint8Array.from(atob(f.b64), c => c.charCodeAt(0))}));
        document.dispatchEvent(new CustomEvent('sc-lab:figure-bundle:render', {detail: {files, expectedBundleSha256: %s}})); })()"""
                 % (json.dumps(package), json.dumps(expected)))
    await cdp.wait_for("!!document.querySelector('[data-figure-bundle-renderer] [data-figure-bundle-state]')", 60)
    await cdp.wait_for("""(() => { const c = document.querySelector('[data-figure-bundle-renderer] .sc-lab-figure-bundle-card');
        return !c || Array.from(c.querySelectorAll('[data-view-state="rendered-vega-lite"]')).every(s => s.getAttribute('data-vega-view')); })()""", 60)
    await asyncio.sleep(1.0)
    state = await cdp.js(STATE)
    state.update(await cdp.js(FIG02B_STATE))
    return state


def verify_export(item, bundle_sha256):
    """Independent (Python) re-verification of one exported SVG and its receipt."""
    data = base64.b64decode(item["svg"])
    receipt = json.loads(item["receipt"])
    tree = ET.fromstring(data)
    tags = {el.tag.replace(SVG_NS, "") for el in tree.iter()}
    meta = tree.find(f"{SVG_NS}metadata")
    prov = json.loads(meta.text) if meta is not None and meta.text else {}
    return {
        "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
        "receiptMatches": receipt.get("sha256") == hashlib.sha256(data).hexdigest() == item["sha256"] and receipt.get("bytes") == len(data),
        "bundleBound": receipt.get("bundleSha256") == bundle_sha256,
        "noActiveContent": not ({"script", "foreignObject", "image", "a", "iframe"} & tags) and b"javascript:" not in data and b" on" not in data.lower().replace(b" one", b""),
        "provenance": {k: prov.get(k) for k in ("schema", "figureId", "evidenceClass", "reproducibility", "viewArtifactSha256")},
        "datasetSha256": (prov.get("dataset") or {}).get("sha256"),
        "renderer": receipt.get("renderer", {}).get("name"),
        "artifactEntry": receipt.get("artifactEntry"),
        "data": data,
    }


async def run(url, outdir, expect_release=None, label="staging"):
    outdir.mkdir(parents=True, exist_ok=True)
    origin = "{0.scheme}://{0.netloc}".format(urlparse(url))
    port = 9335
    profile = tempfile.mkdtemp(prefix="fig02b-cdp-")
    proc = subprocess.Popen([_chrome(), "--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars",
                             f"--remote-debugging-port={port}", f"--user-data-dir={profile}",
                             "--window-size=1280,1800", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    report = {"url": url, "expectRelease": expect_release, "checks": {}, "cases": {}, "exports": {}, "network": {}}

    def check(name, cond, detail=None):
        report["checks"][name] = {"ok": bool(cond), "detail": detail}

    async def shot(name):
        clip = await cdp.js("""(() => { const r = document.querySelector('[data-figure-bundle-renderer]').getBoundingClientRect();
            return {x: r.left + scrollX, y: r.top + scrollY, width: r.width, height: Math.min(r.height, 4000), scale: 1}; })()""")
        img = await cdp.call("Page.captureScreenshot", format="png", clip=clip, captureBeyondViewport=True)
        (outdir / f"{label}-fig02b-{name}.png").write_bytes(base64.b64decode(img["data"]))

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
            integrity = json.loads(await cdp.js("fetch('/wp-json/sc-lab/v1/runtime/v02632/health', {credentials: 'omit'}).then(r => r.text())") or "{}")
            report["integrity"] = {k: integrity.get(k) for k in ("ok", "state", "releaseVersion", "partialInstallRisk")}
            check("lab.integrityVerified", integrity.get("ok") is True and integrity.get("state") == "verified"
                  and (expect_release is None or integrity.get("releaseVersion") == expect_release), report["integrity"])
            health = json.loads(await cdp.js("fetch('/wp-json/sc-lab/v1/graph-studio/figure-bundle-renderer/health', {credentials: 'omit'}).then(r => r.text())") or "{}")
            report["health"] = health
            f2 = health.get("fig02b") or {}
            check("health.fig02bServedVerified", health.get("enabled") is True and f2.get("served") is True and f2.get("vegaSha256Verified") is True
                  and f2.get("evalUsed") is False and health.get("publicationPerformed") is False and health.get("cdnUsed") is False, f2)
            await asyncio.sleep(2)
            cfg = json.loads(await cdp.js("JSON.stringify(window.SCLabFigureBundleRendererConfig || null)") or "null")
            check("config.vegaLite", bool(cfg) and cfg.get("vegaLite") is True, cfg)
            versions = await cdp.js("""JSON.stringify({vega: window.vega && vega.version, vegaLite: window.vegaLite && vegaLite.version,
                interpreter: window.vegaInterpreter && vegaInterpreter.version, plotly: window.Plotly && Plotly.version,
                fig02b: window.SCLabVegaLiteFIG02B && SCLabVegaLiteFIG02B.version,
                runtime: window.SCLabVegaLiteFIG02B ? SCLabVegaLiteFIG02B.runtimeErrors() : ['not loaded'],
                scripts: Array.from(document.scripts).map(s => s.src).filter(s => /vega|plotly|fig02b/.test(s))})""")
            versions = json.loads(versions)
            report["libraries"] = versions
            check("libraries.pinnedAndLocal", versions["vega"] == "6.4.0" and versions["vegaLite"] == "6.5.0" and versions["interpreter"] == "2.3.2"
                  and versions["plotly"] == "3.3.1" and not versions["runtime"] and versions["scripts"]
                  and all(s.startswith(origin + "/wp-content/plugins/sustainable-catalyst-lab/") for s in versions["scripts"]), versions)
            await cdp.js("""(() => { const b = document.querySelector('[data-lab-module-button="graph-studio"]'); if (b) { b.click(); } })()""")
            check("viewer.mounted", await cdp.wait_for("!!document.querySelector('[data-figure-bundle-renderer]')", 60))

            source = json.loads((FIXTURES / "SOURCE.json").read_text())
            erw_bundle_sha = source["files"]["erw.bundle.json"]

            # ERW: live Vega-Lite view, table, export from the page, Python re-verification.
            st = await render(cdp, packed(FIXTURES, "erw.bundle.json", "erw.vega-lite.json"), erw_bundle_sha)
            report["cases"]["erw"] = st
            heads = (st["viewTables"] or [{}])[0].get("heads", [])
            check("case.erw", st["state"] == "rendered" and st["views"] == ["rendered-vega-lite"] and st["vegaReady"] == ["ready"]
                  and st["vegaPaths"][0] > 4 and st["bundleSha256"] == erw_bundle_sha and st["evidenceClass"] == "modelled"
                  and "Cumulative CO2 uptake (t CO2 ha-1)" in st["vegaText"][0] and "literature-derived" in st["vegaText"][0]
                  and "modelled" in st["vegaText"][0] and "not publication-approved" in st["reviewText"], st)
            check("case.erw.accessibleTable", st["viewTables"][0]["caption"] and st["viewTables"][0]["rows"] == 20
                  and "Evidence class" in heads and any("(t CO2 ha-1)" in h for h in heads)
                  and st["uncertainty"] and st["uncertainty"][0].startswith("Uncertainty (range)") and st["linksOrFrames"] == 0, st["viewTables"])
            await shot("erw")
            exports = json.loads(await cdp.js(EXPORT_ALL))
            v = verify_export(exports[0], erw_bundle_sha)
            report["exports"]["erw"] = {k: v[k] for k in v if k != "data"}
            check("export.erw", exports[0]["state"] == "verified" and v["receiptMatches"] and v["bundleBound"] and v["noActiveContent"]
                  and v["provenance"]["schema"] == "sc.figure-svg-provenance.v1" and v["provenance"]["evidenceClass"] == "modelled"
                  and v["datasetSha256"] == json.loads((FIXTURES / "erw.vega-lite.json").read_text())["usermeta"]["sc"]["datasetSha256"], report["exports"]["erw"])
            (outdir / f"{label}-fig02b-erw.svg").write_bytes(v["data"])
            (outdir / f"{label}-fig02b-erw.receipt.json").write_text(exports[0]["receipt"])
            again = json.loads(await cdp.js(EXPORT_ALL))
            check("export.erw.repeatable", again[0]["sha256"] == exports[0]["sha256"], [again[0]["sha256"], exports[0]["sha256"]])

            # Round trip: the exported SVG as a verified static view of the next bundle revision.
            rev = json.loads((FIXTURES / "erw.bundle.json").read_text())
            rev["artifacts"].append(v["artifactEntry"])
            st = await render(cdp, [blob("erw.rev.bundle.json", json.dumps(rev).encode()), *packed(FIXTURES, "erw.vega-lite.json"),
                                    blob(v["artifactEntry"]["artifactRef"], v["data"])])
            report["cases"]["erw-roundtrip"] = st
            check("case.erw-roundtrip", st["state"] == "rendered" and st["views"] == ["rendered-vega-lite", "static-svg"] and st["staticSvg"] == [True], st)
            await shot("erw-roundtrip")

            # Metrics: gaps and no uncertainty.
            st = await render(cdp, packed(FIXTURES, "metrics.bundle.json", "metrics.vega-lite.json"), source["files"]["metrics.bundle.json"])
            report["cases"]["metrics"] = st
            check("case.metrics", st["state"] == "rendered" and st["vegaReady"] == ["ready"] and st["evidenceClass"] == "hypothetical"
                  and st["viewTables"][0]["notReported"] == 3 and st["uncertainty"][0].startswith("Uncertainty: none reported"), st)
            await shot("metrics")

            # Combined: Plotly and Vega-Lite side by side, both exported.
            st = await render(cdp, [*packed(FIXTURES, "combined.bundle.json", "erw.vega-lite.json"), *packed(GENERIC, "points.plotly.json")])
            report["cases"]["combined"] = st
            check("case.combined", st["state"] == "rendered" and st["views"] == ["rendered-vega-lite", "rendered-plotly"] and st["svgDrawn"] and st["exportButtons"] == 2, st)
            exports = json.loads(await cdp.js(EXPORT_ALL))
            comb_sha = hashlib.sha256((FIXTURES / "combined.bundle.json").read_bytes()).hexdigest()
            verified = [verify_export(x, comb_sha) for x in exports]
            report["exports"]["combined"] = [{k: e[k] for k in e if k != "data"} for e in verified]
            check("export.combined", sorted(e["renderer"] for e in verified) == ["plotly.js", "vega-lite"]
                  and all(x["state"] == "verified" for x in exports) and all(e["receiptMatches"] and e["noActiveContent"] for e in verified),
                  report["exports"]["combined"])
            await shot("combined")

            # Refusals on the live page.
            erw_view = json.loads((FIXTURES / "erw.vega-lite.json").read_text())
            remote = dict(erw_view, data={"url": "https://example.org/x.csv"})
            st = await render(cdp, [*packed(FIXTURES, "erw.bundle.json"), blob("erw.vega-lite.json", json.dumps(remote).encode())])
            report["cases"]["refused-remote-data"] = st
            check("case.refused-remote-data", st["state"] == "refused", st)
            bad_svg = b'<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"><rect width="1" height="1"/></svg>'
            b2 = json.loads((FIXTURES / "erw.bundle.json").read_text())
            b2["artifacts"].append({"format": "svg", "artifactRef": "x.svg", "sha256": hashlib.sha256(bad_svg).hexdigest(),
                                    "mediaType": "image/svg+xml", "status": "local-review"})
            st = await render(cdp, [blob("b.json", json.dumps(b2).encode()), *packed(FIXTURES, "erw.vega-lite.json"), blob("x.svg", bad_svg)])
            report["cases"]["refused-svg-handler"] = st
            check("case.refused-svg-handler", st["state"] == "refused", st)
            st = await render(cdp, packed(GENERIC, "mixed.bundle.json", "points.plotly.json", "static.png", "view.vega-lite.json"))
            report["cases"]["generic-vega-lite-without-usermeta"] = st
            check("case.generic-vega-lite-without-usermeta", st["state"] == "refused" and "usermeta" in (st.get("reasons") or ""), st)

            await asyncio.sleep(1)
            network_checks(cdp, check, report, origin)
            check("network.noRemoteRequests", not report["network"]["remote"], report["network"]["remote"])
            pump.cancel()
    finally:
        proc.terminate()
        proc.wait(10)
        shutil.rmtree(profile, ignore_errors=True)
    report["previewMode"] = "fig02b"
    return finish(report, outdir, label + "-fig02b")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("outdir", type=Path)
    ap.add_argument("--expect-release")
    ap.add_argument("--label", default="staging")
    a = ap.parse_args()
    sys.exit(asyncio.run(run(a.url, a.outdir, a.expect_release, a.label)))
