from __future__ import annotations

import platform
import time
import traceback

from discord.ext import commands

from patches.slash_command_try_catch import install_slash_command_try_catch_patch
from swit.api.logger import Logger
from swit.build_in.get_version import get_swit_version
from swit.context import set_swit
from swit.loader.loader import Loader
from swit.setup.setup_hook_step import _load_hooker, _setup_intents


class Swit(commands.AutoShardedBot):

    INSTANCE = None

    def __new__(cls, *args, **kwargs):
        if cls.INSTANCE is None:
            cls.INSTANCE = super().__new__(cls)
        return cls.INSTANCE

    __slots__ = ["_synced", "discord_intents", "intents_config", "lazyconfig", "loader", "registry"]

    def __init__(
        self,
        config: dict,
        lazyconfig: dict | None = None,
        *,
        command_prefix: str = "!",
        debug: bool = False,
    ):
        self._synced = False
        self.config: dict | None = config

        self.logger: Logger | None = Logger(debug=debug)
        self.loader: Loader | None = Loader(self)
        self.lazyconfig: dict | None = lazyconfig

        self.version = get_swit_version()
        self.intents_config: dict = (self.config or {}).get("Discord",{}).get("intents", {})

        super().__init__(intents=_setup_intents(self.intents_config), command_prefix=command_prefix)
        self.registry = None
        set_swit(self)

    async def on_ready(self):
        await self.logger.info(f"Logged in as {self.user} (ID: {self.user.id})")

        if not getattr(self, "_synced", False):
            await self.logger.info("Start sync slash commands")
            total_cog = await self.tree.sync()
            self._synced = True
            await self.logger.success("Done sync slash commands")
            await self.logger.success(f"Total cogs: {len(total_cog)}")
            await self.logger.success(
                f"Total slash commands: {len(self.tree.get_commands())}"
            )

            slash_commands = self.tree.get_commands()
            cmd_lines = []
            for command in slash_commands:
                cmd_lines.append(f"/{command.name}")
                if isinstance(command, commands.Group):
                    for subcommand in command.commands:
                        cmd_lines.append(f"  - /{subcommand.name}")
            if cmd_lines:
                await self.logger.info("Command map:\n" + "\n".join(cmd_lines))

        await self.logger.success("Bot ready!")


    async def setup_hook(self) -> None:
        """
        Initialize Swit by setting up patches, loading modules, and executing
        registered setup hooks.

        This method is called automatically during the bot initialization
        process. Custom initialization logic can be added by overriding this
        method.

        :return: None
        """

        setup_step_hook = []
        await self.logger.info("Starting...")
        await self.logger.info(f"Running on swit {self.version}")
        await self.logger.info(f"Running on {platform.python_version()}..")
        await self.logger.info("Setup patches")
        install_slash_command_try_catch_patch(self)
        await self.logger.success("Install patches success!")
        await self.logger.debug(f"Loadded {len(self.intents_config)} intents")
        await self.logger.debug(f"{self.intents_config}")
        await self.logger.info("Start Loader")
        start = time.time()

        modules = await self.loader.start_loader(setup_step_hook)

        module_count = len(modules)

        await self.logger.success(
            f"Loadded: {module_count} {'modules' if module_count > 0 else 'module'} after {round(time.time() - start, 3)} seconds"
        )

        await self.logger.info("Checking hooker")
        await self.logger.info(f"Found: {len(setup_step_hook)} hooks")

        # load hooker
        await _load_hooker(self, setup_step_hook)
        await self.logger.info(
            f"Loadded: {len(setup_step_hook)} hook after {round(time.time() - start, 3)} seconds"
        )

    # build in event
    async def on_error(self, event: str, *args, **kwargs):
        await self.logger.error(
            f"Error infomation:\n"
            f"- Event: {event}\n"
            f"- Args: {args}\n"
            f"- Kwargs: {kwargs}\n"
            f"- Traceback:"
            f"- {traceback.format_exc()}"
        )

    # getter
    def get_version(self):
        return self.version

    def get_logger(self):
        return self.logger

    def get_swit_config(self):
        return self.config

