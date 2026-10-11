from __future__ import annotations

import yaml

from swit.api.utils.path_api import PathAPI


class Config:
    """Helper for reading and writing module configuration files."""

    @staticmethod
    def load(config_name: str) -> dict:
        name = config_name if config_name.endswith((".yml", ".yaml")) else f"{config_name}.yml"
        path = PathAPI.join_path("configs", name)
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}

    @staticmethod
    def save(config_name: str, data: dict) -> None:
        name = config_name if config_name.endswith((".yml", ".yaml")) else f"{config_name}.yml"
        path = PathAPI.join_path("configs", name, create_parent=True)
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, default_flow_style=False)