from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal
from typing import Any


class ChartDataBuilder:
    @staticmethod
    def build_antv_data(
        rows: list[list[Any]],
        fields: list[dict[str, Any]],
        x_axis: list[dict[str, Any]],
        y_axis: list[dict[str, Any]],
        chart_type: str,
    ) -> list[dict[str, Any]]:
        normalized_rows = [ChartDataBuilder._row_to_dict(row, fields) for row in rows]
        if chart_type.lower() == "table":
            return normalized_rows

        dimensions = [item for item in x_axis if isinstance(item, dict)]
        metrics = [item for item in y_axis if isinstance(item, dict)]
        if not metrics:
            return normalized_rows

        data: list[dict[str, Any]] = []
        for row in normalized_rows:
            dimension_list = [
                {
                    "id": dimension.get("id"),
                    "value": row.get(ChartDataBuilder._field_key(dimension)),
                }
                for dimension in dimensions
            ]
            dimension_values = [item.get("value") for item in dimension_list if item.get("value") is not None]
            label = " / ".join(str(value) for value in dimension_values) if dimension_values else None

            for metric in metrics:
                metric_key = ChartDataBuilder._field_key(metric)
                # extField=1 (record count) uses "cnt" as the SQL alias, not "*"
                if metric_key == "*":
                    metric_key = "cnt"
                raw_value = row.get(metric_key)
                value = ChartDataBuilder._to_number(raw_value)
                if value is None and raw_value is None:
                    continue
                metric_name = metric.get("name") or metric_key
                item_label = label or str(metric_name)
                data.append(
                    {
                        "field": item_label,
                        "name": item_label,
                        "value": value if value is not None else raw_value,
                        "category": metric_name,
                        "quotaList": [{"id": metric.get("id")}],
                        "dimensionList": dimension_list,
                    }
                )
        return data if data else normalized_rows

    @staticmethod
    def _row_to_dict(row: Sequence[Any], fields: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            str(field.get("name") or f"col{index + 1}"): ChartDataBuilder._normalize_value(row[index] if index < len(row) else None)
            for index, field in enumerate(fields)
        }

    @staticmethod
    def _field_key(field: dict[str, Any]) -> str:
        return str(field.get("dataeaseName") or field.get("dataease_name") or field.get("name") or field.get("id") or "")

    @staticmethod
    def _normalize_value(value: Any) -> Any:
        if isinstance(value, Decimal):
            return float(value)
        return value

    @staticmethod
    def _to_number(value: Any) -> float | int | None:
        value = ChartDataBuilder._normalize_value(value)
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int | float):
            return value
        return None
