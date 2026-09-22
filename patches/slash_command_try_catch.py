import discord
from discord.app_commands import Command

_original_do_call = Command._do_call


def install_slash_command_try_catch_patch(swit):
    async def slash_command_try_catch_patch(
        self,
        interaction: discord.Interaction,
        params,
    ):
        try:
            return await _original_do_call(
                self,
                interaction,
                params,
            )
        except Exception as e:
            logger = swit.get_logger()

            command_info = {
                "name": self.name,
                "qualified_name": self.qualified_name,
                "module": self.callback.__module__,
                "callback": self.callback.__qualname__,
                "interaction_command": interaction.command,
                "user": interaction.user,
                "guild": interaction.guild,
                "channel": interaction.channel,
            }

            command_name = self.name
            qualified_name = self.qualified_name
            module = self.callback.__module__

            await logger.warning(f"-"*50)
            await logger.warning(
                "Error occurred while trying to execute slash command: "
                f"command info: {command_info}"
            )
            await logger.warning(f"-" * 50)
            await logger.error(e)
            await logger.warning(f"-" * 50)
            raise

    Command._do_call = slash_command_try_catch_patch