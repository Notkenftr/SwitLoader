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
    async def build_in(
            self,
            ctx: commands.Context,
            module_name: str,
    ):
        if ctx.author.id not in self.bot.get_swit_config().get("Swit",{}).get("allow_build_in_command",[]):
            return

        msg = await ctx.send(f"Unloading `{module_name}`...")
        status, error = await self.loader.unload_module_by_name(
            module_name,
            debug=True,
        )
        if status:
            await msg.edit(content=f"Successfully unloaded `{module_name}`.")
            return

        match error:
            case "Err: module not loaded":
                content = f"Module `{module_name}` is not loaded."
            case "Err: cog not found":
                content = f"Cog for module `{module_name}` was not found."
            case _:
                content = f"Failed to unload module `{module_name}`."

        await msg.edit(content=content)

        
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