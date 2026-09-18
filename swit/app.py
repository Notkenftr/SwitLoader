from __future__ import annotations

import asyncio
import inspect
import platform
import time
import traceback

import discord
from discord.ext import commands

from patches.slash_command_try_catch import install_slash_command_try_catch_patch
from swit.api.logger import Logger
from swit.build_in.get_version import get_swit_version
from swit.context import set_swit
from swit.loader.loader import Loader


class Swit(commands.AutoShardedBot):
    __slots__ = ["discord_intents", "intents_config", "loader", "registry"]

    def __init__(
        self,
        config: dict,
        *,
        command_prefix: str = "!",
        debug: bool = False,
    ):
        self.config = config
        self.intents_config = self.config.get("intents", {})
        self.logger = Logger(debug=debug)
        self.loader = Loader(self)

        self.version = get_swit_version()

        self.discord_intents = self._setup_intents()

        super().__init__(intents=self.discord_intents, command_prefix=command_prefix)
        self.registry = None
        set_swit(self)

        asyncio.run(self.logger.info("Setup patches"))
        install_slash_command_try_catch_patch(self)

    async def on_ready(self):
        await self.logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.logger.info("Start sync slash commands")
        total_cog = await self.tree.sync()
        await self.logger.success("Done sync slash commands")
        await self.logger.success(f"Total cogs: {len(total_cog)}")
        await self.logger.success(
            f"Total slash commands: {len(self.tree.get_commands())}"
        )

        slash_commands = self.tree.get_commands()

        await self.logger.info("command map")
        for command in slash_commands:
            await self.logger.info(f"/{command.name}")
            if isinstance(command, commands.Group):
                for subcommand in command.commands:
                    await self.logger.info(f"- /{subcommand.name}")
        await self.logger.success("Bot ready!")

    async def setup_hook(self) -> None:
        setup_step_hook = []
        await self.logger.info("Starting...")
        await self.logger.info(f"Running on swit {self.version}")
        await self.logger.info(f"Running on {platform.python_version()}..")
        await self.logger.debug(f"Loadded {len(self.intents_config)} intents")
        await self.logger.debug(f"{self.intents_config}")
        await self.logger.info("Start Loader")
        start = time.time()

        modules = await self.loader.start_loader(setup_step_hook)

        module_count = len(modules)

        await self.logger.success(
            f"Loadded: {module_count} {'modules' if module_count > 0 else 'module'} after {round(time.time() - start, 3)} seconds"
        )

        await self.logger.info("Checking hooker")
        await self.logger.info(f"Found: {len(setup_step_hook)} hooks")

        # load hooker
        for func in setup_step_hook:
            if callable(func):
                await self.logger.debug(f"Running {func.__name__}")
                try:
                    if inspect.iscoroutinefunction(func):
                        await func(self)
                    else:
                        func(self)
                except Exception as e:  # noqa: BLE001
                    await self.logger.error(e)
            else:
                await self.logger.error(f"{func.__name__} is not callable")
                continue
        await self.logger.info(
            f"Loadded: {len(setup_step_hook)} hook after {round(time.time() - start, 3)} seconds"
        )

    # build in event
    async def on_error(self, event: str, *args, **kwargs):
        await self.logger.error(
            f"Error infomation:\n"
            f"- Event: {event}\n"
            f"- Args: {args}\n"
            f"- Kwargs: {kwargs}\n"
            f"- Traceback:"
            f"- {traceback.format_exc()}"
        )

    # getter

    def get_version(self):
        return self.version

    def get_logger(self):
        return self.logger

    def get_swit_config(self):
        return self.config

    def _setup_intents(self) -> discord.Intents:
        intents = discord.Intents.default()

        for name, value in self.intents_config.items():
            if name in ["auto_detect", "all", "default"]:
                continue
            if not hasattr(intents, name):
                raise ValueError(f"Invalid Discord intent: {name}")
            setattr(intents, name, value)

        return intents
