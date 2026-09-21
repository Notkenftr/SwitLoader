from __future__ import annotations

import asyncio
import importlib.util
import inspect
import sys
import traceback
from pathlib import Path
from swit.api.enums.module_type import ModuleType
from swit.api.types.module_manifest import ModuleManifest

# api
from swit.api.utils.path_api import PathAPI
from swit.loader.dependency import package_dependency

# local
from swit.loader.registry import Registry


def _load_spec(module_path: Path):
    module_name = f"swit_modules.{module_path.name}"

    spec = importlib.util.spec_from_file_location(
        module_name, module_path / "module.py"
    )

    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module: {module_path}")

    module = importlib.util.module_from_spec(spec)

    sys.modules[module_name] = module

    spec.loader.exec_module(module)

    return module

def _insert_metadata(module_path: Path,entry,manifest: ModuleManifest) -> dict:
    _metadata = {
        "module_path": module_path,
        "entry": entry
    }
    manifest._metadata = _metadata
    return _metadata

def _call_entry(entry,swit,manifest):
    signature = inspect.signature(entry)

    if len(signature.parameters) >= 2:
        return entry(swit, manifest)
    return entry(swit)

class Loader:
    __slots__ = [
        "loaded_modules",
        "logger",
        "module_path",
        "module_metadata",
        "registry",
        "swit",
        "swit_loader_config",
        "waiting_depend",
    ]

    def __init__(self, swit):
        self.swit = swit
        self.swit_loader_config = self.swit.get_swit_config()
        self.logger = self.swit.get_logger().get("SwitLoader",{})
        self.registry = Registry()
        self.loaded_modules = {}
        self.module_metadata = {}
        self.waiting_depend = []
        self.swit.registry = self.registry
        self.module_path = PathAPI.join_path("modules")
        self.module_path.mkdir(parents=True, exist_ok=True)

    async def _load(self, module_path: Path, setup_step_hook_array: list):
        try:
            module = await asyncio.to_thread(
                _load_spec,
                module_path,
            )
            await self.logger.info(f"Loading: {module.__name__}")
            manifest: ModuleManifest | None = getattr(module, "Manifest", None)
            if manifest is None:
                return False
            entry = manifest.entry

            if manifest.dependencies_package:
                await self.logger.info(
                    f"Loading dependency package: {manifest.dependencies_package}"
                )
                await package_dependency(self, manifest)
            if manifest.disable:
                return False
            entry_instance = _call_entry(entry, self.swit, manifest)

            match manifest.module_type:
                case ModuleType.PREFIX_COMMAND:
                    await self.swit.add_cog(entry_instance)
                case ModuleType.SLASH_COMMAND:
                    await self.swit.add_cog(entry_instance)
                case ModuleType.EVENT:
                    await self.swit.add_cog(entry_instance)
                case ModuleType.COG:
                    await self.swit.add_cog(entry_instance)
                case ModuleType.GROUP_COMMAND:
                    self.swit.tree.add_command(entry_instance)
                case ModuleType.LOOP_EVENT:
                    await self.swit.add_listener(entry_instance)
                case ModuleType.HOOK_TO_SETUP_STEP:
                    for name in ("hooker", "hook", "entry"):
                        value = getattr(module, name, None)
                        if value:
                            setup_step_hook_array.append(value)
                case ModuleType.CALL_SETUP_FUNC:
                    setup = module.setup
                    await setup(self.swit)
                case _:
                    if entry:
                        await self.swit.add_cog(
                            _call_entry(entry, self.swit, manifest)
                        )

            self.registry.add(manifest.name, module)
            self.loaded_modules[manifest.name] = module
            metadata = _insert_metadata(module_path=module_path, entry=entry, manifest=manifest)
            self.module_metadata[manifest.name] = metadata

            return True

        except Exception as e:  # noqa: BLE001
            await self.logger.warning(f"Failed to load module: {module_path}")
            traceback.print_exc()
            await self.logger.warning(f"Info: {e}")
            return False

    async def load_with_semaphore(self, module_path: Path, setup_step_hook_array: list,semaphore):
        async with semaphore:
            return await self._load(module_path, setup_step_hook_array)

    async def start_loader(self, setup_step_hook_array):
        modules = [
            path
            for path in self.module_path.iterdir()
            if (path.is_dir() and (path / "module.py").exists())
        ]


        # Synchronous load
        if not self.swit_loader_config.get("parallel_load", False):
            count = 0
            for module in modules:
                await self._load(module,setup_step_hook_array)
                await self.logger.success(f"Loaded {count}/{len(modules)} modules")
                count += 1
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
            *(self._load(module, setup_step_hook_array) for module in modules)
        )
        await self.logger.success(f"Loaded {sum(result)}/{len(modules)} modules")
        return modules

