from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    app_name: str = "DataEase API"
    version: str = "0.1.0"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://dataease:dataease@localhost:5432/dataease"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_recycle: int = 1800
    secret_key: str = "change-me-in-production"
    share_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_exp_seconds: int = 1800
    api_prefix: str = "/de2api"
    cors_origins: str = "*"
    org_management_enabled: bool = True
    permission_enforcement_enabled: bool = True
    rsa_private_key_path: str = ""
    log_level: str = "INFO"

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(env_file=".env", env_prefix="DE_")


class DevConfig(BaseConfig):
    debug: bool = True
    database_url: str = "postgresql+asyncpg://dataease:dataease@localhost:5432/dataease"


class ProdConfig(BaseConfig):
    debug: bool = False


_settings: BaseConfig | None = None


def get_settings() -> BaseConfig:
    global _settings
    if _settings is None:
        import os

        env = os.getenv("DE_ENV", "dev")
        if env == "prod":
            _settings = ProdConfig()
        else:
            _settings = DevConfig()
    return _settings
