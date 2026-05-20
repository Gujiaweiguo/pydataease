"""Unit tests for ChartDataBuilder."""

from __future__ import annotations

from decimal import Decimal


from app.services.chart_data_builder import ChartDataBuilder


# ===========================================================================
# _normalize_value
# ===========================================================================


def test_normalize_value_decimal():
    assert ChartDataBuilder._normalize_value(Decimal("3.14")) == 3.14


def test_normalize_value_int():
    assert ChartDataBuilder._normalize_value(42) == 42


def test_normalize_value_str():
    assert ChartDataBuilder._normalize_value("hello") == "hello"


def test_normalize_value_none():
    assert ChartDataBuilder._normalize_value(None) is None


# ===========================================================================
# _to_number
# ===========================================================================


def test_to_number_int():
    assert ChartDataBuilder._to_number(42) == 42


def test_to_number_float():
    assert ChartDataBuilder._to_number(3.14) == 3.14


def test_to_number_bool():
    assert ChartDataBuilder._to_number(True) == 1
    assert ChartDataBuilder._to_number(False) == 0


def test_to_number_decimal():
    assert ChartDataBuilder._to_number(Decimal("2.5")) == 2.5


def test_to_number_string_returns_none():
    assert ChartDataBuilder._to_number("abc") is None


def test_to_number_none():
    assert ChartDataBuilder._to_number(None) is None


# ===========================================================================
# _field_key
# ===========================================================================


def test_field_key_dataease_name():
    assert ChartDataBuilder._field_key({"dataeaseName": "col_a"}) == "col_a"


def test_field_key_dataease_name_underscore():
    assert ChartDataBuilder._field_key({"dataease_name": "col_b"}) == "col_b"


def test_field_key_name_fallback():
    assert ChartDataBuilder._field_key({"name": "col_c"}) == "col_c"


def test_field_key_id_fallback():
    assert ChartDataBuilder._field_key({"id": "col_d"}) == "col_d"


def test_field_key_empty():
    assert ChartDataBuilder._field_key({}) == ""


def test_field_key_priority():
    """dataeaseName takes priority over dataease_name, name, id."""
    assert ChartDataBuilder._field_key({
        "dataeaseName": "a",
        "dataease_name": "b",
        "name": "c",
        "id": "d",
    }) == "a"


# ===========================================================================
# _row_to_dict
# ===========================================================================


def test_row_to_dict_basic():
    row = ["alpha", 42, 3.14]
    fields = [{"name": "label"}, {"name": "count"}, {"name": "price"}]
    result = ChartDataBuilder._row_to_dict(row, fields)
    assert result == {"label": "alpha", "count": 42, "price": 3.14}


def test_row_to_dict_decimal_normalized():
    row = [Decimal("9.99")]
    fields = [{"name": "cost"}]
    result = ChartDataBuilder._row_to_dict(row, fields)
    assert result == {"cost": 9.99}


def test_row_to_dict_short_row():
    """Row shorter than fields → None for missing columns."""
    row = ["only_one"]
    fields = [{"name": "first"}, {"name": "second"}]
    result = ChartDataBuilder._row_to_dict(row, fields)
    assert result == {"first": "only_one", "second": None}


def test_row_to_dict_no_name_uses_col_index():
    row = ["val"]
    fields = [{}]
    result = ChartDataBuilder._row_to_dict(row, fields)
    assert "col1" in result
    assert result["col1"] == "val"


# ===========================================================================
# build_antv_data - table chart type
# ===========================================================================


def test_build_antv_table_chart():
    rows = [["a", 1], ["b", 2]]
    fields = [{"name": "x"}, {"name": "y"}]
    result = ChartDataBuilder.build_antv_data(
        rows, fields, [], [], "table"
    )
    assert len(result) == 2
    assert result[0]["x"] == "a"
    assert result[1]["y"] == 2


# ===========================================================================
# build_antv_data - non-table, no metrics
# ===========================================================================


def test_build_antv_no_metrics_returns_normalized():
    rows = [["hello", 10]]
    fields = [{"name": "label"}, {"name": "value"}]
    result = ChartDataBuilder.build_antv_data(
        rows, fields, [], [], "bar"
    )
    assert len(result) == 1
    assert result[0]["label"] == "hello"


# ===========================================================================
# build_antv_data - bar chart with dimensions and metrics
# ===========================================================================


def test_build_antv_bar_chart():
    rows = [["Beijing", 100]]
    fields = [{"name": "city"}, {"name": "sales"}]
    x_axis = [{"id": "x1", "dataeaseName": "city"}]
    y_axis = [{"id": "y1", "dataeaseName": "sales", "name": "Sales"}]

    result = ChartDataBuilder.build_antv_data(
        rows, fields, x_axis, y_axis, "bar"
    )

    assert len(result) == 1
    item = result[0]
    assert item["value"] == 100
    assert item["category"] == "Sales"
    assert item["field"] == "Beijing"
    assert len(item["dimensionList"]) == 1
    assert item["dimensionList"][0]["value"] == "Beijing"


def test_build_antv_multiple_metrics():
    rows = [["Q1", 100, 200]]
    fields = [{"name": "quarter"}, {"name": "revenue"}, {"name": "cost"}]
    x_axis = [{"id": "x1", "dataeaseName": "quarter"}]
    y_axis = [
        {"id": "y1", "dataeaseName": "revenue", "name": "Revenue"},
        {"id": "y2", "dataeaseName": "cost", "name": "Cost"},
    ]

    result = ChartDataBuilder.build_antv_data(
        rows, fields, x_axis, y_axis, "line"
    )

    assert len(result) == 2
    assert result[0]["category"] == "Revenue"
    assert result[0]["value"] == 100
    assert result[1]["category"] == "Cost"
    assert result[1]["value"] == 200


def test_build_antv_null_metric_value_skipped():
    rows = [["Beijing", None]]
    fields = [{"name": "city"}, {"name": "sales"}]
    x_axis = [{"id": "x1", "dataeaseName": "city"}]
    y_axis = [{"id": "y1", "dataeaseName": "sales", "name": "Sales"}]

    result = ChartDataBuilder.build_antv_data(
        rows, fields, x_axis, y_axis, "bar"
    )

    # raw_value is None and value is None → skipped, falls back to normalized_rows
    assert len(result) == 1
    assert result[0]["city"] == "Beijing"


def test_build_antv_empty_rows():
    result = ChartDataBuilder.build_antv_data(
        [], [], [{"id": "x1"}], [{"id": "y1", "dataeaseName": "val", "name": "Val"}], "bar"
    )
    assert result == []


def test_build_antv_case_insensitive_table():
    rows = [["a"]]
    fields = [{"name": "col1"}]
    result = ChartDataBuilder.build_antv_data(
        rows, fields, [], [], "TABLE"
    )
    assert len(result) == 1
    assert result[0]["col1"] == "a"


def test_build_antv_metric_with_no_dimension_label():
    """When dimension values are all None, label falls back to metric name."""
    rows = [[42]]
    fields = [{"name": "val"}]
    x_axis = [{"id": "x1", "dataeaseName": "nonexistent"}]
    y_axis = [{"id": "y1", "dataeaseName": "val", "name": "Value"}]

    result = ChartDataBuilder.build_antv_data(
        rows, fields, x_axis, y_axis, "bar"
    )

    assert len(result) == 1
    assert result[0]["field"] == "Value"
