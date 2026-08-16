from __future__ import annotations

import platform
import time

import discord
from discord.ext import commands

from swit.api.logger import Logger
from swit.loader.loader import Loader


class Swit(commands.AutoShardedBot):

    __slots__ = ["intents_config","registry","loader"]
    def __init__(
        self,
        intents: dict[str, bool],
        *,
        command_prefix: str = "!",
        debug: bool = False,
    ):
        self.intents_config = intents

        discord_intents = self._setup_intents()

        super().__init__(
            intents=discord_intents,
            command_prefix=command_prefix
        )

        self.registry = None
        self.logger = Logger(debug=debug)
        self.loader = Loader(self)
    async def on_ready(self):
        await self.logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.logger.info(f"Start sync slash commands")
        total_cog = await self.tree.sync()
        await self.logger.success(f"Done sync slash commands")
        await self.logger.success(f"Total cogs: {len(total_cog)}")

    async def setup_hook(self) -> None:
        await self.logger.info("Start Swit")
        await self.logger.info(f"Running on {platform.python_version()}..")
        await self.logger.info("Start Loader")
        start = time.time()
        modules = await self.loader.start_loader()
        await self.logger.success(f"Loadded: {len(modules)} after {round(time.time() - start,3)} seconds")

    def get_logger(self):
        return self.logger

    def _setup_intents(self) -> discord.Intents:
        intents = discord.Intents.default()

        for name, value in self.intents_config.items():
            if not hasattr(intents, name):
                raise ValueError(
                    f"Invalid Discord intent: {name}"
                )

            setattr(intents,name,value)

        return intents
