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
        raise FileNotFoundError(
            f"Missing config file: {config_path}"
        )

    with config_path.open(
        "r",
        encoding="utf-8"
    ) as file:
        config = yaml.safe_load(file)

    if not isinstance(config, dict):
        raise ValueError(
            "config.yml must contain a YAML object"
        )

    return config


async def main():
    ensure_dependencies()
    depend_handler()

    if sys.version_info < (3,13):
        raise RuntimeError(
            f"Python 3.13+ is required. "
            f"Current version: {sys.version.split()[0]}"
        )

    config = load_config()

    discord_config = config.get("Discord", {})

    if not isinstance(discord_config, dict):
        raise ValueError(
            "Discord config must be a mapping"
        )

    bot_token = discord_config.get("bot-token")

    if not bot_token:
        raise ValueError(
            "Missing required config: Discord.bot_token"
        )

    from swit.app import Swit

    bot = Swit(
        intents=discord_config.get(
            "intents",
            {}
        ),
        command_prefix=discord_config.get(
            "command_prefix",
            "!"
        ),
        debug=config.get("Logger",{}).get("debug",False),
    )

    await bot.start(bot_token)


def bootstrap():
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("Stop")

    except Exception as e:
        print(
            f"Fatal error: {type(e).__name__}: {e}"
        )
        raise


