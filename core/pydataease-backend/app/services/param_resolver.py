from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any

SOURCE_PRIORITY: dict[str, int] = {
    "sysVariable": 100,
    "outerParam": 80,
    "embedContext": 60,
    "dataFilingContext": 40,
    "defaultValue": 20,
}


@dataclass(slots=True)
class ResolutionSource:
    kind: str
    key: str
    raw_value: Any
    source_meta: dict[str, Any] | None = None


@dataclass(slots=True)
class ResolvedParameter:
    key: str
    value: Any
    value_state: str
    winning_source: str
    winning_priority: int
    overridden_sources: list[str]
    audit_meta: dict[str, Any] = field(default_factory=dict)


class ParamResolver:
    """Canonical 5-stage parameter resolution chain."""

    def resolve(
        self,
        keys: list[str],
        sources: list[ResolutionSource],
        required_keys: list[str] | None = None,
        defaults: dict[str, Any] | None = None,
    ) -> tuple[dict[str, ResolvedParameter], list[dict[str, Any]]]:
        required = set(required_keys or [])
        default_values = defaults or {}
        grouped = self._group_sources(keys, sources)
        resolved_map: dict[str, ResolvedParameter] = {}
        audit_trail: list[dict[str, Any]] = []

        for key in keys:
            parsed_sources = [self._parse_source(source) for source in grouped.get(key, [])]
            normalized_sources = [self._normalize_source(source) for source in parsed_sources]

            winning_source = self._pick_winner(key, normalized_sources, default_values)
            overridden_sources = [source["kind"] for source in normalized_sources if source is not winning_source]
            error = "missing_required" if key in required and winning_source["value_state"] == "missing" else None

            resolved = ResolvedParameter(
                key=key,
                value=winning_source["value"],
                value_state=winning_source["value_state"],
                winning_source=winning_source["kind"],
                winning_priority=winning_source["priority"],
                overridden_sources=overridden_sources,
                audit_meta={
                    "key": key,
                    "winning_source": winning_source["kind"],
                    "winning_priority": winning_source["priority"],
                    "value_state": winning_source["value_state"],
                    "overridden_sources": overridden_sources,
                    "required": key in required,
                    "error": error,
                    "candidates": [
                        {
                            "kind": source["kind"],
                            "priority": source["priority"],
                            "value_state": source["value_state"],
                            "source_meta": source["source_meta"],
                        }
                        for source in normalized_sources
                    ],
                },
            )
            resolved_map[key] = resolved
            audit_trail.append(
                {
                    "key": key,
                    "winning_source": resolved.winning_source,
                    "winning_priority": resolved.winning_priority,
                    "value_state": resolved.value_state,
                    "overridden_sources": resolved.overridden_sources,
                    "required": key in required,
                    "error": error,
                }
            )

        return resolved_map, audit_trail

    def _group_sources(self, keys: list[str], sources: list[ResolutionSource]) -> dict[str, list[ResolutionSource]]:
        grouped = {key: [] for key in keys}
        key_set = set(keys)
        for source in sources:
            if source.key in key_set:
                grouped[source.key].append(source)
        return grouped

    def _parse_source(self, source: ResolutionSource) -> dict[str, Any]:
        return {
            "kind": source.kind,
            "key": source.key,
            "raw_value": source.raw_value,
            "value": self._parse_value(source.raw_value),
            "priority": SOURCE_PRIORITY.get(source.kind, 0),
            "source_meta": source.source_meta,
        }

    def _normalize_source(self, source: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(source)
        normalized["value_state"] = self._determine_value_state(source["value"])
        return normalized

    def _pick_winner(
        self,
        key: str,
        normalized_sources: list[dict[str, Any]],
        defaults: dict[str, Any],
    ) -> dict[str, Any]:
        candidates = [source for source in normalized_sources if source["value_state"] != "missing"]
        if key in defaults:
            default_value = self._parse_value(defaults[key])
            candidates.append(
                {
                    "kind": "defaultValue",
                    "key": key,
                    "raw_value": defaults[key],
                    "value": default_value,
                    "priority": SOURCE_PRIORITY["defaultValue"],
                    "source_meta": {"injected": True},
                    "value_state": self._determine_value_state(default_value),
                }
            )
        if candidates:
            candidates.sort(key=lambda item: item["priority"], reverse=True)
            return candidates[0]
        return {
            "kind": "missing",
            "key": key,
            "raw_value": None,
            "value": None,
            "priority": 0,
            "source_meta": None,
            "value_state": "missing",
        }

    def _parse_value(self, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        stripped = value.strip()
        lowered = stripped.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        if re.fullmatch(r"[+-]?\d+", stripped):
            try:
                return int(stripped)
            except ValueError:
                return value
        if re.fullmatch(r"[+-]?(?:\d+\.\d*|\d*\.\d+|\d+[eE][+-]?\d+|\d+\.\d*[eE][+-]?\d+|\d*\.\d+[eE][+-]?\d+)", stripped):
            try:
                return float(stripped)
            except ValueError:
                return value
        return value

    def _determine_value_state(self, value: Any) -> str:
        if value is _MISSING:
            return "missing"
        if value is None:
            return "explicit_null"
        if isinstance(value, str) and value == "":
            return "empty_string"
        return "present"


_MISSING = object()
