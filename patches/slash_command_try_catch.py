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
            await swit.get_logger().error(e)
            raise

    Command._do_call = slash_command_try_catch_patch