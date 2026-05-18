import base64
import os

from fastapi import APIRouter, Depends, UploadFile

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.services.font_service import FontPayload, get_font_service
from app.services.interactive_tree_service import get_interactive_tree_service
from app.services.sys_setting_service import get_sys_setting_service
from app.services.template_market_service import get_template_market_service
from app.utils.rsa_utils import get_dekey_response

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


@router.get("/sysParameter/defaultLogin")
async def get_default_login(service=Depends(get_sys_setting_service)):
    return await service.get_default_login()


@router.get("/setting/authentication/status")
async def get_authentication_status():
    return False


@router.get("/sysParameter/shareBase")
async def get_share_base(service=Depends(get_sys_setting_service)):
    return await service.get_share_base()


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


@router.post("/dataVisualization/interactiveTree")
async def get_interactive_tree(
    service=Depends(get_interactive_tree_service),
):
    return await service.get_tree()


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
async def get_sqlbot_settings():
    return {"enable": False, "url": ""}


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
    """Generate and return a Base64-encoded 128-bit AES key for symmetric encryption.

    The frontend uses this key with AES-128-CBC (IV='0000000000000000') to decrypt
    sensitive configuration fields in datasource responses.
    """
    key = base64.b64encode(os.urandom(16)).decode("ascii")
    return key


@router.get("/engine/supportSetKey")
async def support_set_key(_: TokenUser = Depends(get_current_user)) -> bool:
    """Whether the engine supports the 'set key' feature for API datasources."""
    return False


@router.get("/sqlbot/datasource")
async def get_sqlbot_datasource_list(
    dsId: int | None = None,  # noqa: N803 — match Java query-param name
    tableId: int | None = None,  # noqa: N803
) -> list:
    """Return available data sources for the SQL Bot assistant.

    Stub — requires external AI service (SQLBot) which is not bundled in
    the community edition.
    """
    return []


@router.get("/sqlbot/dataset/{dv_info}")
async def get_sqlbot_dataset_list(dv_info: str) -> list:
    """Return available datasets for the SQL Bot assistant.

    Stub — requires external AI service (SQLBot) which is not bundled in
    the community edition.
    """
    return []


@router.post("/resource/checkPermission/{resource_id}")
async def check_resource_permission(
    resource_id: int,
    user: TokenUser = Depends(get_current_user),  # BUG-060 fix: require auth
) -> bool:
    """Check if the current user has permission for the given resource.

    Stub — community edition grants access to all authenticated resources.
    """
    _ = user
    return True
