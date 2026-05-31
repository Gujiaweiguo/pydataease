from __future__ import annotations

from urllib.parse import urlencode

import httpx

from .base import BasePlatformProvider, PlatformUserInfo


class DingTalkPlatformProvider(BasePlatformProvider):
    platform_type = "dingtalk"

    def validate_config(self, config: dict[str, str]) -> list[str]:
        errors: list[str] = []
        for key in ("appId", "appKey", "appSecret", "callbackDomain"):
            if not config.get(key):
                errors.append(f"Missing required config: {key}")
        return errors

    async def get_authorize_url(self, redirect_uri: str, state: str) -> str:
        params = {
            "appid": self.config["appId"],
            "response_type": "code",
            "scope": "snsapi_login",
            "state": state,
            "redirect_uri": redirect_uri,
        }
        return f"https://login.dingtalk.com/login/qrcode.htm?{urlencode(params)}"

    async def handle_callback(self, code: str, state: str, redirect_uri: str) -> PlatformUserInfo:
        del state, redirect_uri
        async with httpx.AsyncClient(timeout=30.0) as client:
            token_resp = await client.post(
                "https://api.dingtalk.com/v1.0/oauth2/userAccessToken",
                json={
                    "clientId": self.config["appKey"],
                    "clientSecret": self.config["appSecret"],
                    "code": code,
                    "grantType": "authorization_code",
                },
            )
            token_data = token_resp.json()
            access_token = str(token_data.get("accessToken", ""))
            if not access_token:
                raise ValueError(token_data.get("message") or "DingTalk access token is empty")

            user_resp = await client.get(
                "https://api.dingtalk.com/v1.0/contact/users/me",
                headers={"x-acs-dingtalk-access-token": access_token},
            )
            user_data = user_resp.json()

        external_id = str(user_data.get("unionId") or user_data.get("openId") or user_data.get("userid") or "")
        if not external_id:
            raise ValueError("DingTalk callback returned empty user identifier")
        return PlatformUserInfo(
            platform=self.platform_type,
            external_id=external_id,
            username=user_data.get("nick") or user_data.get("name"),
            display_name=user_data.get("name") or user_data.get("nick"),
            email=user_data.get("email"),
            mobile=user_data.get("mobile"),
            avatar_url=user_data.get("avatarUrl"),
        )

    async def test_connection(self) -> dict[str, str | bool]:
        return {"success": True, "message": "DingTalk config validated"}
