from __future__ import annotations

from urllib.parse import urlencode

import httpx

from .base import BasePlatformProvider, PlatformUserInfo


class WeComPlatformProvider(BasePlatformProvider):
    platform_type = "wecom"
    _BASE_URL = "https://qyapi.weixin.qq.com"

    def validate_config(self, config: dict[str, str]) -> list[str]:
        errors: list[str] = []
        for key in ("corpId", "agentId", "secret", "callbackDomain"):
            if not config.get(key):
                errors.append(f"Missing required config: {key}")
        return errors

    async def get_authorize_url(self, redirect_uri: str, state: str) -> str:
        params = {
            "appid": self.config["corpId"],
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "snsapi_base",
            "agentid": self.config["agentId"],
            "state": state,
        }
        return f"https://open.weixin.qq.com/connect/oauth2/authorize?{urlencode(params)}#wechat_redirect"

    async def handle_callback(self, code: str, state: str, redirect_uri: str) -> PlatformUserInfo:
        del state, redirect_uri
        access_token = await self._get_access_token()
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{self._BASE_URL}/cgi-bin/auth/getuserinfo",
                params={"access_token": access_token, "code": code},
            )
            data = resp.json()
            self._raise_if_error(data, "Failed to fetch WeCom user info")
            user_id = str(data.get("userid", ""))
            if not user_id:
                raise ValueError("WeCom callback returned empty userid")

            detail_resp = await client.get(
                f"{self._BASE_URL}/cgi-bin/user/get",
                params={"access_token": access_token, "userid": user_id},
            )
            detail = detail_resp.json()
            self._raise_if_error(detail, "Failed to fetch WeCom user detail")

        return PlatformUserInfo(
            platform=self.platform_type,
            external_id=user_id,
            username=detail.get("alias") or detail.get("userid"),
            display_name=detail.get("name"),
            email=detail.get("email"),
            mobile=detail.get("mobile"),
            avatar_url=detail.get("avatar"),
        )

    async def test_connection(self) -> dict[str, str | bool]:
        try:
            await self._get_access_token()
        except Exception as exc:
            return {"success": False, "message": str(exc)}
        return {"success": True, "message": "Connection test passed"}

    async def _get_access_token(self) -> str:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{self._BASE_URL}/cgi-bin/gettoken",
                params={"corpid": self.config["corpId"], "corpsecret": self.config["secret"]},
            )
            data = resp.json()
            self._raise_if_error(data, "Failed to obtain WeCom access token")
            token = str(data.get("access_token", ""))
            if not token:
                raise ValueError("WeCom access token is empty")
            return token

    @staticmethod
    def _raise_if_error(data: dict[str, object], message: str) -> None:
        errcode = data.get("errcode", 0)
        if errcode not in (0, None):
            errmsg = data.get("errmsg", "unknown error")
            raise ValueError(f"{message}: {errmsg}")
