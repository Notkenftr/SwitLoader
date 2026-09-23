from __future__ import annotations

import discord
from discord.ext import commands

from swit.api import ModuleManifest, ModuleType
from swit.api.logger import Logger
from swit.app import Swit


class BuildIn(commands.Cog):

    def __init__(self, bot: Swit, manifest: ModuleManifest):
        self.bot = bot
        self.logger: Logger = bot.get_logger()
    @commands.command(name="unload")
    async def build_in(self, ctx: commands.Context,module_name: str):
        print("trigger")
        await ctx.send(module_name)


Manifest = ModuleManifest(
    entry=BuildIn,
    module_type=ModuleType.PREFIX_COMMAND,
    name="build-in",
    description="",
    author=[],
    dependencies_package=[],
    dependencies_module=[],
    disable=False
)