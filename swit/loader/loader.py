from __future__ import annotations

import sys
import asyncio
import importlib.util
import traceback
from pathlib import Path

from swit.api.enums.module_type import ModuleType
from swit.api.types.module_manifest import ModuleManifest
# local
from swit.loader.registry import Registry

# api
from swit.api.utils.path_api import PathAPI


def _load_spec(module_path: Path):
    module_name = f"swit_modules.{module_path.name}"

    spec = importlib.util.spec_from_file_location(
        module_name,
        module_path / "module.py"
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Cannot load module: {module_path}"
        )

    module = importlib.util.module_from_spec(spec)

    sys.modules[module_name] = module

    spec.loader.exec_module(module)

    return module


class Loader:
    __slots__ = ["swit",
                 "registry",
                 "module_path",
                 "loaded_modules",
                 "waiting_depend",
                 "logger"]
    def __init__(self,swit):
        self.swit = swit
        self.logger = self.swit.get_logger()
        self.registry = Registry()
        self.loaded_modules = {}
        self.waiting_depend = []
        self.swit.registry = self.registry
        self.module_path = PathAPI.join_path("modules")
        self.module_path.mkdir(parents=True, exist_ok=True)

    async def _load(self, module_path: Path):
        try:
            module = _load_spec(module_path)
            manifest: ModuleManifest | None = getattr(
                module,
                "Manifest",
                None
            )
            if manifest is None:
                return False
            entry = manifest.entry

            if manifest.dependencies_package:
                await self.logger.info(f"Loading dependency package: {manifest.dependencies_package}")

            match manifest.module_type:
                case ModuleType.PREFIX_COMMAND:
                    await self.swit.add_cog(entry(self.swit))
                case ModuleType.SLASH_COMMAND:
                    await self.swit.add_cog(entry(self.swit))
                case ModuleType.GROUP_COMMAND:
                    self.swit.add_command(entry(self.swit))
                case ModuleType.LOOP_EVENT:
                    await self.swit.add_listener(entry(self.swit))
                case ModuleType.CALL_SETUP_FUNC:
                    setup = getattr(module,"setup")
                    await setup(self.swit)
                case _:
                    if entry:
                        await self.swit.add_cog(entry(self.swit))
            self.registry.add(manifest.name,module)
            self.loaded_modules[manifest.name] = module
            return True

        except Exception:
            traceback.print_exc()
            await self.logger.warning(f"Failed to load module: {module_path}")
            return False

    async def start_loader(self):
        modules = [
            path
            for path in self.module_path.iterdir() if (path.is_dir()and (path / "module.py").exists())
        ]
        result = await asyncio.gather(
            *(
                self._load(module)
                for module in modules
            )
        )
        await self.logger.success(f"Loaded {sum(result)}/{len(modules)} modules")

        return modules



if __name__ == '__main__':
    loader = Loader()
    asyncio.run(loader.start_loader())
