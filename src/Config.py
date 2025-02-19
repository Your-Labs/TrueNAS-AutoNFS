
from __future__ import annotations
from dataclasses import dataclass
import os
import logging

@dataclass
class Config:
    host: str
    api_key: str
    parent_dataset_id: str
    ssl_verify: bool = True
    parent_real_path: str = "/mnt"
    filter_path_pattern: str = "_"
    filter_path_mode: str = "end_with"
    filter_path_reversed: bool = True
    check_period_sec: int = 600
    dry_run: bool = False
    log_level: int = logging.INFO

    @classmethod
    def new_from_env(cls) -> Config:
        TRUENAS_HOST = os.environ.get("TRUENAS_HOST")
        TRUENAS_API_KEY_FILE = os.environ.get("TRUENAS_API_KEY_FILE")
        TRUENAS_PARENT_DATASET_ID = os.environ.get("TRUENAS_PARENT_DATASET_ID")
        TRUENAS_LOG_LEVEL = os.environ.get("TRUENAS_LOG_LEVEL", "INFO")
        log_level = getattr(logging, TRUENAS_LOG_LEVEL.upper(), logging.INFO)

        if TRUENAS_API_KEY_FILE and os.path.exists(TRUENAS_API_KEY_FILE):
            with open(TRUENAS_API_KEY_FILE, "r") as f:
                TRUENAS_API_KEY = f.read().strip()
        else:
            TRUENAS_API_KEY = os.environ.get("TRUENAS_API_KEY")
        if not TRUENAS_HOST:
            raise ValueError("TRUENAS_HOST is not set")
        if not TRUENAS_API_KEY:
            raise ValueError("TRUENAS_API_KEY is not set")
        if not TRUENAS_PARENT_DATASET_ID:
            raise ValueError("TRUENAS_PARENT_DATASET_ID is not set")

        return Config(
            host=TRUENAS_HOST,
            api_key=TRUENAS_API_KEY,
            parent_dataset_id=TRUENAS_PARENT_DATASET_ID,
            ssl_verify=bool(os.environ.get("TRUENAS_SSL_VERIFY", True)),
            parent_real_path=os.environ.get("TRUENAS_PARENT_REAL_PATH", "/mnt"),
            filter_path_mode=os.environ.get("TRUENAS_FILTER_PATH_MODE", "end_with"),
            filter_path_pattern=os.environ.get("TRUENAS_FILTER_PATH_PATTERN", "_"),
            filter_path_reversed=bool(os.environ.get("TRUENAS_FILTER_PATH_REVERSED", True)),
            check_period_sec=int(os.environ.get("TRUENAS_CHECK_PERIOD_SEC", 600)),
            dry_run=bool(os.environ.get("TRUENAS_DRY_RUN", False)),
            log_level=log_level
        )
