
from __future__ import annotations
from dataclasses import dataclass, field
from .TrueNAS import NfsShareAdd
import os
import logging
import json


def get_env(env_name: str, default: str = "") -> str:
    """
    Get the environment variable as a string.
    Args:
        env_name: The name of the environment variable.
        default: Default value if the environment variable is not found.
    Returns:
        The value of the environment variable or the default value.
    """
    return os.environ.get(env_name, default)


def get_env_list(env_name: str, default: list[str] = []) -> list[str]:
    """
    Get the environment variable as a list of strings (split by commas).
    Args:
        env_name: The name of the environment variable.
        default: Default value if the environment variable is not found.
    Returns:
        A list of strings split from the environment variable value.
    """
    env_value = os.environ.get(env_name, "")
    return env_value.split(",") if env_value else default


def get_env_bool(env_name: str, default: bool = False) -> bool:
    """
    Get the environment variable as a boolean.
    Args:
        env_name: The name of the environment variable.
        default: Default value if the environment variable is not found.
    Returns:
        True or False based on the environment variable value.
    """
    env_value = os.environ.get(env_name, "").lower()
    return env_value in ["true", "1", "yes"] if env_value else default


def get_env_int(env_name: str, default: int = 0) -> int:
    """
    Get the environment variable as an integer.
    Args:
        env_name: The name of the environment variable.
        default: Default value if the environment variable is not found.
    Returns:
        The integer value of the environment variable or the default value.
    """
    env_value = os.environ.get(env_name, "")
    try:
        return int(env_value) if env_value else default
    except ValueError:
        return default


@dataclass
class Config:
    host: str = ""
    api_key: str = ""
    parent_dataset_id: str = ""
    ssl_verify: bool = True
    parent_real_path: str = "/mnt"
    filter_path_pattern: str = "_"
    filter_path_mode: str = "end_with"
    filter_path_reversed: bool = True
    check_period_sec: int = 600
    dry_run: bool = False
    log_level: int = logging.INFO
    nfs_common_networks: list[str] = field(default_factory=list)
    nfs_common_hosts: list[str] = field(default_factory=list)
    nfs_auto_remove: bool = True

    @property
    def nfs_common(self) -> NfsShareAdd:
        return NfsShareAdd(networks=self.nfs_common_networks,hosts=self.nfs_common_hosts)

    def read_from_json_file(self, file_path: str) -> Config:
        with open(file_path, "r") as f:
            data = json.load(f)
            for key in self.__dict__.keys():
                if key in data:
                    self.__dict__[key] = data[key]
        return self

    def write_to_json_file(self, file_path: str):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w+") as f:
            json.dump(self.__dict__, f, indent=4)

    def from_env(self) -> Config:
        TRUENAS_HOST = get_env("TRUENAS_HOST", "")
        TRUENAS_API_KEY_FILE = get_env("TRUENAS_API_KEY_FILE")
        TRUENAS_PARENT_DATASET_ID = get_env("TRUENAS_PARENT_DATASET_ID", "")

        if TRUENAS_API_KEY_FILE and os.path.exists(TRUENAS_API_KEY_FILE):
            with open(TRUENAS_API_KEY_FILE, "r") as f:
                TRUENAS_API_KEY = f.read().strip()
        else:
            TRUENAS_API_KEY = get_env("TRUENAS_API_KEY", "")
        if not TRUENAS_HOST:
            raise ValueError("TRUENAS_HOST is not set")
        if not TRUENAS_API_KEY:
            raise ValueError("TRUENAS_API_KEY is not set")
        if not TRUENAS_PARENT_DATASET_ID:
            raise ValueError("TRUENAS_PARENT_DATASET_ID is not set")

        self.host = TRUENAS_HOST
        self.api_key = TRUENAS_API_KEY
        self.parent_dataset_id = TRUENAS_PARENT_DATASET_ID
        self.ssl_verify = get_env_bool("TRUENAS_SSL_VERIFY", True)
        self.parent_real_path = get_env("TRUENAS_PARENT_REAL_PATH", "/mnt")
        self.filter_path_mode = get_env("TRUENAS_FILTER_PATH_MODE", "end_with")
        self.filter_path_pattern = get_env("TRUENAS_FILTER_PATH_PATTERN", "_")
        self.filter_path_reversed = get_env_bool("TRUENAS_FILTER_PATH_REVERSED", True)
        self.check_period_sec = get_env_int("TRUENAS_CHECK_PERIOD_SEC", 600)
        self.dry_run = get_env_bool("TRUENAS_DRY_RUN", False)
        self.nfs_common_networks = get_env_list("TRUENAS_NFS_COMMON_NETWORKS", [])
        self.nfs_common_hosts = get_env_list("TRUENAS_NFS_COMMON_HOSTS", [])
        log_level = get_env("TRUENAS_LOG_LEVEL", "INFO").upper()
        self.log_level = getattr(logging, log_level, logging.INFO)
        self.nfs_auto_remove = get_env_bool("TRUENAS_NFS_AUTO_REMOVE", True)
        return self

    @classmethod
    def new_from_env(cls) -> Config:
        obj = cls()
        return obj.from_env()

    @classmethod
    def new(cls, config_file: str = None) -> Config:
        obj = cls()
        if config_file is None:
            obj.from_env()
            print("Read config from environment variables.")
        else:
            try:
                obj.read_from_json_file(file_path=config_file)
                print(f"Read config from file: {config_file}")
            except Exception as e:
                print(f"Failed to read config: {e}")
                raise
        return obj
