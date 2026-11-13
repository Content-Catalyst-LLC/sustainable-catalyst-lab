#!/usr/bin/env python3
"""FIG-03A preparation fixtures: synthetic Site Intelligence spatial evidence objects + a Lab map view + bundle.

    python3 tests/fixtures/fig03a-maplibre/build_fixtures.py <site-intelligence checkout>

The evidence objects are produced by Site Intelligence's own normaliser
(backend/app/spatial_evidence_registry_v4460.normalize_evidence_object), so their content digests are
SI's, and the Lab adapter must reproduce them. All places and values are synthetic. Re-running gives
byte-identical files.
"""
import hashlib
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
VIEW_MEDIA = "application/vnd.sc.maplibre-view.v1+json"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    si = pathlib.Path(sys.argv[1]).resolve()
    sys.path.insert(0, str(si / "backend"))
    from app import spatial_evidence_registry_v4460 as reg  # noqa: E402
    si_commit = subprocess.run(["git", "-C", str(si), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    src = {"source_id": "synthetic:fig03a-soil-network", "authority": "sc-test-fixture", "license": "CC0-1.0"}
    zones = [
        ("Zone A (synthetic)", [[[-7.2, 52.1], [-6.9, 52.1], [-6.9, 52.35], [-7.2, 52.35], [-7.2, 52.1]]], 31.5),
        ("Zone B (synthetic)", [[[-6.9, 52.1], [-6.55, 52.1], [-6.55, 52.35], [-6.9, 52.35], [-6.9, 52.1]]], 27.25),
    ]
    points = [("Comparison site 1 (synthetic)", [-7.05, 52.22], 29.0), ("Comparison site 2 (synthetic)", [-6.7, 52.27], 25.5)]
    objects = []
    for title, ring, soc in zones:
        objects.append(reg.normalize_evidence_object({
            "layer_id": "soils-land-degradation", "geometry": {"type": "Polygon", "coordinates": ring},
            "source": src, "observed_at": "2026-05-01T00:00:00Z",
            "properties": {"title": title, "evidence_class": "modelled", "soc": soc},
            "provenance": {"transformations": [{"step": "synthetic-zone-model", "note": "fixture only"}]}}))
    for title, xy, soc in points:
        objects.append(reg.normalize_evidence_object({
            "layer_id": "soils-land-degradation", "geometry": {"type": "Point", "coordinates": xy},
            "source": src, "observed_at": "2026-05-01T00:00:00Z",
            "properties": {"title": title, "evidence_class": "literature-derived", "soc": soc}}))
    view = {
        "schema": "sc-lab-maplibre-view/1.0",
        "title": "SYNTHETIC soil organic carbon zones and comparison sites (not Wexford data)",
        "objects": objects,
        "evidenceField": "evidence_class",
        "fields": {"title": {"label": "Site", "unit": "category"}, "soc": {"label": "Soil organic carbon", "unit": "g kg-1"}},
        "layers": [
            {"id": "modelled-zones", "geometry": "polygon", "where": {"property": "evidence_class", "equals": "modelled"},
             "style": {"color": "#5e3c99", "opacity": 0.25, "outlineColor": "#5e3c99", "outlineWidth": 1.5}},
            {"id": "literature-sites", "geometry": "point", "where": {"property": "evidence_class", "equals": "literature-derived"},
             "style": {"color": "#e66101", "radius": 6, "opacity": 0.95, "strokeColor": "#ffffff", "strokeWidth": 1}},
        ],
        "legend": [{"layer": "modelled-zones", "label": "Modelled zones (synthetic)"},
                   {"layer": "literature-sites", "label": "Literature comparison sites (synthetic)"}],
        "basemap": None,
        "camera": {"bbox": [-7.2, 52.1, -6.55, 52.35], "maxZoom": 11},
    }
    view_sha = sha(view)
    bundle = {
        "schema": "sc.figure-bundle.v1", "figureId": "SYN-FIG03A-soil-map", "version": 1,
        "title": "SYNTHETIC soil organic carbon zones with literature comparison sites",
        "project": {"projectRef": "fig03a-synthetic-ci", "ownerScope": "unbound-local", "environment": "local-review"},
        "publication": {"kind": "none", "target": "unassigned", "bindingStatus": "unbound"},
        "figureType": "spatial-map", "evidenceClass": "modelled",
        "scientificContext": {"interpretation": "Synthetic map used to prepare the FIG-03A MapLibre adapter.",
                              "limitations": ["Synthetic geometry and values", "No basemap; positions are illustrative of the contract only"],
                              "measurementStatus": "computed-from-specified-inputs", "units": "g kg-1",
                              "doNotInfer": ["any real soil carbon value", "any Wexford site location"]},
        "sourceRefs": [{"sourceId": src["source_id"], "provider": "Sustainable Catalyst test fixture via Site Intelligence normaliser",
                        "identityStatus": "source-identified", "qualityStatus": "not-applicable", "licenceStatus": "verified-for-use",
                        "crs": "EPSG:4326", "notes": "CC0-1.0 synthetic fixture"}],
        "calculationRefs": [{"system": "other", "runRef": "fixture:fig03a-zones", "method": "synthetic zone values (fixture)",
                             "outputSha256": sha([o["content_digest"] for o in objects]), "assumptionRefs": []}],
        "spatial": {"geometryStatus": "illustrative", "crs": "EPSG:4326", "extentStatus": "regional-rectangle",
                    "bbox": [-7.2, 52.1, -6.55, 52.35]},
        "rendering": {"profileId": "sc-institutional-research-v1", "renderer": "maplibre-gl", "rendererVersion": "not yet vendored (FIG-03A preparation)",
                      "caption": "SYNTHETIC: modelled zones (shaded) and literature comparison sites (points); no basemap.",
                      "altText": "Two adjacent shaded rectangles representing modelled zones, with two comparison points inside them.",
                      "palette": "colorblind-safe", "accessibilityReview": "pending", "visualizationSpecSha256": view_sha},
        "artifacts": [{"format": "json", "artifactRef": f"sc://lab/fig03a/SYN-FIG03A-soil-map/{view_sha}.json", "sha256": view_sha,
                       "mediaType": VIEW_MEDIA, "status": "local-review", "revision": 1}],
        "provenance": {"authorityOwner": "lab", "sourceSnapshotIds": [src["source_id"]], "generationRunId": "lab.fig03a-fixture-builder:" + view_sha[:24],
                       "generatedAt": "2026-11-11T00:00:00Z", "reproducibility": "synthetic-fixture-tested",
                       "lineageRefs": ["site-intelligence:" + o["object_id"] for o in objects]},
        "review": {"scientific": "pending", "visual": "pending", "rights": "pending", "sourceIntegrity": "pending", "publication": "pending"},
    }
    write("soil.map-view.json", view)
    write("soil.bundle.json", bundle)
    files = {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in ("soil.bundle.json", "soil.map-view.json")}
    write("SOURCE.json", {"generator": "tests/fixtures/fig03a-maplibre/build_fixtures.py", "siteIntelligenceCommit": si_commit,
                          "siNormaliser": "backend/app/spatial_evidence_registry_v4460.normalize_evidence_object",
                          "synthetic": True, "files": files})
    print(json.dumps(files, indent=1))


if __name__ == "__main__":
    main()
