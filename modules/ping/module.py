from __future__ import annotations

from typing import cast

import discord
from discord import app_commands, InteractionResponse
from discord.ext import commands

from swit.api import ModuleManifest, ModuleType
from swit.app import Swit


class Ping(commands.Cog):
    def __init__(self, bot: Swit):
        self.bot = bot

    @app_commands.command(name="ping", description="ping pong!")
    async def ping(self, interaction: discord.Interaction):
        message = f"Pong! ``{round(self.bot.latency * 1000)}``ms"
        await interaction.response.send_message(message, ephemeral=True)


Manifest = ModuleManifest(
    entry=Ping,
    module_type=ModuleType.SLASH_COMMAND,
    name="Ping",
    description="",
    author=[],
    dependencies_package=[],
    dependencies_module=[],
)
