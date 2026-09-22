import pytest
from app.exploratory_data_analysis_studio_v01200 import *

ROWS=[
 {"group":"A","x":1.0,"y":2.0,"z":10.0,"note":"alpha"},
 {"group":"A","x":2.0,"y":4.1,"z":11.0,"note":"alpha"},
 {"group":"A","x":3.0,"y":6.2,"z":None,"note":"beta"},
 {"group":"B","x":4.0,"y":8.0,"z":13.0,"note":"beta"},
 {"group":"B","x":5.0,"y":10.2,"z":14.0,"note":"gamma"},
 {"group":"B","x":40.0,"y":12.0,"z":15.0,"note":"gamma"},
]
BASE={"id":"eda-test","rows":ROWS}

def test_normalize_and_profile():
 d=normalize_dataset(BASE); assert d["row_count"]==6 and d["source_rows_immutable"] is True and len(d["dataset_hash"])==64
 p=profile_dataset(BASE); assert p["exploratory_not_confirmatory"] is True and any(x["column"]=="x" and x["kind"]=="numeric" for x in p["columns"])

def test_missingness_and_distributions():
 m=analyze_missingness(BASE); assert next(x for x in m["columns"] if x["column"]=="z")["missing_count"]==1 and m["mcar_mar_mnar_not_determined"] is True
 d=analyze_distributions(BASE); assert d["normality_assumed"] is False and any(x["column"]=="group" for x in d["distributions"])

def test_correlations_are_exploratory():
 c=analyze_correlations({**BASE,"columns":["x","y","z"],"method":"spearman"}); assert c["p_values_computed"] is False and c["causality_inferred"] is False and len(c["pairs"])==3

def test_group_comparison_is_descriptive():
 g=compare_groups({**BASE,"group_by":"group","value_columns":["x","y"]}); assert len(g["groups"])==2 and g["hypothesis_test_performed"] is False and len(g["descriptive_contrasts"])==2

def test_outlier_flagging_never_removes_rows():
 o=analyze_outliers({**BASE,"columns":["x"],"method":"iqr","threshold":1.5}); assert o["rows_removed"] is False and o["columns"][0]["flag_count"]>=1

def test_relationship_no_causality():
 r=analyze_relationship({**BASE,"x":"x","y":"y"}); assert r["n"]==6 and r["causality_inferred"] is False and r["linear_descriptive_fit"]["r2"] is not None

def test_transform_preview_is_non_mutating():
 p=plan_transformations({**BASE,"operations":[{"column":"x","operation":"standardize"},{"column":"z","operation":"winsorize","parameters":{"lower_quantile":.1,"upper_quantile":.9}}]}); assert p["automatic_application"] is False
 v=preview_transformations({**BASE,"operations":p["operations"],"preview_rows":3}); assert v["source_dataset_mutated"] is False and "x__standardize" in v["generated_columns"]

def test_pca_explicit_and_exploratory():
 p=analyze_pca({**BASE,"columns":["x","y","z"],"standardize":True,"components":2}); assert len(p["components"])==2 and p["cluster_structure_inferred"] is False and p["missing_rows_excluded_from_pca"]==1

def test_visual_studio_snapshot_export():
 v=build_visualization_plan(BASE); assert v["automatic_render"] is False and any(x["figure_type"]=="missingness-matrix" for x in v["figures"])
 s=build_studio(BASE); assert s["source_dataset_mutated"] is False and len(s["studio_hash"])==64
 snap=build_snapshot({**BASE,"settings":{"correlation":"pearson"}}); assert snap["automatic_persistence"] is False and len(snap["snapshot"]["snapshot_hash"])==64
 ex=build_export_plan({**BASE,"formats":["json","pdf","svg"]}); assert ex["automatic_file_write"] is False

def test_core_plan_reference_first():
 c=build_core_object_plan({**BASE,"session_id":"s1","analysis_id":"eda1"}); assert c["automatic_core_submission"] is False and c["binding"]["data"]["object_type"]=="artifact"

def test_limits_and_invalid_settings():
 with pytest.raises(EDAStudioError): analyze_correlations({**BASE,"method":"kendall"})
 with pytest.raises(EDAStudioError): plan_transformations({**BASE,"operations":[{"column":"x","operation":"magic"}]})
