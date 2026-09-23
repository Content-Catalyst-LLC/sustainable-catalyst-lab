import numpy as np
import pytest

from app.spatial_spatiotemporal_research_studio_v01260 import *


def crs():
    return {"id": "LOCAL:GRID", "name": "Declared research grid", "axisOrder": "xy", "units": "km", "geographic": False}


def spatial_rows():
    rows=[]
    for iy in range(4):
        for ix in range(4):
            i=iy*4+ix
            rows.append({"id":f"p{i}","x":float(ix),"y":float(iy),"value":float(ix+iy+(2 if ix>=2 and iy>=2 else 0)),"cov":float(ix-iy)})
    return rows


def study_payload():
    return {"id":"s1","title":"Spatial study","rows":spatial_rows(),"x":"x","y":"y","value":"value","id_column":"id","crs":crs()}


def test_health_catalog_schema_boundaries():
    h=health(); c=catalog(); s=schema_info()
    assert h["version"]=="0.126.0" and h["method_family_count"]==12 and h["figure_family_count"]==14
    assert c["automatic_reprojection"] is False and h["automatic_causal_interpretation"] is False
    assert s["limits"]["rows"]==50000


def test_study_and_crs_audit_are_explicit():
    n=normalize_study(study_payload())["study"]
    assert n["crs"]["id"]=="LOCAL:GRID" and n["row_count"]==16 and len(n["study_hash"])==64
    a=crs_audit({"crs":{"id":"EPSG:4326","units":"degrees","geographic":True}})
    assert a["automatic_reprojection"] is False and a["physical_distance_certified"] is False and a["warnings"]


def test_knn_weights_are_reproducible():
    w=build_spatial_weights({**study_payload(),"method":"knn","k":2})["weights"]
    assert len(w["matrix"])==16 and len(w["weights_hash"])==64
    assert all(abs(sum(row)-1)<1e-9 for row in w["matrix"])
    w2=build_spatial_weights({**study_payload(),"method":"knn","k":2})["weights"]
    assert w["weights_hash"]==w2["weights_hash"]


def test_distance_band_rejects_isolates():
    with pytest.raises(SpatialResearchStudioError):
        build_spatial_weights({**study_payload(),"method":"distance-band","threshold":0.1})


def test_global_and_local_moran():
    p={**study_payload(),"method":"knn","k":3}
    g=global_morans_i(p); l=local_morans_i(p)
    assert isinstance(g["moran_i"],float) and g["significance_certified"] is False
    assert len(l["locations"])==16 and l["significance_labels_assigned"] is False
    assert {x["quadrant"] for x in l["locations"]} <= {"HH","LL","HL","LH"}


def test_getis_ord_and_nearest_neighbor():
    p={**study_payload(),"method":"knn","k":3}
    g=getis_ord_gi_star(p); n=nearest_neighbor_report(study_payload())
    assert len(g["locations"])==16 and g["multiple_testing_adjustment_performed"] is False
    assert n["mean_nearest_distance"]>0 and n["physical_distance_certified"] is False


def test_spatial_lag_is_descriptive_not_causal():
    r=spatial_lag_estimate({**study_payload(),"method":"knn","k":3,"covariates":["cov"]})
    assert r["model_type"]=="descriptive-spatial-lag-regression" and r["causal_interpretation"] is False
    assert {x["term"] for x in r["coefficients"]}=={"intercept","spatial_lag_y","cov"}


def raster(values):
    return {"id":"r","crs":crs(),"bounds":[0,0,2,2],"values":values}


def test_raster_zonal_stats_and_change():
    z=raster_zonal_stats({"raster":raster([[1,2],[3,4]]),"zones":[["a","a"],["b","b"]]})
    assert len(z["zones"])==2 and z["zones"][0]["mean"]==1.5
    ch=raster_change_summary({"before":raster([[1,2],[3,4]]),"after":raster([[2,4],[1,5]])})
    assert ch["summary"]["valid_change_cells"]==4 and ch["automatic_resampling"] is False


def test_spatial_join_is_plan_only():
    p=spatial_join_plan({"left_ref":"points:1","right_ref":"zones:1","predicate":"within"})
    assert p["predicate"]=="within" and p["automatic_execution"] is False and p["relationship_inference"] is False


def spacetime_rows():
    rows=[]
    for t in range(3):
        for y in range(2):
            for x in range(2):
                rows.append({"id":f"{x}-{y}","location_id":f"{x}-{y}","entity_id":f"e{y}","x":float(x),"y":float(y),"time":float(t),"value":float(x+y+t),"score":float(x+y+t)})
    return rows


def test_spatiotemporal_cube_and_change_profiles():
    rows=spacetime_rows()
    c=build_spatiotemporal_cube({"rows":rows,"x":"x","y":"y","time":"time","value":"value","x_edges":[-0.5,0.5,1.5],"y_edges":[-0.5,0.5,1.5],"time_edges":[-0.5,0.5,1.5,2.5],"statistic":"mean"})["cube"]
    assert len(c["cells"])==12 and c["included_row_count"]==12 and c["automatic_binning"] is False
    p=spatiotemporal_change_profile({"rows":rows,"location_id":"location_id","time":"time","value":"value"})
    assert len(p["locations"])==4 and all(x["linear_slope"] is not None for x in p["locations"])


def test_space_time_autocorrelation_is_slice_descriptive():
    p=space_time_autocorrelation({"rows":spacetime_rows(),"id_column":"id","x":"x","y":"y","time":"time","value":"value","crs":crs(),"method":"knn","k":2})
    assert len(p["time_slices"])==3 and p["significance_certified"] is False


def test_trajectory_and_hotspot_persistence():
    rows=spacetime_rows()
    t=trajectory_report({"rows":rows,"entity_id":"entity_id","time":"time","x":"x","y":"y","crs":crs()})
    assert len(t["trajectories"])==2 and t["geodesic_distance_computed"] is False
    h=hotspot_persistence({"rows":rows,"location_id":"location_id","time":"time","score":"score","threshold":2.0})
    assert len(h["locations"])==4 and h["statistical_significance_inferred"] is False


def test_visual_studio_snapshot_export_core_and_boundaries():
    v=build_visualization_plan({}); assert v["figure_count"]==14 and v["automatic_claim_generation"] is False
    st=build_studio({"study_id":"s1","methods":["global-morans-i"]})["studio"]; assert len(st["studio_hash"])==64
    snap=build_snapshot({"studio":st}); assert len(snap["snapshot_hash"])==64 and snap["automatic_persistence"] is False
    assert build_reproduction_plan({"snapshot_ref":"snap:1"})["automatic_execution"] is False
    assert build_export_plan({})["automatic_publication"] is False
    assert build_core_object_plan({"session_id":"sess","analysis_id":"a1"})["automatic_core_submission"] is False
    assert build_execution_lineage_plan({"session_id":"sess","analysis_id":"a1"})["automatic_execution"] is False
    b=interpretation_boundaries_report(); assert b["causal_validity_certified"] is False and len(b["boundaries"])>=8
