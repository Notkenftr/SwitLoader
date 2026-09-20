from __future__ import annotations

import discord
from discord.ext import commands

from swit.app import Swit

from swit.api.logger import Logger
from swit.api import ModuleManifest, ModuleType


class ModuleClassName(commands.Cog):

    def __init__(self, bot: Swit):
        self.bot = bot
        self.logger: Logger = bot.get_logger()

    @commands.command(name="{module_name}")
    async def ModuleName(self, ctx: commands.Context):
        await ctx.send("Hello world!")


Manifest = ModuleManifest(
    entry=ModuleClassName,
    module_type=ModuleType.PREFIX_COMMAND,
    name="{module_name}",
    description="",
    author=[],
    dependencies_package=[],
    dependencies_module=[],
    disable=False
)