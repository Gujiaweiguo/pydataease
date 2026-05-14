"""JSON serialization that converts large integers (>2^53-1) to strings.

Mirrors the Java backend's ``@JsonSerialize(using = ToStringSerializer.class)`` pattern.
JavaScript ``Number.MAX_SAFE_INTEGER = 2^53 - 1 = 9007199254740991``.
"""
from __future__ import annotations

import json
from typing import Any

from starlette.responses import JSONResponse as _JSONResponse

MAX_SAFE_INTEGER = 2**53 - 1  # 9007199254740991


class BigIntEncoder(json.JSONEncoder):
    """JSON encoder that serializes integers exceeding JS safe range as strings."""

    def encode(self, o: Any) -> str:
        return super().encode(self._convert(o))

    def iterencode(self, o: Any, _one_shot: bool = True) -> Any:
        return super().iterencode(self._convert(o), _one_shot)

    @classmethod
    def _convert(cls, obj: Any) -> Any:
        """Recursively walk the data structure, converting large ints to strings."""
        if isinstance(obj, int) and not isinstance(obj, bool):
            if abs(obj) > MAX_SAFE_INTEGER:
                return str(obj)
            return obj
        if isinstance(obj, dict):
            return {k: cls._convert(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [cls._convert(item) for item in obj]
        return obj


class BigIntJSONResponse(_JSONResponse):
    """JSON response that uses :class:`BigIntEncoder` for serialization."""

    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            cls=BigIntEncoder,
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
