from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from swit.app import Swit
from swit.api import ModuleManifest
from swit.api import ModuleType


class Ping(commands.Cog):
    def __init__(self,bot: Swit):
        self.bot = bot

    @app_commands.command(name="example",description="Example command")
    async def example(self,interaction: discord.Interaction):
        pass

Manifest = ModuleManifest(
    entry=Ping,
    module_type=ModuleType.SLASH_COMMAND,
    name="Ping",
    description="",
    author=[],
    dependencies_package=[],
    dependencies_module=[]
)