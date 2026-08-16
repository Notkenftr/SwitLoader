from pathlib import Path


root = Path(__file__).parents[1]

base = """from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from swit.app import Swit
from swit.api import ModuleManifest
from swit.api import ModuleType


class {module_class_name}(commands.Cog):
    def __init__(self,bot: Swit):
        self.bot = bot

    @app_commands.command(name="example",description="Example command")
    async def example(self,interaction: discord.Interaction):
        pass

async def setup(self,bot: Swit):
    self.bot.add_command({module_class_name}(bot))


Manifest = ModuleManifest(
    entry={module_class_name},
    module_type=ModuleType.CALL_SETUP_FUNC,
    name="{module_name}",
    description="",
    author=[],
    dependencies_package=[],
    dependencies_module=[]
)
"""

def main():
    module_name = str(input("Enter your module name: "))

    module_path = Path(root,"modules",module_name)
    module_path.mkdir(parents=True, exist_ok=True)

    module_entry_file = module_path / "module.txt"
    module_entry_file.touch(exist_ok=True)

    with open(module_entry_file,"w") as f:
        f.write(
            base.format(
                module_class_name = (module_name
                                    .replace("-","")
                                    .replace(" ","")
                                    .lower()
                                     ).strip().capitalize(),
                module_name = module_name,
            )
        )

if __name__ == '__main__':
    main()
