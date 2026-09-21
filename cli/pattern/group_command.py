from __future__ import annotations

import discord
from discord import app_commands

from swit.app import Swit
from swit.api.logger import Logger
from swit.api import ModuleManifest, ModuleType


class ModuleClassName(app_commands.Group):

    def __init__(self, bot: Swit, manifest: ModuleManifest):
        super().__init__(
            name="{module_name}",
            description="Example command group"
        )

        self.bot = bot
        self.logger: Logger = bot.get_logger()

    @app_commands.command(
        name="{module_name",
        description="Example command"
    )
    async def ModuleName(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello world!")


Manifest = ModuleManifest(
    entry=ModuleClassName,
    module_type=ModuleType.GROUP_COMMAND,
    name="{module_name}",
    description="",
    author=[],
    dependencies_package=[],
    dependencies_module=[]
)