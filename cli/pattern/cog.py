from __future__ import annotations

from discord.ext import commands

from swit.api import ModuleManifest, ModuleType
from swit.api.logger import Logger
from swit.app import Swit


class ModuleClassName(commands.Cog):

    def __init__(self, bot: Swit, manifest: ModuleManifest):
        self.bot = bot
        self.logger: Logger = bot.get_logger()


Manifest = ModuleManifest(
    entry=ModuleClassName,
    module_type=ModuleType.COG,
    name="{module_name}",
    description="",
    author=[],
    dependencies_package=[],
    dependencies_module=[]
)