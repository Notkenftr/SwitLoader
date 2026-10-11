from __future__ import annotations

import inspect
import sys
import traceback

from swit.api.enums.module_type import ModuleType


async def _unload_module_by_name(
    loader_instance,
    name: str,
    /,
    debug: bool = False,
) -> bool | tuple[bool, str]:
    if name not in loader_instance.loaded_modules:
        if debug:
            return False, "Err: module not loaded"
        return False

    module = loader_instance.loaded_modules[name]
    manifest = getattr(module, "Manifest", None)
    if manifest is None:
        if debug:
            return False, "Err: module has no Manifest"
        return False

    entry = manifest.entry

    # Handle Group Command
    if manifest.module_type == ModuleType.GROUP_COMMAND:
        cmd_name = getattr(entry, "name", name)
        loader_instance.swit.tree.remove_command(cmd_name)
    else:
        # Handle Cogs
        cog_name = getattr(entry, "__name__", str(entry))
        cog = loader_instance.swit.get_cog(cog_name)

        if cog is not None:
            if hasattr(cog, "on_unload"):
                on_unload_func = cog.on_unload
                try:
                    result = on_unload_func()
                    if inspect.isawaitable(result):
                        await result
                except Exception as e:  # noqa: BLE001
                    await loader_instance.logger.warning(f"Failed to unload module: {name}")
                    await loader_instance.logger.error(traceback.format_exc())
                    if debug:
                        return False, f"Err: on_unload failed: {e}"
                    return False
            try:
                await loader_instance.swit.remove_cog(cog_name)
            except Exception as e:  # noqa: BLE001
                await loader_instance.logger.warning(f"Failed to unload module: {name}")
                await loader_instance.logger.error(traceback.format_exc())
                if debug:
                    return False, f"Err: remove cog failed: {e}"
                return False

    loader_instance.loaded_modules.pop(name, None)
    loader_instance.module_metadata.pop(name, None)

    # Clean up registry
    if hasattr(loader_instance, "registry") and hasattr(loader_instance.registry, "modules"):
        loader_instance.registry.modules.pop(name, None)

    # Clean up sys.modules
    sys.modules.pop(f"swit_modules.{name}", None)

    if debug:
        return True, "OK: module unloaded"
    return True