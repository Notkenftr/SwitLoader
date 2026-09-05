from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from swit.api import ModuleManifest, ModuleType
from swit.app import Swit


class Ping(commands.Cog):
    def __init__(self, bot: Swit):
        self.bot = bot

    @app_commands.command(name="example", description="Example command")
    async def example(self, interaction: discord.Interaction):
        pass


Manifest = ModuleManifest(
    entry=Ping,
    module_type=ModuleType.SLASH_COMMAND,
    name="Ping",
    description="",
    author=[],
    dependencies_package=[],
    dependencies_module=[],
)
