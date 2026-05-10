#!/usr/bin/env python3
"""Validate a live PyDataEase deployment.

This script is intended for cutover smoke validation. It checks health,
protected API behavior, representative domains, database reachability hints,
and optional WebSocket connectivity.
"""

from __future__ import annotations

import argparse
import asyncio
from typing import Any

import httpx
from jose import jwt

from app.settings.config import get_settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a running pydataease backend deployment.")
    parser.add_argument("--base-url", required=True, help="Base URL such as http://localhost:8000")
    parser.add_argument("--token", help="Existing auth token for protected endpoint checks.")
    parser.add_argument("--user-id", type=int, default=7, help="Fallback JWT user id when generating a local validation token.")
    parser.add_argument("--org-id", type=int, default=9, help="Fallback JWT organization id when generating a local validation token.")
    parser.add_argument("--timeout", type=float, default=10.0, help="HTTP/WebSocket timeout in seconds.")
    parser.add_argument("--skip-websocket", action="store_true", help="Skip the websocket connectivity check.")
    parser.add_argument("--strict-login", action="store_true", help="Require /de2api/login/localLogin to return a token before protected checks continue.")
    return parser


def build_fallback_token(user_id: int, org_id: int) -> str:
    settings = get_settings()
    return jwt.encode({"uid": user_id, "oid": org_id}, settings.secret_key, algorithm=settings.jwt_algorithm)


async def fetch_login_token(client: httpx.AsyncClient) -> str | None:
    response = await client.post("/de2api/login/localLogin")
    if response.status_code != 200:
        return None
    payload = response.json()
    data = payload.get("data") if isinstance(payload, dict) else None
    token = data.get("token") if isinstance(data, dict) else None
    return str(token) if token else None


async def check_websocket(base_url: str, timeout: float) -> tuple[bool, str]:
    try:
        import websockets
    except ImportError:
        return False, "websockets package unavailable in runtime environment"

    ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://") + "/websocket"
    try:
        async with websockets.connect(ws_url, open_timeout=timeout, close_timeout=timeout) as socket:
            message = await asyncio.wait_for(socket.recv(), timeout=timeout)
            return True, str(message)
    except Exception as exc:  # pragma: no cover - live validation path
        return False, str(exc)


async def run_validation(args: argparse.Namespace) -> int:
    failures: list[str] = []
    settings = get_settings()
    async with httpx.AsyncClient(base_url=args.base_url.rstrip("/"), timeout=args.timeout) as client:
        health = await client.get("/health")
        print(f"[health] {health.status_code} {health.text}")
        if health.status_code != 200:
            failures.append("health endpoint failed")

        unauthorized = await client.get(f"{settings.api_prefix}/datasource/query/bootstrap")
        print(f"[auth-block] {unauthorized.status_code} {unauthorized.text}")
        if unauthorized.status_code != 401:
            failures.append("protected datasource endpoint did not block unauthenticated access")

        login_token = await fetch_login_token(client)
        token = args.token or login_token or build_fallback_token(args.user_id, args.org_id)
        if args.strict_login and not login_token:
            failures.append("strict login enabled but /de2api/login/localLogin did not return a token")

        headers = {"X-DE-TOKEN": token}
        protected_checks: list[tuple[str, str, dict[str, Any] | None]] = [
            ("GET", f"{settings.api_prefix}/menu/query", None),
            ("POST", f"{settings.api_prefix}/datasetTree/tree", {"busiFlag": "dataset"}),
            ("POST", f"{settings.api_prefix}/dataVisualization/tree", {"busiFlag": "dashboard"}),
            ("POST", f"{settings.api_prefix}/exportCenter/exportTasks/1", None),
        ]

        for method, path, payload in protected_checks:
            response = await client.request(method, path, headers=headers, json=payload)
            print(f"[{path}] {response.status_code}")
            if response.status_code >= 500:
                failures.append(f"{path} returned server error {response.status_code}")
            if response.status_code == 401:
                failures.append(f"{path} rejected the validation token")

        db_hint = await client.get(f"{settings.api_prefix}/sysParameter/requestTimeOut")
        print(f"[db-hint] {db_hint.status_code} {db_hint.text}")
        if db_hint.status_code != 200:
            failures.append("system endpoint check failed; database/application readiness is suspect")

        if not args.skip_websocket:
            ok, detail = await check_websocket(args.base_url.rstrip("/"), args.timeout)
            print(f"[websocket] {'ok' if ok else 'fail'} {detail}")
            if not ok:
                failures.append("websocket connectivity failed")

    if failures:
        print("\nValidation FAILED:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nValidation PASSED")
    return 0


def main() -> None:
    args = build_parser().parse_args()
    raise SystemExit(asyncio.run(run_validation(args)))


if __name__ == "__main__":
    main()
