from __future__ import annotations

from app.services.param_resolver import ParamResolver, ResolutionSource


def test_basic_resolution() -> None:
    resolver = ParamResolver()

    resolved, audit = resolver.resolve(["foo"], [ResolutionSource(kind="embedContext", key="foo", raw_value="bar")])

    assert resolved["foo"].value == "bar"
    assert resolved["foo"].winning_source == "embedContext"
    assert audit == [
        {
            "key": "foo",
            "winning_source": "embedContext",
            "winning_priority": 60,
            "value_state": "present",
            "overridden_sources": [],
            "required": False,
            "error": None,
        }
    ]


def test_priority_prefers_higher_source() -> None:
    resolver = ParamResolver()

    resolved, _ = resolver.resolve(
        ["foo"],
        [
            ResolutionSource(kind="embedContext", key="foo", raw_value="embed"),
            ResolutionSource(kind="sysVariable", key="foo", raw_value="system"),
        ],
    )

    assert resolved["foo"].value == "system"
    assert resolved["foo"].winning_source == "sysVariable"
    assert resolved["foo"].overridden_sources == ["embedContext"]


def test_missing_optional_key_uses_default() -> None:
    resolver = ParamResolver()

    resolved, audit = resolver.resolve(["foo"], [], defaults={"foo": "fallback"})

    assert resolved["foo"].value == "fallback"
    assert resolved["foo"].winning_source == "defaultValue"
    assert audit[0]["error"] is None


def test_missing_required_key_sets_audit_error() -> None:
    resolver = ParamResolver()

    resolved, audit = resolver.resolve(["foo"], [], required_keys=["foo"])

    assert resolved["foo"].value is None
    assert resolved["foo"].value_state == "missing"
    assert resolved["foo"].audit_meta["error"] == "missing_required"
    assert audit[0]["error"] == "missing_required"


def test_normalization_string_values_pass_through() -> None:
    resolver = ParamResolver()

    resolved, _ = resolver.resolve(["foo"], [ResolutionSource(kind="embedContext", key="foo", raw_value="hello")])

    assert resolved["foo"].value == "hello"
    assert resolved["foo"].value_state == "present"


def test_multiple_keys_resolve_in_one_call() -> None:
    resolver = ParamResolver()

    resolved, _ = resolver.resolve(
        ["foo", "bar"],
        [
            ResolutionSource(kind="embedContext", key="foo", raw_value="alpha"),
            ResolutionSource(kind="outerParam", key="bar", raw_value="beta"),
        ],
    )

    assert resolved["foo"].value == "alpha"
    assert resolved["bar"].value == "beta"


def test_audit_trail_contains_winning_and_overridden_sources() -> None:
    resolver = ParamResolver()

    resolved, audit = resolver.resolve(
        ["foo"],
        [
            ResolutionSource(kind="dataFilingContext", key="foo", raw_value="filing"),
            ResolutionSource(kind="embedContext", key="foo", raw_value="embed"),
        ],
    )

    assert resolved["foo"].winning_source == "embedContext"
    assert resolved["foo"].overridden_sources == ["dataFilingContext"]
    assert audit[0]["winning_source"] == "embedContext"
    assert audit[0]["overridden_sources"] == ["dataFilingContext"]


def test_missing_key_without_default_has_missing_state() -> None:
    resolver = ParamResolver()

    resolved, _ = resolver.resolve(["foo"], [])

    assert resolved["foo"].value_state == "missing"
    assert resolved["foo"].winning_source == "missing"
