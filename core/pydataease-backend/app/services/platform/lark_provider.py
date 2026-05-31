from __future__ import annotations

from urllib.parse import urlencode

import httpx

from .base import BasePlatformProvider, PlatformUserInfo


class LarkPlatformProvider(BasePlatformProvider):
    platform_type = "lark"
    base_url = "https://open.feishu.cn"

    def validate_config(self, config: dict[str, str]) -> list[str]:
        errors: list[str] = []
        for key in ("appId", "appSecret", "callbackDomain"):
            if not config.get(key):
                errors.append(f"Missing required config: {key}")
        return errors

    async def get_authorize_url(self, redirect_uri: str, state: str) -> str:
        params = {
            "app_id": self.config["appId"],
            "redirect_uri": redirect_uri,
            "state": state,
        }
        return f"{self.base_url}/open-apis/authen/v1/authorize?{urlencode(params)}"

    async def handle_callback(self, code: str, state: str, redirect_uri: str) -> PlatformUserInfo:
        del state, redirect_uri
        app_access_token = await self._get_app_access_token()
        async with httpx.AsyncClient(timeout=30.0) as client:
            token_resp = await client.post(
                f"{self.base_url}/open-apis/authen/v1/oidc/access_token",
                json={"grant_type": "authorization_code", "code": code},
                headers={"Authorization": f"Bearer {app_access_token}"},
            )
            token_data = token_resp.json()
            self._raise_if_error(token_data, "Failed to obtain Lark user access token")
            token_payload = token_data.get("data", token_data)
            user_access_token = str(token_payload.get("access_token", ""))
            if not user_access_token:
                raise ValueError("Lark user access token is empty")

            user_resp = await client.get(
                f"{self.base_url}/open-apis/authen/v1/user_info",
                headers={"Authorization": f"Bearer {user_access_token}"},
            )
            user_data = user_resp.json()
            self._raise_if_error(user_data, "Failed to fetch Lark user info")

        payload = user_data.get("data", user_data)
        external_id = str(payload.get("open_id") or payload.get("union_id") or "")
        if not external_id:
            raise ValueError("Lark callback returned empty user identifier")
        return PlatformUserInfo(
            platform=self.platform_type,
            external_id=external_id,
            username=payload.get("name") or payload.get("en_name"),
            display_name=payload.get("name") or payload.get("en_name"),
            email=payload.get("email"),
            mobile=payload.get("mobile"),
            avatar_url=payload.get("avatar_url") or payload.get("avatar_thumb"),
        )

    async def test_connection(self) -> dict[str, str | bool]:
        try:
            await self._get_app_access_token()
        except Exception as exc:
            return {"success": False, "message": str(exc)}
        return {"success": True, "message": "Connection test passed"}

    async def _get_app_access_token(self) -> str:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base_url}/open-apis/auth/v3/app_access_token/internal",
                json={"app_id": self.config["appId"], "app_secret": self.config["appSecret"]},
            )
            data = resp.json()
            self._raise_if_error(data, "Failed to obtain Lark app access token")
            token = str(data.get("app_access_token") or data.get("tenant_access_token") or "")
            if not token:
                raise ValueError("Lark app access token is empty")
            return token

    @staticmethod
    def _raise_if_error(data: dict[str, object], message: str) -> None:
        code = data.get("code", 0)
        if code not in (0, None):
            msg = data.get("msg") or data.get("message") or "unknown error"
            raise ValueError(f"{message}: {msg}")


class LarkSuitePlatformProvider(LarkPlatformProvider):
    platform_type = "larksuite"
    base_url = "https://open.larksuite.com"
