from __future__ import annotations

import asyncio
import importlib.util
import inspect
import sys
import traceback
from pathlib import Path

# types
from swit.api.enums.module_type import ModuleType
from swit.api.types.module_manifest import ModuleManifest
from swit.loader.dependency import package_dependency


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

def _call_entry(entry,swit,manifest):
    signature = inspect.signature(entry)

    if len(signature.parameters) >= 2:
        return entry(swit, manifest)
    return entry(swit)

def _insert_metadata(module_path: Path,entry,manifest: ModuleManifest) -> dict:
    _metadata = {
        "module_path": module_path,
        "entry": entry
    }
    manifest._metadata = _metadata
    return _metadata

async def _load(loader_instance, module_path: Path, setup_step_hook_array: list):
    try:
        module = await asyncio.to_thread(
            _load_spec,
            module_path,
        )
        await loader_instance.logger.info(f"Loading: {module.__name__}")
        manifest: ModuleManifest | None = getattr(module, "Manifest", None)
        if manifest is None:
            return False
        entry = manifest.entry

        if manifest.dependencies_package:
            await loader_instance.logger.info(
                f"Loading dependency package: {manifest.dependencies_package}"
            )
            await package_dependency(loader_instance, manifest)
        if manifest.disable:
            return False
        entry_instance = _call_entry(entry, loader_instance.swit, manifest)

        match manifest.module_type:
            case ModuleType.PREFIX_COMMAND:
                await loader_instance.swit.add_cog(entry_instance)
            case ModuleType.SLASH_COMMAND:
                await loader_instance.swit.add_cog(entry_instance)
            case ModuleType.EVENT:
                await loader_instance.swit.add_cog(entry_instance)
            case ModuleType.COG:
                await loader_instance.swit.add_cog(entry_instance)
            case ModuleType.GROUP_COMMAND:
                loader_instance.swit.tree.add_command(entry_instance)
            case ModuleType.LOOP_EVENT:
                await loader_instance.logger.warning(f"[{manifest.name}] ModuleType.LOOP_EVENT is deprecated and will be removed in a future release. ""Please replace it with ModuleType.TASK_LOOP.")
                await loader_instance.swit.add_cog(entry_instance)
            case ModuleType.TASK_LOOP:
                await loader_instance.swit.add_cog(entry_instance)
            case ModuleType.HOOK_TO_SETUP_STEP:
                for name in ("hooker", "hook", "entry"):
                    value = getattr(module, name, None)
                    if value:
                        setup_step_hook_array.append(value)
            case ModuleType.CALL_SETUP_FUNC:
                setup = module.setup
                await setup(loader_instance.swit)
            case _:
                if entry:
                    await loader_instance.swit.add_cog(
                        _call_entry(entry, loader_instance.swit, manifest)
                    )

        loader_instance.registry.add(manifest.name, module)
        loader_instance.loaded_modules[manifest.name] = module
        metadata = _insert_metadata(module_path=module_path, entry=entry, manifest=manifest)
        loader_instance.module_metadata[manifest.name] = metadata

        return True

    except Exception as e:  # noqa: BLE001
        await loader_instance.logger.warning(f"Failed to load module: {module_path}")
        traceback.print_exc()
        await loader_instance.logger.warning(f"Info: {e}")
        return False