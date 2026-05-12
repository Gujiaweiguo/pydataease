def _sid(value: int | None) -> str | None:
    """Convert a BigInteger ID to its string representation for JSON-safe BigInt precision."""
    if value is None:
        return None
    return str(value)
