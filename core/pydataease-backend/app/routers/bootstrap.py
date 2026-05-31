import base64

# pyright: reportMissingImports=false

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user  # pyright: ignore[reportImplicitRelativeImport]
from app.dependencies.database import get_db  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.services.font_service import FontPayload, get_font_service  # pyright: ignore[reportImplicitRelativeImport]
from app.services.auth_provider_service import AuthProviderService, get_auth_provider_service  # pyright: ignore[reportImplicitRelativeImport]
from app.services.permission_service import PermissionService, get_permission_service  # pyright: ignore[reportImplicitRelativeImport]
from app.services.sys_setting_service import SysSettingService, get_sys_setting_service  # pyright: ignore[reportImplicitRelativeImport]
from app.services.template_market_service import get_template_market_service  # pyright: ignore[reportImplicitRelativeImport]
from app.services.watermark_service import WatermarkService, get_watermark_service  # pyright: ignore[reportImplicitRelativeImport]
from app.utils.rsa_utils import get_dekey_response  # pyright: ignore[reportImplicitRelativeImport]

from app.settings.defaults import SETTINGS_DEFAULTS, is_feature_enabled  # pyright: ignore[reportImplicitRelativeImport]

router = APIRouter()


@router.get("/xpackModel")
async def get_xpack_model():
    return None


@router.get("/model")
async def get_model():
    return None


@router.get("/sysParameter/i18nOptions")
async def get_i18n_options(service=Depends(get_sys_setting_service)):
    return await service.get_i18n_options()


@router.get("/sysParameter/defaultSettings")
async def get_default_settings(service=Depends(get_sys_setting_service)):
    return await service.get_default_settings()


@router.get("/sysParameter/ui")
async def get_sys_parameter_ui(service=Depends(get_sys_setting_service)):
    return await service.get_ui_settings()


@router.get("/sysParameter/appearance")
async def get_appearance_settings(
    service: SysSettingService = Depends(get_sys_setting_service),
) -> dict[str, str]:
    keys = [key for key in SETTINGS_DEFAULTS if key.startswith("ui.")]
    keys.append("basic.siteName")
    values: dict[str, str] = {}
    for key in keys:
        values[key] = await service.get_setting(key) or SETTINGS_DEFAULTS[key]
    return values


@router.get("/sysParameter/feature/status")
async def get_feature_status(
    service: SysSettingService = Depends(get_sys_setting_service),
) -> dict[str, bool]:
    feature_keys = [key for key in SETTINGS_DEFAULTS if key.startswith("feature.")]
    status_map: dict[str, bool] = {}
    for key in feature_keys:
        value = await service.get_setting(key)
        if value is None:
            value = SETTINGS_DEFAULTS[key]
        status_map[key] = value == "true"
    return status_map


@router.get("/sysParameter/defaultLogin")
async def get_default_login(service=Depends(get_sys_setting_service)):
    return await service.get_default_login()


@router.get("/setting/authentication/status")
async def get_authentication_status(service: AuthProviderService = Depends(get_auth_provider_service)):
    return await service.get_auth_status()


@router.get("/sysParameter/shareBase")
async def get_share_base(service=Depends(get_sys_setting_service)):
    return await service.get_share_base()


@router.get("/watermark/public")
async def get_public_watermark(
    session: AsyncSession = Depends(get_db),
    service: WatermarkService = Depends(get_watermark_service),
) -> dict[str, object]:
    feature_enabled = await is_feature_enabled(session, "feature.watermark.enabled")
    watermark = await service.get_watermark_info(feature_enabled=feature_enabled)
    return WatermarkService.build_public_payload(watermark)


@router.get("/typeface/defaultFont")
async def get_default_font(service=Depends(get_font_service)):
    return await service.default_fonts()


@router.get("/typeface/listFont")
async def get_list_font(service=Depends(get_font_service)):
    return await service.list_fonts()


@router.get("/typeface/download/{font_id}")
async def download_font(font_id):
    # Return empty response for null font IDs or non-existent fonts
    if font_id is None or font_id == "null" or font_id == "None":
        return {"data": None, "msg": "no font"}
    return {"data": None, "msg": "font not found"}


@router.post("/typeface/create")
async def create_font(data: FontPayload, service=Depends(get_font_service)):
    await service.create_font(data)
    return None


@router.post("/typeface/edit")
async def edit_font(data: FontPayload, service=Depends(get_font_service)):
    await service.edit_font(data)
    return None


@router.post("/typeface/delete/{font_id}")
async def delete_font(font_id: int, service=Depends(get_font_service)):
    await service.delete_font(font_id)
    return None


@router.post("/typeface/uploadFile")
async def upload_font_file(file: UploadFile, service=Depends(get_font_service)):
    return await service.upload_file(file)


@router.get("/templateMarket/search")
async def get_template_market_search(service=Depends(get_template_market_service)):
    return await service.search()


@router.get("/templateMarket/searchPreview")
async def get_template_market_search_preview(service=Depends(get_template_market_service)):
    return await service.search_preview()


@router.get("/templateMarket/categories")
async def get_template_market_categories(service=Depends(get_template_market_service)):
    return await service.get_categories()


@router.get("/templateMarket/categoriesObject")
async def get_template_market_categories_object(service=Depends(get_template_market_service)):
    return await service.get_categories_object()


@router.get("/templateMarket/searchRecommend")
async def get_template_market_search_recommend(service=Depends(get_template_market_service)):
    return await service.search_recommend()


@router.post("/license/validate")
async def validate_license():
    return {"status": "valid", "license": "community", "edition": "Community Edition", "serialNo": "", "remark": "", "expired": False}


@router.get("/license/version")
async def get_license_version():
    return {"version": "2.10", "type": "community"}


@router.get("/aiBase/findTargetUrl")
async def find_ai_target_url():
    return {"url": "", "enable": False}


@router.get("/sysParameter/sqlbot")
async def get_sqlbot_settings(service: SysSettingService = Depends(get_sys_setting_service)):
    return await service.get_sqlbot_settings()


@router.post("/sysParameter/sqlbot")
async def save_sqlbot_settings(
    payload: dict[str, object],
    _: TokenUser = Depends(get_current_user),
    service: SysSettingService = Depends(get_sys_setting_service),
):
    return await service.save_sqlbot_settings(payload)


@router.post("/msg-center/count")
async def get_msg_count():
    return 0


@router.get("/dekey")
async def get_dekey():
    return get_dekey_response()


@router.post("/exportCenter/exportLimit")
async def export_limit(_: TokenUser = Depends(get_current_user)) -> str:
    return "100000"


@router.get("/symmetricKey")
async def symmetric_key() -> str:
    """Return the fixed symmetric key used for engine config encryption/decryption.

    The frontend uses this key with AES-128-CBC (IV='0000000000000000') to decrypt
    sensitive configuration fields (e.g., engine configuration in /engine/getEngine).
    """
    # Fixed key must match _SYMMETRIC_KEY in system_service.py
    return base64.b64encode(b"DataEase@SymKey!").decode("ascii")


@router.get("/engine/supportSetKey")
async def support_set_key(_: TokenUser = Depends(get_current_user)) -> bool:
    """Whether the engine supports the 'set key' feature for API datasources."""
    return False


@router.get("/sqlbot/datasource")
async def get_sqlbot_datasource_list(
    dsId: int | None = None,  # noqa: N803 — match Java query-param name
    tableId: int | None = None,  # noqa: N803
) -> list[object]:
    """Return available data sources for the SQL Bot assistant.

    Stub — requires external AI service (SQLBot) which is not bundled in
    the community edition.
    """
    return []


@router.get("/sqlbot/dataset/{dv_info}")
async def get_sqlbot_dataset_list(dv_info: str) -> list[object]:
    """Return available datasets for the SQL Bot assistant.

    Stub — requires external AI service (SQLBot) which is not bundled in
    the community edition.
    """
    return []


@router.post("/resource/checkPermission/{resource_id}")
async def check_resource_permission(
    resource_id: int,
    resource_type: str | None = None,
    permission_type: str | None = None,
    user: TokenUser = Depends(get_current_user),  # BUG-060 fix: require auth
    service: PermissionService = Depends(get_permission_service),
) -> bool:
    """Check if the current user has the requested resource permission."""
    resolved_type = (resource_type or "").strip().lower() or _resource_type_for_permission_check(resource_id)
    resolved_permission = (permission_type or "view").strip().lower() or "view"
    return await service.has_resource_permission(user, resolved_type, resolved_permission)


def _resource_type_for_permission_check(resource_id: int) -> str:
    if resource_id == 2:
        return "screen"
    if resource_id == 3:
        return "dataset"
    if resource_id == 4:
        return "datasource"
    return "dashboard"
