from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from swit.api import ModuleManifest, ModuleType
from swit.api.logger import Logger
from swit.app import Swit


class ModuleClassName(commands.Cog):

    def __init__(self, bot: Swit, manifest: ModuleManifest):
        self.bot = bot
        self.logger: Logger = bot.get_logger()

    @app_commands.command(
        name="{module_name}",
        description="Example command"
    )
    async def ModuleName(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello world!")


Manifest = ModuleManifest(
    entry=ModuleClassName,
    module_type=ModuleType.SLASH_COMMAND,
    name="{module_name}",
    description="",
    author=[],
    dependencies_package=[],
    dependencies_module=[]
)