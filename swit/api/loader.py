from swit.context import get_swit


def get_module(module_name: str):
    """
    Get a loaded module by its name from the active Swit instance.
    """
    bot = get_swit()
    if bot and bot.loader:
        return bot.loader.get_module_by_name(module_name)
    return None
