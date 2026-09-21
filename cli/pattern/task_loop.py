from __future__ import annotations

from discord.ext import commands, tasks

from swit.app import Swit
from swit.api.logger import Logger
from swit.api import ModuleManifest, ModuleType


class ModuleClassName(commands.Cog):

    def __init__(self, bot: Swit, manifest: ModuleManifest):
        self.bot = bot
        self.logger: Logger = bot.get_logger()
        self.example_loop.start()

    @tasks.loop(seconds=60)
    async def example_loop(self):
        # write logic here
        ...

    @example_loop.before_loop
    async def before_example_loop(self):
        await self.bot.wait_until_ready()


Manifest = ModuleManifest(
    entry=ModuleClassName,
    module_type=ModuleType.LOOP_EVENT,
    name="{module_name}",
    description="",
    author=[],
    dependencies_package=[],
    dependencies_module=[]
)