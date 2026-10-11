from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from swit.api.utils.package import install_package
from swit.api.utils.path_api import PathAPI
from swit.bootstrap.depend_handler import depend_handler


def ensure_dependencies():
    required = {
        "yaml": "pyyaml",
    }

    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            install_package(package)


def load_config() -> dict:
    import yaml

    config_path = Path(PathAPI.join_path("config.yml"))

    if not config_path.exists():
        raise FileNotFoundError(f"Missing config file: {config_path}")

    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if not isinstance(config, dict):
        raise TypeError("config.yml must contain a YAML object")

    return config

def load_dotenv_if_exists() -> None:
    import os

    env_path = Path(PathAPI.join_path(".env"))
    if env_path.exists():
        with env_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key and key not in os.environ:
                        os.environ[key] = val


def load_lazyconfig() -> dict:
    try:
        import lazyconfig
        return {
            k: v for k, v in vars(lazyconfig).items()
            if not k.startswith("_")
        }
    except ModuleNotFoundError:
        return {}


async def main():
    if sys.version_info < (3, 13):  # noqa: UP036
        raise RuntimeError(
            f"Python 3.13+ is required. Current version: {sys.version.split()[0]}"
        )

    ensure_dependencies()
    depend_handler()
    load_dotenv_if_exists()

    config = load_config()

    discord_config = config.get("Discord", {})

    if not isinstance(discord_config, dict):
        raise TypeError("Discord config must be a mapping")

    import os
    bot_token = (
        discord_config.get("bot-token")
        or discord_config.get("bot_token")
        or os.getenv("DISCORD_BOT_TOKEN")
        or os.getenv("DISCORD_TOKEN")
    )

    if not bot_token:
        raise ValueError("Missing required config: Discord.bot-token in config.yml")

    from swit.app import Swit

    lazyconfig = load_lazyconfig()

    bot = Swit(
        config=config,
        lazyconfig=lazyconfig,
        command_prefix=discord_config.get("command_prefix", "!"),
        debug=config.get("Logger", {}).get("debug", False),
    )

    try:
        await bot.start(bot_token)
    finally:
        if not bot.is_closed():
            await bot.close()


def bootstrap():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[SwitLoader] Stopped by user (KeyboardInterrupt).")
    except Exception as e:
        print(f"\n[SwitLoader] Fatal error: {type(e).__name__}: {e}")
        raise
