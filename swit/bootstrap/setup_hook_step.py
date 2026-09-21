import discord
import inspect

def _setup_intents(intents_config: dict) -> discord.Intents:
    intents = discord.Intents.default()

    for name, value in intents_config.items():
        if name in ["auto_detect", "all", "default"]:
            continue
        if not hasattr(intents, name):
            raise ValueError(f"Invalid Discord intent: {name}")
        setattr(intents, name, value)

    return intents

async def _load_hooker(self,setup_step_hook):
    for func in setup_step_hook:
        if callable(func):
            await self.logger.debug(f"Running {func.__name__}")
            try:
                if inspect.iscoroutinefunction(func):
                    await func(self)
                else:
                    func(self)
            except Exception as e:  # noqa: BLE001
                await self.logger.error(e)
        else:
            await self.logger.error(f"{func.__name__} is not callable")
            continue