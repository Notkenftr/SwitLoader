from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

from discord import Object

from swit.api.logger import Logger
# api
from swit.api.utils.path_api import PathAPI
from swit.app import Swit
from swit.loader.load_module import _load
# local
from swit.loader.registry import Registry

class Loader:
    __slots__ = [
        "loaded_modules",
        "logger",
        "module_metadata",
        "module_path",
        "registry",
        "swit",
        "swit_loader_config",
        "waiting_depend",
    ]

    def __init__(self, swit):
        self.swit: Swit = swit
        self.swit_loader_config: Optional[dict,None] = self.swit.get_swit_config().get("SwitLoader",{})
        self.logger: Logger = self.swit.get_logger()
        self.registry: Registry = Registry()

        self.loaded_modules: dict[str,Object] = {}
        self.module_metadata: dict[str,dict[str,...]] = {}
        self.waiting_depend = []
        self.swit.registry = self.registry
        self.module_path = PathAPI.join_path("modules")
        self.module_path.mkdir(parents=True, exist_ok=True)

    async def load_with_semaphore(self,module_path: Path, setup_step_hook_array: list,semaphore):
        async with semaphore:
            return await _load(self,module_path, setup_step_hook_array)

    async def start_loader(self, setup_step_hook_array):
        """
        Initialize the Loader. Do not call this method directly unless you understand its behavior.
        :param setup_step_hook_array:
        :return:
        """
        modules = [
            path
            for path in self.module_path.iterdir()
            if (path.is_dir() and (path / "module.py").exists())
        ]
        # Synchronous load
        if not self.swit_loader_config.get("parallel_load", False):
            count = 0
            for i,module in enumerate(modules):
                await _load(self,module,setup_step_hook_array)
                count = i
            await self.logger.success(f"Loaded {count}/{len(modules)} modules")
            return modules

        # Paralled load
        if self.swit_loader_config.get("max_concurrency") and self.swit_loader_config.get("max_concurrency") != "inf":
            semaphore = asyncio.Semaphore(self.swit_loader_config["max_concurrency"])
            result = await asyncio.gather(
                *(self.load_with_semaphore(module, setup_step_hook_array,semaphore) for module in modules)
            )
            await self.logger.success(f"Loaded {sum(result)}/{len(modules)} modules")
            return modules

        result = await asyncio.gather(
            *(_load(self,module, setup_step_hook_array) for module in modules)
        )
        await self.logger.success(f"Loaded {sum(result)}/{len(modules)} modules")
        return modules

