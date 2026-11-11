#!/usr/bin/env python3
"""SC-FIG-04 fixtures: SYNTHETIC Wexford agricultural and environmental spatial evidence.

    python3 tests/fixtures/fig04-wexford/build_fixtures.py <site-intelligence checkout>

Every evidence object is produced by Site Intelligence's own normaliser
(backend/app/spatial_evidence_registry_v4460.normalize_evidence_object), and the set is sealed with SI's
reproducible spatial package (backend/app/reproducible_spatial_packages_v4540.compose_package), so the
digests are SI's. Field shapes, monitoring sites and every value are invented: nothing here is a measured
Wexford soil carbon, nitrate or pH value, and no claim about any real farm or water body may be drawn from it.

Outputs (byte-identical on re-run):
- wexford.si-package.json   sealed SI package (evidence_objects group)
- wexford.dataset.json      Workspace dataset: flat rows derived from the objects, pinned to the package
- wexford.map-view.json     Lab map view sc-lab-maplibre-view/1.1
- wexford.bundle.json       sc.figure-bundle.v1 (spatial-map, EPSG:4326)
"""
import hashlib
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
VIEW_MEDIA = "application/vnd.sc.maplibre-view.v1+json"
TIMES = ["2026-02-01T00:00:00Z", "2026-05-01T00:00:00Z", "2026-08-01T00:00:00Z", "2026-11-01T00:00:00Z"]
BBOX = [-6.64, 52.28, -6.36, 52.44]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def ols(xs, ys):
    """Ordinary least squares slope with its standard error (same model as R lm(y ~ x))."""
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    icpt = my - slope * mx
    rss = sum((y - icpt - slope * x) ** 2 for x, y in zip(xs, ys))
    return slope, (rss / (n - 2) / sxx) ** 0.5


def fields():
    # Six synthetic field parcels on a 3 x 2 grid (lon -6.62..-6.38, lat 52.30..52.42).
    out = []
    for k in range(6):
        col, row = k % 3, k // 3
        x0, y0 = round(-6.62 + 0.08 * col, 3), round(52.30 + 0.06 * row, 3)
        x1, y1 = round(x0 + 0.072, 3), round(y0 + 0.052, 3)
        out.append((f"WX-F{k + 1}", [[[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]]))
    return out


SITES = [("WX-M1", [-6.605, 52.315]), ("WX-M2", [-6.55, 52.335]), ("WX-M3", [-6.49, 52.31]), ("WX-M4", [-6.415, 52.33]),
         ("WX-M5", [-6.59, 52.395]), ("WX-M6", [-6.52, 52.405]), ("WX-M7", [-6.455, 52.38]), ("WX-M8", [-6.395, 52.41])]
SOC0 = [28.4, 31.2, 25.9, 34.1, 29.7, 27.3]      # g kg-1 at the first step (invented)
SOC_STEP = [0.30, -0.10, 0.45, 0.05, 0.20, 0.35]   # change per quarter (invented)
NO3 = [4.2, 7.9, 11.3, 5.6, 3.1, 8.8, 12.6, 6.4]   # mg L-1 nitrate-N at the first step (invented)
NO3_SEASON = [0.0, -1.4, -2.6, 1.9]                # seasonal offset per step (invented)


def main():
    si = pathlib.Path(sys.argv[1]).resolve()
    sys.path.insert(0, str(si / "backend"))
    from app import spatial_evidence_registry_v4460 as reg  # noqa: E402
    from app import reproducible_spatial_packages_v4540 as pkg  # noqa: E402
    si_commit = subprocess.run(["git", "-C", str(si), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    src_soil = {"source_id": "synthetic:fig04-wexford-soil-model", "authority": "sc-test-fixture", "license": "CC0-1.0"}
    src_water = {"source_id": "synthetic:fig04-wexford-nitrate-model", "authority": "sc-test-fixture", "license": "CC0-1.0"}
    objects = []
    for t, when in enumerate(TIMES):
        for k, (fid, ring) in enumerate(fields()):
            soc = round(SOC0[k] + SOC_STEP[k] * t + (0.15 if (k + t) % 3 == 0 else -0.1), 2)
            props = {"title": f"Field {fid} (synthetic)", "field_id": fid, "evidence_class": "modelled",
                     "soc": soc, "soc_se": round(0.8 + 0.1 * ((k + 2 * t) % 5), 2),
                     "ph": None if (k == 4 and t == 2) else round(6.1 + 0.15 * ((k + t) % 4), 2)}
            objects.append(reg.normalize_evidence_object({
                "layer_id": "agriculture-food-systems", "geometry": {"type": "Polygon", "coordinates": ring},
                "source": src_soil, "observed_at": when, "properties": props,
                "provenance": {"transformations": [{"step": "synthetic-field-soil-model", "note": "fixture only; invented values"}]}}))
        for k, (sid, xy) in enumerate(SITES):
            objects.append(reg.normalize_evidence_object({
                "layer_id": "hydrology-rivers-flood-drought", "geometry": {"type": "Point", "coordinates": xy},
                "source": src_water, "observed_at": when,
                "properties": {"title": f"Monitoring site {sid} (hypothetical)", "site_id": sid, "evidence_class": "modelled",
                               "nitrate_n": round(max(0.5, NO3[k] + NO3_SEASON[t] + 0.3 * ((k * 7 + t) % 3 - 1)), 2)},
                "provenance": {"transformations": [{"step": "synthetic-nitrate-model", "note": "fixture only; invented values"}]}}))
    package = pkg.compose_package({
        "title": "SYNTHETIC Wexford agricultural and environmental evidence (SC-FIG-04 fixture)",
        "description": "Invented field parcels and hypothetical monitoring sites for the SC-FIG-04 geospatial workflow. Not Wexford data.",
        "evidence_objects": objects,
        "assumptions": ["All values are invented for software acceptance"],
        "evidence_gaps": ["No measured soil carbon, nitrate or pH data"],
    })["package"]
    assert pkg.verify_package({"package": package})["ok"]

    t0 = TIMES[0]
    rows = []
    for o in objects:
        p = o["properties"]
        if "soc" not in p:
            continue
        rows.append({"object_id": o["object_id"], "content_digest": o["content_digest"], "field_id": p["field_id"],
                     "observed_at": o["observed_at"], "t_years": TIMES.index(o["observed_at"].replace("+00:00", "Z")) * 0.25,
                     "soc": p["soc"], "soc_se": p["soc_se"]})
    assert len(rows) == 24 and t0
    dataset = {"schema": "sc-fig04-si-derived-dataset/1",
               "siPackage": {"package_id": package["package_id"], "package_digest": package["package_digest"],
                             "manifest_digest": package["manifest"]["manifest_digest"]},
               "derivation": "one row per agriculture-food-systems object: soc and soc_se copied from properties; t_years = quarter index x 0.25",
               "rows": rows}
    slope, slope_se = ols([r["t_years"] for r in rows], [r["soc"] for r in rows])

    steps = sorted({o["observed_at"] for o in objects})
    view = {
        "schema": "sc-lab-maplibre-view/1.1",
        "title": "SYNTHETIC Wexford field soil organic carbon and hypothetical nitrate monitoring (invented values)",
        "objects": objects,
        "evidenceField": "evidence_class",
        "fields": {"field_id": {"label": "Field", "unit": "category"},
                   "soc": {"label": "Soil organic carbon", "unit": "g kg-1", "uncertainty": "soc_se", "uncertaintyKind": "standard-error"},
                   "ph": {"label": "Soil pH", "unit": "1"},
                   "site_id": {"label": "Monitoring site", "unit": "category"},
                   "nitrate_n": {"label": "Nitrate-N", "unit": "mg L-1"}},
        "layers": [
            {"id": "field-soc", "geometry": "polygon", "where": {"property": "evidence_class", "equals": "modelled"},
             "style": {"opacity": 0.75, "outlineColor": "#333333", "outlineWidth": 1},
             "classify": {"field": "soc", "breaks": [26, 29, 32], "colors": ["#edf8e9", "#bae4b3", "#74c476", "#238b45"]}},
            {"id": "nitrate-heat", "geometry": "heatmap", "where": {"property": "evidence_class", "equals": "modelled"},
             "weight": {"field": "nitrate_n", "max": 15}, "ramp": "magma", "style": {"radius": 40, "intensity": 1, "opacity": 0.7}},
            {"id": "nitrate-sites", "geometry": "point", "where": {"property": "evidence_class", "equals": "modelled"},
             "style": {"color": "#1f78b4", "radius": 5, "opacity": 1, "strokeColor": "#ffffff", "strokeWidth": 1}},
        ],
        "legend": [{"layer": "field-soc", "label": "Modelled field soil organic carbon (synthetic)"},
                   {"layer": "nitrate-heat", "label": "Modelled nitrate-N density (hypothetical sites)"},
                   {"layer": "nitrate-sites", "label": "Hypothetical monitoring sites"}],
        "basemap": None,
        "camera": {"bbox": BBOX, "maxZoom": 12},
        "time": {"property": "observed_at", "label": "Quarter (synthetic)", "steps": steps, "initial": steps[-1]},
        "comparison": {"field": "soc", "from": steps[0], "to": steps[-1], "match": "field_id",
                       "label": "Change in modelled soil organic carbon, first to last quarter (synthetic)"},
        "calculations": [{"label": "Soil organic carbon trend (OLS, all fields)", "value": round(slope, 4), "unit": "g kg-1 yr-1",
                          "uncertainty": round(slope_se, 4), "uncertaintyKind": "standard-error",
                          "method": "lm(soc ~ t_years) over 24 field-quarter rows", "calculationRef": 0}],
    }
    view_sha = sha(view)
    dataset_sha = sha(dataset)
    srcs = [{"sourceId": s["source_id"], "provider": "Sustainable Catalyst test fixture via Site Intelligence normaliser",
             "identityStatus": "source-identified", "qualityStatus": "not-applicable", "licenceStatus": "verified-for-use",
             "crs": "EPSG:4326", "notes": "CC0-1.0 synthetic fixture"} for s in (src_soil, src_water)]
    bundle = {
        "schema": "sc.figure-bundle.v1", "figureId": "SYN-FIG04-wexford-map", "version": 1,
        "title": "SYNTHETIC Wexford field soil organic carbon with hypothetical nitrate monitoring",
        "project": {"projectRef": "fig04-synthetic-ci", "ownerScope": "unbound-local", "environment": "local-review"},
        "publication": {"kind": "none", "target": "unassigned", "bindingStatus": "unbound"},
        "figureType": "spatial-map", "evidenceClass": "modelled",
        "scientificContext": {"interpretation": "Synthetic map used to accept the SC-FIG-04 geospatial workflow.",
                              "limitations": ["Invented field shapes, sites and values", "No basemap or imagery",
                                              "Heat map is a kernel density of point weights, not an interpolated surface"],
                              "measurementStatus": "computed-from-specified-inputs", "units": "g kg-1; mg L-1",
                              "doNotInfer": ["any real Wexford soil carbon, nitrate or pH value", "any farm or water-body location",
                                             "measured carbon removal"]},
        "sourceRefs": srcs,
        "calculationRefs": [{"system": "other", "runRef": "fixture:fig04-soc-trend", "method": "OLS slope of soc on t_years (fixture)",
                             "outputSha256": sha({"slope": round(slope, 4), "se": round(slope_se, 4), "dataset": dataset_sha}), "assumptionRefs": []}],
        "spatial": {"geometryStatus": "illustrative", "crs": "EPSG:4326", "extentStatus": "regional-rectangle", "bbox": BBOX,
                    "siPackage": dataset["siPackage"]},
        "rendering": {"profileId": "sc-institutional-research-v1", "renderer": "maplibre-gl", "rendererVersion": "5.24.0",
                      "caption": "SYNTHETIC: modelled field soil organic carbon (graduated), hypothetical nitrate-N density and sites, by quarter.",
                      "altText": "Six field parcels shaded by modelled soil organic carbon class, with eight hypothetical monitoring points and a nitrate density overlay.",
                      "palette": "colorblind-safe", "accessibilityReview": "pending", "visualizationSpecSha256": view_sha},
        "artifacts": [{"format": "json", "artifactRef": f"sc://lab/fig04/SYN-FIG04-wexford-map/{view_sha}.json", "sha256": view_sha,
                       "mediaType": VIEW_MEDIA, "status": "local-review", "revision": 1}],
        "provenance": {"authorityOwner": "lab", "sourceSnapshotIds": [s["source_id"] for s in (src_soil, src_water)],
                       "generationRunId": "lab.fig04-fixture-builder:" + view_sha[:24], "generatedAt": "2026-11-11T00:00:00Z",
                       "reproducibility": "synthetic-fixture-tested",
                       "lineageRefs": ["site-intelligence-package:" + package["package_digest"], "dataset:sha256:" + dataset_sha]},
        "review": {"scientific": "pending", "visual": "pending", "rights": "pending", "sourceIntegrity": "pending", "publication": "pending"},
    }
    write("wexford.si-package.json", package)
    write("wexford.dataset.json", dataset)
    write("wexford.map-view.json", view)
    write("wexford.bundle.json", bundle)
    names = ("wexford.si-package.json", "wexford.dataset.json", "wexford.map-view.json", "wexford.bundle.json")
    files = {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in names}
    write("SOURCE.json", {"generator": "tests/fixtures/fig04-wexford/build_fixtures.py", "siteIntelligenceCommit": si_commit,
                          "siNormaliser": "backend/app/spatial_evidence_registry_v4460.normalize_evidence_object",
                          "siPackage": "backend/app/reproducible_spatial_packages_v4540.compose_package",
                          "synthetic": True, "objects": len(objects), "socTrend": {"slope": round(slope, 4), "se": round(slope_se, 4)},
                          "files": files})
    print(json.dumps({"objects": len(objects), "slope": slope, "se": slope_se, "files": files}, indent=1))


if __name__ == "__main__":
    main()
