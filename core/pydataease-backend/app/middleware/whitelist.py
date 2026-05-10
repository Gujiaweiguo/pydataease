from __future__ import annotations

# Compatibility baseline: paths ported from Java WhitelistUtils.java.
# These are public (no-auth) URL patterns the frontend expects to access.
# They are NOT implementations — they preserve frontend routing compatibility.
# xpack/APISIX paths are whitelist entries only, not xpack business logic.
# Login bootstrap endpoints remain public even when mounted under /de2api.
WHITE_PATHS = {
    "/",
    "/health",
    "/login/localLogin",
    "/apisix/check",
    "/dekey",
    "/symmetricKey",
    "/index.html",
    "/model",
    "/xpackModel",
    "/swagger-resources",
    "/doc.html",
    "/panel.html",
    "/mobile.html",
    "/lark/qrinfo",
    "/lark/token",
    "/larksuite/qrinfo",
    "/larksuite/token",
    "/dingtalk/qrinfo",
    "/dingtalk/token",
    "/wecom/qrinfo",
    "/wecom/token",
    "/sysParameter/requestTimeOut",
    "/sysParameter/defaultSettings",
    "/setting/authentication/status",
    "/sysParameter/ui",
    "/sysParameter/defaultLogin",
    "/embedded/initIframe",
    "/sysParameter/i18nOptions",
    "/login/modifyInvalidPwd",
    "/perSetting/hmac/info",
}

WHITE_PREFIXES = (
    "/login/platformLogin/",
    "/static-resource/",
    "/appearance/image/",
    "/share/proxyInfo",
    "/share/validate",
    "/xpackComponent/content",
    "/xpackComponent/pluginStaticInfo",
    "/geo/",
    "/customGeo/",
    "/websocket",
    "/map/",
    "/oauth2/",
    "/mfa/",
    "/mfa/qr/",
    "/mfa/login",
    "/typeface/download",
    "/typeface/defaultFont",
    "/typeface/listFont",
    "/exportCenter/download",
    "/i18n/",
    "/communicate/image/",
    "/saml/",
    "/communicate/down/",
    "/lark/",
    "/dingtalk/",
    "/wecom/",
    "data:image",
)

STATIC_SUFFIXES = (
    ".gif",
    ".ico",
    ".js",
    ".css",
    ".svg",
    ".png",
    ".jpg",
    ".js.map",
    ".otf",
    ".ttf",
    ".woff2",
)

API_PREFIXES = ("/de2api", "/casbi/de2api", "/oidcbi/de2api")


def normalize_path(path: str) -> str:
    normalized = path or "/"
    if not normalized.startswith("/") and not normalized.startswith("data:image"):
        normalized = f"/{normalized}"
    for prefix in API_PREFIXES:
        if normalized.startswith(prefix):
            stripped = normalized[len(prefix) :]
            return stripped or "/"
    return normalized


def is_invalid_path(path: str) -> bool:
    lowered = path.lower()
    return "./" in path or ".%" in path or "%2e" in lowered or (";" in path and "?" not in path)


def is_whitelisted_path(path: str) -> bool:
    normalized = normalize_path(path)
    if is_invalid_path(normalized):
        return False
    if normalized in WHITE_PATHS:
        return True
    if normalized.endswith(STATIC_SUFFIXES):
        return True
    return any(normalized.startswith(prefix) for prefix in WHITE_PREFIXES)
