from swit.api.config import Config
from swit.api.utils.path_api import PathAPI


def test_config_load_and_save():
    cfg_name = "test_custom_config.yml"
    cfg_path = PathAPI.join_path("configs", cfg_name)

    try:
        Config.save(cfg_name, {"bot": {"name": "TestBot", "enabled": True}})
        assert cfg_path.exists()

        data = Config.load(cfg_name)
        assert data["bot"]["name"] == "TestBot"
        assert data["bot"]["enabled"] is True
    finally:
        if cfg_path.exists():
            cfg_path.unlink()
