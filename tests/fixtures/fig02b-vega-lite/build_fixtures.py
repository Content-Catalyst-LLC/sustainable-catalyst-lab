#!/usr/bin/env python3
"""FIG-02B synthetic fixtures (no scientific meaning). Re-running produces byte-identical files.

Hashes follow the Workbench/Workspace canonical JSON rule: json.dumps(value, sort_keys=True,
separators=(",", ":"), ensure_ascii=False) encoded as UTF-8. The Lab verifier recomputes them in the
browser from the files' own text, so these fixtures also cross-check Python and JavaScript hashing.

    erw.bundle.json + erw.vega-lite.json          SYNTHETIC enhanced-rock-weathering scenario (modelled band and
                                                  line, literature-derived comparison points with ranges)
    metrics.bundle.json + metrics.vega-lite.json  SYNTHETIC SDG-style indicator for three placeholder countries,
                                                  with missing years and no reported uncertainty
    combined.bundle.json                          one figure with the existing Plotly points view and a Vega-Lite view
"""
import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
GENERIC = HERE.parent / "figure-bundle-generic"
VL5 = "https://vega.github.io/schema/vega-lite/v5.json"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def bundle(figure_id, title, evidence, status, sources, calcs, interpretation, limitations, caption, alt, artifacts, reproducibility):
    return {
        "schema": "sc.figure-bundle.v1", "figureId": figure_id, "version": 1, "title": title,
        "project": {"projectRef": "fig02b-synthetic-ci", "ownerScope": "unbound-local", "environment": "local-review"},
        "publication": {"kind": "none", "target": "unassigned", "bindingStatus": "unbound"},
        "evidenceClass": evidence, "figureType": "evidence-chart", "sourceRefs": sources, "calculationRefs": calcs,
        "scientificContext": {"interpretation": interpretation, "limitations": limitations, "measurementStatus": status,
                              "claimIds": [], "doNotInfer": ["any scientific conclusion", "measured or certified carbon removal"]},
        "rendering": {"profileId": "sc-institutional-research-v1", "renderer": "vega-lite", "rendererVersion": "vega-lite 6.5.0; vega 6.4.0",
                      "caption": caption, "altText": alt, "palette": "colorblind-safe", "accessibilityReview": "pending",
                      "visualizationSpecSha256": artifacts[0]["sha256"]},
        "artifacts": artifacts,
        "provenance": {"authorityOwner": "lab", "sourceSnapshotIds": [s["sourceId"] for s in sources],
                       "generationRunId": "lab.fig02b-fixture-builder:" + artifacts[0]["sha256"][:24],
                       "generatedAt": "2026-11-11T00:00:00Z", "reproducibility": reproducibility},
        "review": {"scientific": "pending", "visual": "pending", "rights": "pending", "sourceIntegrity": "pending", "publication": "pending"},
    }


def vl_artifact(figure_id, view):
    h = sha(view)
    return {"format": "json", "artifactRef": f"sc://lab/fig02b/{figure_id}/{h}.json", "sha256": h,
            "mediaType": "application/vnd.vegalite.v5+json", "width": 720, "height": 420, "status": "local-review", "revision": 1}


def erw():
    rows = []
    for m in range(0, 49, 6):  # months since application, synthetic first-order uptake curves
        for scen, rate, k in (("basalt 40 t/ha (synthetic)", 2.4, 0.045), ("basalt 20 t/ha (synthetic)", 1.3, 0.05)):
            mid = round(rate * (1 - pow(2.718281828, -k * m)) * 4.0, 3)
            rows.append({"month": m, "cdr": mid, "lo": round(mid * 0.7, 3), "hi": round(mid * 1.3, 3),
                         "series": scen, "evidenceClass": "modelled"})
    for m, v, lo, hi, s in ((12, 1.1, 0.6, 1.6, "literature comparison A (synthetic)"), (36, 2.9, 1.9, 4.2, "literature comparison B (synthetic)")):
        rows.append({"month": m, "cdr": v, "lo": lo, "hi": hi, "series": s, "evidenceClass": "literature-derived"})
    data_sha = sha(rows)
    # One legend lists both evidence classes: dashed line = modelled, filled diamond = literature-derived.
    Y_TITLE = "Cumulative CO2 uptake (t CO2 ha-1)"
    EVIDENCE_DASH = {"domain": ["modelled", "literature-derived"], "range": [[6, 3], [1, 0]]}
    EVIDENCE_SHAPE = {"domain": ["modelled", "literature-derived"], "range": ["circle", "diamond"]}
    view = {
        "$schema": VL5, "width": 640, "height": 360,
        "title": "SYNTHETIC — enhanced rock weathering uptake scenario (not Wexford data)",
        "data": {"values": rows},
        "layer": [
            {"transform": [{"filter": {"field": "evidenceClass", "equal": "modelled"}}],
             "mark": {"type": "errorband", "opacity": 0.25},
             "encoding": {"x": {"field": "month", "type": "quantitative"}, "y": {"field": "lo", "type": "quantitative", "title": Y_TITLE},
                          "y2": {"field": "hi"}, "color": {"field": "series", "type": "nominal"}}},
            {"transform": [{"filter": {"field": "evidenceClass", "equal": "modelled"}}],
             "mark": {"type": "line"},
             "encoding": {"x": {"field": "month", "type": "quantitative"}, "y": {"field": "cdr", "type": "quantitative"},
                          "color": {"field": "series", "type": "nominal"},
                          "strokeDash": {"field": "evidenceClass", "type": "nominal", "scale": EVIDENCE_DASH,
                                         "legend": {"title": "Evidence class"}}}},
            {"transform": [{"filter": {"field": "evidenceClass", "equal": "literature-derived"}}],
             "mark": {"type": "errorbar", "ticks": True},
             "encoding": {"x": {"field": "month", "type": "quantitative"}, "y": {"field": "lo", "type": "quantitative", "title": Y_TITLE},
                          "y2": {"field": "hi"}}},
            {"transform": [{"filter": {"field": "evidenceClass", "equal": "literature-derived"}}],
             "mark": {"type": "point", "filled": True, "size": 70},
             "encoding": {"x": {"field": "month", "type": "quantitative"}, "y": {"field": "cdr", "type": "quantitative"},
                          "shape": {"field": "evidenceClass", "type": "nominal", "scale": EVIDENCE_SHAPE,
                                    "legend": {"title": "Evidence class"}},
                          "color": {"field": "series", "type": "nominal"}}},
        ],
        "usermeta": {"sc": {
            "profile": "sc-vega-lite-v1", "datasetId": "synthetic:erw-uptake-scenario-v1", "datasetSha256": data_sha,
            "evidenceField": "evidenceClass",
            "fields": {"month": {"label": "Months since application", "unit": "months"},
                       "cdr": {"label": "Cumulative CO2 uptake", "unit": "t CO2 ha-1"},
                       "lo": {"label": "Lower bound", "unit": "t CO2 ha-1"}, "hi": {"label": "Upper bound", "unit": "t CO2 ha-1"},
                       "series": {"label": "Series", "unit": "category"}, "evidenceClass": {"label": "Evidence class", "unit": "category"}},
            "uncertainty": {"kind": "range", "lowerField": "lo", "upperField": "hi",
                            "statement": "Synthetic ±30% scenario band for modelled series; reported min–max for the literature comparisons."}}},
    }
    art = vl_artifact("SYN-ERW-vega-lite", view)
    params = {"model": "first-order dissolution", "rates": [2.4, 1.3], "k": [0.045, 0.05], "fixture": True}
    b = bundle("SYN-ERW-vega-lite", "SYNTHETIC enhanced rock weathering uptake scenario with literature comparisons",
               "modelled", "computed-from-specified-inputs",
               [{"sourceId": "synthetic:erw-scenario-parameters-v1", "provider": "Sustainable Catalyst test fixture",
                 "identityStatus": "source-hash-verified", "qualityStatus": "not-applicable", "licenceStatus": "verified-for-use", "sha256": sha(params)},
                {"sourceId": "synthetic:literature-comparison-placeholder", "provider": "test fixture standing in for published literature",
                 "citationId": "SYNTHETIC-CITATION-1", "identityStatus": "source-identified", "qualityStatus": "pending", "licenceStatus": "pending"}],
               [{"system": "workbench", "runRef": "synthetic-fixture:erw-uptake-scenario-v1", "method": "first-order dissolution with synthetic parameters",
                 "outputSha256": data_sha, "assumptionRefs": ["synthetic:erw-scenario-parameters-v1"]}],
               "Synthetic modelled uptake curves with a scenario band beside two synthetic literature comparison points; exercises FIG-02B only.",
               ["Synthetic values with no scientific meaning", "Not Wexford measurements; no carbon removal is measured or certified"],
               "SYNTHETIC: modelled uptake scenarios (dashed, with band) and literature-style comparison points with ranges.",
               "Line chart of two synthetic modelled uptake scenarios over 48 months with shaded bands, and two synthetic comparison points with error bars.",
               [art], "synthetic-fixture-tested")
    return b, view


def metrics():
    rows = []
    base = {"Country A (synthetic)": 62.0, "Country B (synthetic)": 81.5, "Country C (synthetic)": 94.0}
    gaps = {("Country A (synthetic)", 2018), ("Country A (synthetic)", 2019), ("Country C (synthetic)", 2021)}
    for c, v0 in base.items():
        for i, y in enumerate(range(2015, 2025)):
            v = None if (c, y) in gaps else round(min(100.0, v0 + i * (100 - v0) / 14), 1)
            rows.append({"year": y, "value": v, "country": c, "evidenceClass": "hypothetical"})
    data_sha = sha(rows)
    view = {
        "$schema": VL5, "width": 640, "height": 360,
        "title": "SYNTHETIC — SDG-style indicator: access to electricity (placeholder countries)",
        "data": {"values": rows},
        "layer": [
            {"mark": {"type": "line", "point": True},
             "encoding": {"x": {"field": "year", "type": "ordinal"}, "y": {"field": "value", "type": "quantitative", "scale": {"domain": [0, 100]}},
                          "color": {"field": "country", "type": "nominal"}}},
        ],
        "usermeta": {"sc": {
            "profile": "sc-vega-lite-v1", "datasetId": "synthetic:metrics-sdg-7-1-1-style-v1", "datasetSha256": data_sha,
            "evidenceField": "evidenceClass",
            "fields": {"year": {"label": "Year", "unit": "year"}, "value": {"label": "Population with access to electricity", "unit": "%"},
                       "country": {"label": "Country", "unit": "category"}, "evidenceClass": {"label": "Evidence class", "unit": "category"}},
            "uncertainty": {"kind": "none", "statement": "The synthetic source reports no uncertainty; missing years are shown as gaps, not interpolated."}}},
    }
    art = vl_artifact("SYN-METRICS-vega-lite", view)
    b = bundle("SYN-METRICS-vega-lite", "SYNTHETIC SDG-style indicator for three placeholder countries",
               "hypothetical", "hypothetical-only",
               [{"sourceId": "synthetic:metrics-indicator-table-v1", "provider": "Sustainable Catalyst test fixture standing in for the UN SDG database",
                 "citationId": "SYNTHETIC-SDG-TABLE", "identityStatus": "source-hash-verified", "qualityStatus": "not-applicable",
                 "licenceStatus": "verified-for-use", "sha256": data_sha}],
               [], "Synthetic indicator series with missing observations, used to exercise the Metrics acceptance path of FIG-02B.",
               ["Synthetic values for placeholder countries", "Missing years are not interpolated", "No causal or ranking claim"],
               "SYNTHETIC: indicator values by year for three placeholder countries; gaps are missing observations.",
               "Line chart of a synthetic percentage indicator from 2015 to 2024 for three placeholder countries, with gaps for missing years.",
               [art], "synthetic-fixture-tested")
    return b, view


def combined(erw_bundle, erw_view):
    plotly = json.loads((GENERIC / "points.plotly.json").read_text(encoding="utf-8"))
    src = json.loads((GENERIC / "points.bundle.json").read_text(encoding="utf-8"))
    b = json.loads(json.dumps(erw_bundle))
    b["figureId"] = "SYN-COMBINED-plotly-vega-lite"
    b["title"] = "SYNTHETIC figure with a Plotly view and a Vega-Lite view"
    b["artifacts"] = [erw_bundle["artifacts"][0], src["artifacts"][0]]
    b["rendering"]["renderer"] = "vega-lite; plotly"
    b["rendering"]["rendererVersion"] = "vega-lite 6.5.0; vega 6.4.0; plotly.js 3.3.1"
    assert sha(plotly) == src["artifacts"][0]["sha256"]
    return b


def main():
    eb, ev = erw()
    mb, mv = metrics()
    write("erw.bundle.json", eb); write("erw.vega-lite.json", ev)
    write("metrics.bundle.json", mb); write("metrics.vega-lite.json", mv)
    write("combined.bundle.json", combined(eb, ev))
    files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob("*.json")) if p.name != "SOURCE.json"}
    write("SOURCE.json", {"description": "SYNTHETIC FIG-02B fixtures built by build_fixtures.py; no scientific meaning; not Wexford or SDG data.",
                          "hashRule": "sha256 of json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)",
                          "files": files})


if __name__ == "__main__":
    main()
