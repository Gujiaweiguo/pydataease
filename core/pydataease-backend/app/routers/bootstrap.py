from fastapi import APIRouter

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
async def get_interactive_tree():
    return {"dashboard": [], "dataV": [], "dataset": [], "datasource": []}
