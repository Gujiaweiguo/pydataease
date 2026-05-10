from __future__ import annotations

import sys

import httpx


def main() -> None:
    try:
        resp = httpx.get("http://localhost:8000/health", timeout=5)
        if resp.status_code == 200:
            sys.exit(0)
    except Exception:
        pass
    sys.exit(1)


if __name__ == "__main__":
    main()
