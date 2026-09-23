import inspect


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
    entry = module.Manifest.entry

    cog = loader_instance.swit.get_cog(entry.__name__)

    if cog is None:
        if debug:
            return False, "Err: cog not found"
        return False

    if hasattr(cog, "on_unload"):
        on_unload_func = cog.on_unload

        try:
            result = on_unload_func()

            if inspect.isawaitable(result):
                await result
        except Exception as e:
            import traceback
            await loader_instance.logger.warning(f"Failed to unload module: {name}")
            await loader_instance.logger.error(
                traceback.format_exc()
            )
            if debug:
                return False, f"Err: on_unload failed: {e}"
            return False
    try:
        await loader_instance.swit.remove_cog(entry.__name__)
    except Exception as e:
        import traceback
        await loader_instance.logger.warning(f"Failed to unload module: {name}")
        await loader_instance.logger.error(traceback.format_exc())
        if debug:
            return False, f"Err: remove cog failed: {e}"
        return False
    loader_instance.loaded_modules.pop(name, None)
    loader_instance.module_metadata.pop(name, None)
    if debug:
        return True, "OK: module unloaded"
    return True