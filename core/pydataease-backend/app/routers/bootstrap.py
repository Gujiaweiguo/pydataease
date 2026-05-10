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
