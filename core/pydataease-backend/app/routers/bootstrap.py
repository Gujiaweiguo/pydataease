from fastapi import APIRouter, Depends

from app.services.interactive_tree_service import get_interactive_tree_service
from app.utils.rsa_utils import get_dekey_response

router = APIRouter()


@router.get("/xpackModel")
async def get_xpack_model():
    return None


@router.get("/model")
async def get_model():
    return None


@router.get("/sysParameter/i18nOptions")
async def get_i18n_options():
    return {}


@router.get("/sysParameter/defaultSettings")
async def get_default_settings():
    return {}


@router.get("/sysParameter/ui")
async def get_sys_parameter_ui():
    return {}


@router.get("/sysParameter/defaultLogin")
async def get_default_login():
    return 0


@router.get("/setting/authentication/status")
async def get_authentication_status():
    return False


@router.get("/sysParameter/shareBase")
async def get_share_base():
    return {"disable": True, "peRequire": False}


@router.get("/typeface/defaultFont")
async def get_default_font():
    return []


@router.get("/typeface/listFont")
async def get_list_font():
    return []


@router.get("/templateMarket/searchRecommend")
async def get_template_market_search_recommend():
    return {"baseUrl": "", "contents": []}


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
