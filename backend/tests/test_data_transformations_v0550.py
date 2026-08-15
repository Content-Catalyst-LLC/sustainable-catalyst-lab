import math
import pytest

from app.data_transformations import DataTransformationError, convert_unit_value, join_datasets, normalize_plan, transform_dataset


def test_normalize_plan_rejects_unknown_operation():
    with pytest.raises(DataTransformationError):
        normalize_plan({"operations": [{"type": "python", "code": "import os"}]})


def test_derived_variable_uses_safe_equation_engine_and_lineage():
    out = transform_dataset({"rows": [{"x": 1, "y": 2}, {"x": 3, "y": 4}], "plan": {"operations": [{"type": "derive", "name": "z", "expression": "x + 2*y", "unit": "m"}]}})["result"]
    assert [row["z"] for row in out["rows"]] == [5.0, 11.0]
    assert out["derivedVariables"][0]["referencedSymbols"] == ["x", "y"]
    assert out["lineage"][0]["inputHash"] != out["lineage"][0]["outputHash"]
    assert len(out["resultHash"]) == 64


def test_derived_variable_rejects_arbitrary_code():
    with pytest.raises(DataTransformationError):
        transform_dataset({"rows": [{"x": 1}], "plan": {"operations": [{"type": "derive", "name": "z", "expression": "__import__('os').system('id')"}]}})


def test_filter_scale_and_select_pipeline():
    result = transform_dataset({"rows": [{"x": 1, "group": "a"}, {"x": 2, "group": "b"}, {"x": 3, "group": "a"}], "plan": {"operations": [
        {"type": "filter", "column": "group", "operator": "eq", "value": "a"},
        {"type": "scale", "column": "x", "target": "x_centered", "method": "center"},
        {"type": "select", "columns": ["group", "x_centered"]},
    ]}})["result"]
    assert result["rowCount"] == 2
    assert result["columns"] == ["group", "x_centered"]
    assert [r["x_centered"] for r in result["rows"]] == [-1.0, 1.0]


def test_unit_conversion_catalog_is_dimension_aware():
    assert convert_unit_value(100, "cm", "m") == pytest.approx(1)
    assert convert_unit_value(0, "degC", "K") == pytest.approx(273.15)
    assert convert_unit_value(32, "degF", "degC") == pytest.approx(0, abs=1e-10)
    with pytest.raises(DataTransformationError):
        convert_unit_value(1, "kg", "m")


def test_unit_conversion_checks_declared_unit():
    with pytest.raises(DataTransformationError):
        transform_dataset({"rows": [{"length": 100}], "units": {"length": "mm"}, "plan": {"operations": [{"type": "unit-convert", "column": "length", "fromUnit": "cm", "toUnit": "m"}]}})


def test_imputation_is_explicit_and_warned():
    result = transform_dataset({"rows": [{"x": 1}, {"x": None}, {"x": 3}], "plan": {"operations": [{"type": "impute", "column": "x", "method": "mean"}]}})["result"]
    assert result["rows"][1]["x"] == pytest.approx(2)
    assert "Imputed 1 missing" in result["warnings"][0]


def test_rename_can_make_column_safe_for_later_derived_variable():
    result = transform_dataset({"rows": [{"air temp": 20}], "plan": {"operations": [{"type": "rename", "from": "air temp", "to": "air_temp"}, {"type": "derive", "name": "kelvin_approx", "expression": "air_temp + 273.15", "unit": "K"}]}})["result"]
    assert result["rows"][0]["kelvin_approx"] == pytest.approx(293.15)


def test_left_join_preserves_unmatched_rows_and_hashes():
    result = join_datasets({"leftRows": [{"id": 1, "x": 4}, {"id": 2, "x": 5}], "rightRows": [{"id": 1, "label": "A"}], "leftKey": "id", "rightKey": "id", "how": "left"})["result"]
    assert result["rowCount"] == 2
    assert result["rows"][0]["label"] == "A"
    assert result["rows"][1]["label"] is None
    assert result["unmatchedLeftRows"] == 1
    assert len(result["joinHash"]) == 64


def test_inner_join_can_expand_but_is_bounded():
    result = join_datasets({"leftRows": [{"id": 1}], "rightRows": [{"id": 1, "v": "a"}, {"id": 1, "v": "b"}], "leftKey": "id", "how": "inner"})["result"]
    assert [r["v"] for r in result["rows"]] == ["a", "b"]


def test_cast_rejects_non_integer_fraction():
    with pytest.raises(DataTransformationError):
        transform_dataset({"rows": [{"x": 1.2}], "plan": {"operations": [{"type": "cast", "column": "x", "dataType": "integer"}]}})
