import os

import aiofiles
import yaml
from discord.ext import commands, tasks

from swit.api import ModuleManifest, ModuleType
from swit.api.logger import Logger
from swit.api.utils.path_api import PathAPI
from swit.app import Swit
from swit.loader.loader import Loader


class BuildIn(commands.Cog):

    def __init__(self, bot: Swit, manifest: ModuleManifest):
        self.bot = bot
        self.loader: Loader = self.bot.loader
        self.logger: Logger = bot.get_logger()

        self.config_path = PathAPI.join_path("config.yml")
        self._config_mtime = 0
        self.reload_main_config.start()

    def cog_unload(self):
        self.reload_main_config.cancel()

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

    @tasks.loop(seconds=2.0)
    async def reload_main_config(self):
        try:
            mtime = os.stat(self.config_path).st_mtime_ns
            if mtime <= self._config_mtime:
                return
            self._config_mtime = mtime
            async with aiofiles.open(self.config_path, mode="r", encoding="utf-8") as f:
                self.bot.config = yaml.safe_load(await f.read())
        except Exception:  # noqa: BLE001, S110
            pass

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