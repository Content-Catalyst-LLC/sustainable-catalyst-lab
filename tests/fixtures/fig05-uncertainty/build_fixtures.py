#!/usr/bin/env python3
"""SC-FIG-05.3 fixtures: SYNTHETIC uncertainty-first figures produced by the real pipeline.

    python3 tests/fixtures/fig05-uncertainty/build_fixtures.py <workspace> <workbench> <site-intelligence>

(run with an interpreter that has fastapi, pydantic, numpy, scipy and plotly 6.5.2; SC_WORKSPACE_SERVICE_TOKEN set)

1. Workspace runtimes compute every uncertainty number: the R runtime's stats::predict.lm bands (the Workspace
   test fixture tests/fixtures/sc_fig05_r_linear_bands.json, produced in the R runtime image), the
   uncertainty runtime's ensemble-quantile-bands op on a seeded synthetic ensemble, and its correlated-normal
   op propagating synthetic per-field input uncertainty.
2. Workspace research_exports.extract_result_values checks and exports those records.
3. Site Intelligence's normaliser and package composer seal the synthetic field objects; the per-field
   uncertainty property is the runtime's value, and one field deliberately has none (drawn "not reported").
4. Workbench's Plotly and MapLibre adapters compile the figures.

Outputs (deterministic apart from Workbench's generatedAt and resultHash):
- chart.compile.json     Workbench Plotly compile response (band panel + fan panel)
- chart-unavailable.compile.json   same request with no runtime records: the unavailable state
- map.view.json, map.bundle.json   Workbench MapLibre view and bundle (value layer + uncertainty layer)
- chart.request.json, map.request.json   the Workbench requests (Workbench tests replay them)
- chart.bundle.json, chart.figure.json, chart.trend.bands.json, chart.ensemble.fan.json   the bundle-path package
- SOURCE.json            commits, inputs and file hashes
Every value is invented. Nothing here is a measured or modelled value for any real place.
"""
import base64
import copy
import hashlib
import importlib.util
import json
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
WS, WB, SI = (pathlib.Path(p).resolve() for p in sys.argv[1:4])


def commit(repo):
    return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()


def canonical(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- 1-2: Workspace runtimes and export -----------------------------------------------------------------------
sys.path.insert(0, str(WS / "backend"))
from fastapi.testclient import TestClient  # noqa: E402
from app import research_exports as rx  # noqa: E402

for k in [m for m in sys.modules if m == "app" or m.startswith("app.")]:
    del sys.modules[k]
sys.path.pop(0)
unc = TestClient(load(WS / "backend" / "uncertainty-runtime" / "service.py", "sc_unc_runtime").app)


def run(op, payload):
    r = unc.post("/v1/execute", json={"operation": op, "payload": payload})
    assert r.status_code == 200, r.text
    return r.json()


r_fixture = json.loads((WS / "backend" / "tests" / "fixtures" / "sc_fig05_r_linear_bands.json").read_text())
band = rx.extract_result_values({"kind": "coefficient-table", "uncertaintyField": "stdError",
                                 "intervalFields": {"lower": "confLow", "upper": "confHigh"},
                                 "rename": {"(Intercept)": "intercept", "t": "slope"}, "bands": ["confidence-band", "prediction-band"],
                                 "assumptions": ["Linear mean in t", "Independent errors", "Constant error variance", "Normal errors"]},
                                {"result": {"remote": r_fixture["output"]}})
# A seeded synthetic ensemble: 40 members x 10 annual steps, random walks with drift (plain LCG; no numpy RNG).
state = 20261112


def uniform():
    global state
    state = (1103515245 * state + 12345) % 2 ** 31
    return state / 2 ** 31


steps = list(range(2026, 2036))
members = []
for m in range(40):
    level, vals = 10.0, []
    for _ in steps:
        level += 0.35 + (uniform() - 0.5) * 1.2
        vals.append(round(level, 6))
    members.append({"name": f"member-{m + 1}", "values": vals})
fan_payload = {"steps": steps, "members": members, "centralLevels": [0.5, 0.8, 0.95]}
fan_result = run("workspace.uncertainty.ensemble-quantile-bands", fan_payload)
fan = rx.extract_result_values({"kind": "scalar-paths", "paths": {"memberCount": "memberCount"}, "quantileBands": True,
                                "assumptions": ["Members are exchangeable draws of one synthetic process", "Quantiles only at the declared steps"]},
                               {"result": {"remote": fan_result}})
# Per-field propagated uncertainty: synthetic modelled SOC means with synthetic input SDs, independent fields.
FIELDS = ["WX-F1", "WX-F2", "WX-F3", "WX-F4", "WX-F5"]
SOC = [26.4, 28.9, 31.2, 27.7, 33.5]
SOC_SD_IN = [0.6, 1.4, 0.9, 2.1, 1.1]
ident = [[1.0 if i == j else 0.0 for j in range(5)] for i in range(5)]
mc_payload = {"means": SOC, "sds": SOC_SD_IN, "correlationMatrix": ident, "draws": 4000, "seed": 20261112}
mc_result = run("workspace.uncertainty.correlated-normal", mc_payload)
map_export = rx.extract_result_values({"kind": "scalar-paths",
                                       "paths": {f: f"summaries.{i}.mean" for i, f in enumerate(FIELDS)},
                                       "uncertaintyPaths": {f: f"summaries.{i}.sd" for i, f in enumerate(FIELDS)},
                                       "uncertaintySemantics": "standard-deviation", "stochastic": True,
                                       "assumptions": ["Fields are independent", "Normal input uncertainty", "Monte Carlo SD of 4000 seeded draws"]},
                                      {"result": {"remote": mc_result}})
for x in (band, fan, map_export):
    assert "error" not in x, x

# --- 3: Site Intelligence objects ------------------------------------------------------------------------------
sys.path.insert(0, str(SI / "backend"))
from app import spatial_evidence_registry_v4460 as reg  # noqa: E402
from app import reproducible_spatial_packages_v4540 as pkg  # noqa: E402

for k in [m for m in sys.modules if m == "app" or m.startswith("app.")]:
    del sys.modules[k]
sys.path.pop(0)
src = {"source_id": "synthetic:fig05-soc-model", "authority": "sc-test-fixture", "license": "CC0-1.0"}
objects = []
for k, fid in enumerate(FIELDS + ["WX-F6"]):
    col, row = k % 3, k // 3
    x0, y0 = round(-6.62 + 0.08 * col, 3), round(52.30 + 0.06 * row, 3)
    x1, y1 = round(x0 + 0.072, 3), round(y0 + 0.052, 3)
    props = {"title": f"Field {fid} (synthetic)", "field_id": fid, "evidence_class": "modelled",
             "soc": map_export["values"].get(fid, 29.0) if fid != "WX-F6" else 29.0}
    if fid in map_export["uncertainty"]["values"]:
        props["soc_sd"] = map_export["uncertainty"]["values"][fid]
    objects.append(reg.normalize_evidence_object({
        "layer_id": "agriculture-food-systems", "geometry": {"type": "Polygon", "coordinates": [[[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]]},
        "source": src, "observed_at": "2026-11-01T00:00:00Z", "properties": props,
        "provenance": {"transformations": [{"step": "synthetic-fig05-soc-model", "note": "fixture only; invented values"}]}}))
package = pkg.compose_package({"title": "SYNTHETIC field SOC with runtime-propagated uncertainty (SC-FIG-05.3 fixture)",
                               "description": "Invented parcels; uncertainty from the Workspace uncertainty runtime. Not Wexford data.",
                               "evidence_objects": objects, "assumptions": ["All values are invented for software acceptance"],
                               "evidence_gaps": ["No measured soil carbon"]})["package"]
assert pkg.verify_package({"package": package})["ok"]
rows = [{"object_id": o["object_id"], "content_digest": o["content_digest"], "field_id": o["properties"]["field_id"],
         "soc": o["properties"]["soc"], **({"soc_sd": o["properties"]["soc_sd"]} if "soc_sd" in o["properties"] else {})} for o in objects]
dataset = {"schema": "sc-fig04-si-derived-dataset/1", "siPackage": package,
           "derivation": "one row per object: soc and soc_sd copied from properties (soc_sd is the Workspace runtime's value)", "rows": rows}

# --- 4: Workbench ------------------------------------------------------------------------------------------------
os.environ["SCWB_PLOTLY_ADAPTER_ENABLED"] = "1"
os.environ["SCWB_MAPLIBRE_ADAPTER_ENABLED"] = "1"
sys.path.insert(0, str(WB / "backend"))
from app import maplibre_figure_adapter as ml  # noqa: E402
from app import plotly_figure_adapter as pa  # noqa: E402

SOURCE_REF = {"sourceId": "synthetic-fig05", "provider": "SC-FIG-05.3 synthetic fixture", "identityStatus": "source-identified",
              "qualityStatus": "not-applicable", "licenceStatus": "verified-for-use"}
chart_bundle = {"figureId": "SYN-FIG05-uncertainty-chart", "title": "SYNTHETIC runtime regression bands and ensemble quantile fan",
                "projectRef": "fig05-synthetic", "ownerScope": "isolated-synthetic", "environment": "local-review",
                "evidenceClass": "modelled", "figureType": "evidence-chart",
                "interpretation": "Synthetic model outputs used only to accept uncertainty-first encodings.",
                "limitations": ["Synthetic values with no scientific meaning", "Bands evaluated only at observed predictor values"],
                "measurementStatus": "computed-from-specified-inputs", "doNotInfer": ["any real trend or projection"],
                "caption": "SYNTHETIC: runtime confidence and prediction bands (left) and an ensemble quantile fan (right).",
                "altText": "A fitted line with a darker 90% confidence band inside a lighter dashed 90% prediction band; "
                           "a median line inside nested 50%, 80% and 95% ensemble bands that widen over ten years.",
                "sourceRefs": [SOURCE_REF], "labels": ["synthetic"]}
band_calc = {"label": "Synthetic trend of y", "unit": "mg L-1", "xLabel": "t (years from 2010)",
             "method": "R stats::lm; bands from stats::predict.lm", "runRef": "sc://workspace/runs/synthetic-fig05-band",
             "values": band["values"], "bands": band["bands"], "linearFit": {"interceptKey": "intercept", "slopeKey": "slope"},
             "assumptions": band["assumptions"]}
fan_calc = {"label": "Synthetic ensemble projection", "unit": "mg L-1", "xLabel": "Year",
            "method": "Uncertainty runtime ensemble-quantile-bands", "runRef": "sc://workspace/runs/synthetic-fig05-fan",
            "values": fan["values"], "quantileBands": fan["quantileBands"], "assumptions": fan["assumptions"]}
chart_req = {"panels": [{"panelId": "trend", "chart": "band", "calculation": 0}, {"panelId": "ensemble", "chart": "fan", "calculation": 1}],
             "calculations": [band_calc, fan_calc], "bundle": chart_bundle, "width": 1000, "height": 760}
chart = pa.compile_request(pa.PlotlyCompileRequest.model_validate(chart_req))
na_req = copy.deepcopy(chart_req)
na_req["calculations"][0].pop("bands"); na_req["calculations"][0].pop("linearFit"); na_req["calculations"][1].pop("quantileBands")
na_req["bundle"].update(figureId="SYN-FIG05-uncertainty-unavailable",
                        caption="SYNTHETIC: the runtime reported no bands, so uncertainty is shown as unavailable.",
                        altText="Two empty panels each stating that uncertainty is unavailable because the run reported none.")
chart_na = pa.compile_request(pa.PlotlyCompileRequest.model_validate(na_req))

raw = canonical(dataset).encode("utf-8")
map_req = {
    "dataset": {"datasetId": "fig05-uncertainty-map", "sha256": hashlib.sha256(raw).hexdigest(),
                "contentBase64": base64.b64encode(raw).decode(), "evidenceClass": "modelled"},
    "view": {"title": "SYNTHETIC field soil organic carbon and its runtime-propagated uncertainty",
             "fields": {"field_id": {"label": "Field", "unit": "category"},
                        "soc": {"label": "Soil organic carbon", "unit": "g kg-1", "uncertainty": "soc_sd", "uncertaintyKind": "standard-deviation"}},
             "layers": [
                 {"id": "soc-value", "geometry": "polygon", "evidenceClass": "modelled", "legend": "Modelled soil organic carbon (synthetic)",
                  "style": {"opacity": 0.8, "outlineColor": "#333333", "outlineWidth": 1},
                  "classify": {"field": "soc", "breaks": [27, 29, 31], "colors": ["#440154", "#3b528b", "#21918c", "#5ec962"]}},
                 {"id": "soc-uncertainty", "geometry": "polygon", "evidenceClass": "modelled",
                  "legend": "Uncertainty of modelled soil organic carbon (runtime Monte Carlo SD)",
                  "style": {"opacity": 0.85, "outlineColor": "#333333", "outlineWidth": 1},
                  "classify": {"field": "soc", "breaks": [0.8, 1.2, 1.8], "colors": ["#00224e", "#414d6b", "#7c7b78", "#bcaf6f"]},
                  "encode": "uncertainty", "uncertaintyRef": 0}]},
    "calculations": [{"label": "Propagated SOC uncertainty per field", "unit": "g kg-1", "method": "Uncertainty runtime correlated-normal, 4000 seeded draws",
                      "runRef": "sc://workspace/runs/synthetic-fig05-map", "values": map_export["values"],
                      "uncertainty": map_export["uncertainty"], "assumptions": map_export["assumptions"],
                      "role": "map-uncertainty", "match": "field_id"}],
    "bundle": {"figureId": "SYN-FIG05-uncertainty-map", "title": "SYNTHETIC soil organic carbon with runtime uncertainty layer",
               "projectRef": "fig05-synthetic", "ownerScope": "isolated-synthetic", "environment": "local-review",
               "evidenceClass": "modelled", "measurementStatus": "computed-from-specified-inputs",
               "interpretation": "Synthetic map used only to accept the per-field uncertainty layer.",
               "limitations": ["Invented parcels and values", "One field has no runtime uncertainty and is shown as not reported"],
               "doNotInfer": ["any real Wexford soil carbon value"],
               "caption": "SYNTHETIC: modelled field SOC classes and, as a toggle, the runtime-propagated SOC standard deviation.",
               "altText": "Six field parcels shaded by modelled SOC class; a second layer shades five by uncertainty, the sixth not reported.",
               "sourceRefs": [{"sourceId": "synthetic:fig05-soc-model", "provider": "SC-FIG-05.3 synthetic fixture via Site Intelligence normaliser",
                               "identityStatus": "source-hash-verified", "qualityStatus": "not-applicable", "licenceStatus": "verified-for-use",
                               "notes": "CC0-1.0 synthetic fixture"}], "labels": ["synthetic"]},
}
mapped = ml.compile_request(ml.MapLibreCompileRequest.model_validate(map_req))

write("map.request.json", map_req)
write("chart.request.json", chart_req)
write("chart.compile.json", chart)
# The bundle-path package (what Research releases and the Hub renders): bundle, figure artifact and the two
# runtime records, each a file whose canonical hash the bundle's calculationRefs bind.
write("chart.bundle.json", chart["figureBundle"])
write("chart.figure.json", chart["plotly"]["figure"])
write("chart.trend.bands.json", band["bands"])
write("chart.ensemble.fan.json", fan["quantileBands"])
write("chart-unavailable.compile.json", chart_na)
write("map.view.json", mapped["maplibre"]["view"])
write("map.bundle.json", mapped["figureBundle"])
write("map.compile.json", mapped)
write("map.uncertainty.json", map_export["uncertainty"])  # the record map.bundle.json binds (uncertaintySha256)
names = ("chart.request.json", "chart.compile.json", "chart.bundle.json", "chart.figure.json", "chart.trend.bands.json",
         "chart.ensemble.fan.json", "chart-unavailable.compile.json", "map.request.json", "map.view.json", "map.bundle.json", "map.compile.json",
         "map.uncertainty.json")
write("SOURCE.json", {
    "generator": "tests/fixtures/fig05-uncertainty/build_fixtures.py", "synthetic": True,
    "commits": {"workspace": commit(WS), "workbench": commit(WB), "siteIntelligence": commit(SI)},
    "runtimeInputs": {"rFixtureSha256": hashlib.sha256((WS / "backend" / "tests" / "fixtures" / "sc_fig05_r_linear_bands.json").read_bytes()).hexdigest(),
                      "ensembleInputSha256": hashlib.sha256(canonical(fan_payload).encode()).hexdigest(),
                      "ensembleRuntimeFingerprint": fan_result["inputFingerprint"],
                      "mapInputSha256": hashlib.sha256(canonical(mc_payload).encode()).hexdigest(),
                      "mapRuntimeFingerprint": mc_result["inputFingerprint"]},
    "exports": {"band": band, "fan": fan, "map": map_export},
    "inputs": {"ensemble": fan_payload, "map": mc_payload},
    "files": {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in names},
})
print("ok", {n: (HERE / n).stat().st_size for n in names})
