import time
from functools import lru_cache
from importlib import metadata
from pathlib import Path
from typing import Dict, Optional, Union

import tomlkit
from pydantic_settings import BaseSettings


def _get_project_meta(name: str = "unknown") -> Dict:
    """
    Get name and version from pyproject metadata.
    """
    version = "unknown"
    description = ""
    try:
        with Path("./pyproject.toml").open() as pyproject:
            file_contents = pyproject.read()
        parsed = dict(tomlkit.parse(file_contents))["tool"]["poetry"]
        name = parsed["name"]
        version = parsed.get("version", "unknown")
        description = parsed.get("description", "")
    except FileNotFoundError:
        # If cannot read the contents of pyproject directly (i.e. in Docker),
        # check installed package using importlib.metadata:
        try:
            dist = metadata.distribution(name)
            name = dist.metadata["Name"]
            version = dist.version
            description = dist.metadata.get("Summary", "")
        except metadata.PackageNotFoundError:
            pass
    return {"name": name, "version": version, "description": description}


PKG_META = _get_project_meta()


class Settings(BaseSettings):
    """
    Settings. Environment variables always take priority over values loaded
    from the dotenv file.
    """

    current_timestamp: int = int(time.time())

    # Meta
    APP_NAME: str = str(PKG_META["name"])
    APP_VERSION: str = str(PKG_META["version"])
    PUBLIC_NAME: str = APP_NAME
    DESCRIPTION: str = str(PKG_META["description"])

    # Logger
    LOGGER_NAME: str = "data_vortex"
    LOG_LEVEL: str = "info"
    VERBOSE_LOGS: Union[bool, int, str] = True
    JSON_LOGS: Union[bool, int, str] = False
    LOG_DIR: Path = (
        Path("logs") / f"{current_timestamp}-{LOGGER_NAME}-{LOG_LEVEL}.log"
    )

    SYSLOG_ADDR: Optional[Path] = None

    DATABASE_URL: str = "sqlite:///vortex.db"
    DATBASE_TYPE: str = "sqlite"

    USE_CACHE_FOR_SEARCH: bool = True
    DATA_DIR: Path = Path("data")
    RAW_LISTING_DIR: Path = Path("raw_data")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        secrets_dir = "secrets"


@lru_cache
def get_settings() -> Settings:
    return Settings(_env_file=Path(__file__).resolve().parent.parent.parent.parent / ".env")


settings = get_settings()
