from pathlib import Path


root = Path(__file__).parents[1]


TEMPLATES = {

    "PREFIX_COMMAND": """from __future__ import annotations

import discord
from discord.ext import commands

from swit.app import Swit
from swit.api import ModuleManifest, ModuleType


class {module_class_name}(commands.Cog):

    def __init__(self, bot: Swit):
        self.bot = bot

    @commands.command(name="example")
    async def example(self, ctx: commands.Context):
        await ctx.send("Hello from SwitLoader!")


Manifest = ModuleManifest(
    entry={module_class_name},
    module_type=ModuleType.PREFIX_COMMAND,
    name="{module_name}",
    description="",
    author=[],
    dependencies_package=[],
    dependencies_module=[]
)
""",

    "SLASH_COMMAND": """from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from swit.app import Swit
from swit.api import ModuleManifest, ModuleType


class {module_class_name}(commands.Cog):

    def __init__(self, bot: Swit):
        self.bot = bot

    @app_commands.command(
        name="example",
        description="Example command"
    )
    async def example(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Hello from SwitLoader!"
        )


Manifest = ModuleManifest(
    entry={module_class_name},
    module_type=ModuleType.SLASH_COMMAND,
    name="{module_name}",
    description="",
    author=[],
    dependencies_package=[],
    dependencies_module=[]
)
""",

    "GROUP_COMMAND": """from __future__ import annotations

import discord
from discord import app_commands

from swit.app import Swit
from swit.api import ModuleManifest, ModuleType


class {module_class_name}(app_commands.Group):

    def __init__(self, bot: Swit):
        super().__init__(
            name="{module_name}",
            description="Example command group"
        )

        self.bot = bot

    @app_commands.command(
        name="example",
        description="Example command"
    )
    async def example(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Hello from SwitLoader!"
        )


Manifest = ModuleManifest(
    entry={module_class_name},
    module_type=ModuleType.GROUP_COMMAND,
    name="{module_name}",
    description="",
    author=[],
    dependencies_package=[],
    dependencies_module=[]
)
""",

    "LOOP_EVENT": """from __future__ import annotations

from discord.ext import commands, tasks

from swit.app import Swit
from swit.api import ModuleManifest, ModuleType


class {module_class_name}(commands.Cog):

    def __init__(self, bot: Swit):
        self.bot = bot
        self.example_loop.start()

    @tasks.loop(seconds=60)
    async def example_loop(self):
        await self.bot.logger.info(
            "Loop event is running..."
        )

    @example_loop.before_loop
    async def before_example_loop(self):
        await self.bot.wait_until_ready()


Manifest = ModuleManifest(
    entry={module_class_name},
    module_type=ModuleType.LOOP_EVENT,
    name="{module_name}",
    description="",
    author=[],
    dependencies_package=[],
    dependencies_module=[]
)
""",

    "CALL_SETUP_FUNC": """from __future__ import annotations

from swit.app import Swit
from swit.api import ModuleManifest, ModuleType


async def setup(bot: Swit):

    pass


Manifest = ModuleManifest(
    entry=setup,
    module_type=ModuleType.CALL_SETUP_FUNC,
    name="{module_name}",
    description="",
    author=[],
    dependencies_package=[],
    dependencies_module=[]
)
""",
}


MODULE_TYPES = tuple(TEMPLATES)


def get_class_name(module_name: str) -> str:
    return "".join(
        part.capitalize()
        for part in module_name.replace("-", " ").split()
    )


def create_workspace(module_name: str, module_type: str):
    module_path = Path(root, "modules", module_name)
    module_path.mkdir(parents=True, exist_ok=True)

    module_file = module_path / "module.py"

    module_file.write_text(
        TEMPLATES[module_type].format(
            module_name=module_name,
            module_class_name=get_class_name(module_name),
        ),
        encoding="utf-8",
    )

    return module_path


def build_workspace():

    print("=== SwitLoader Workspace Setup ===")
    print()

    module_name = input("Enter your module name: ").strip()

    if not module_name:
        print("Module name cannot be empty.")
        return

    print()
    print("Available Module Types:")
    print()

    for index, module_type in enumerate(MODULE_TYPES, 1):
        print(f"{index}. {module_type}")

    print()
    print(
        "Documentation: "
        "https://swittlab.github.io/SwitLoader.docs/module_type/"
    )
    print()

    try:
        module_index = int(input("Select module type: ")) - 1
        module_type = MODULE_TYPES[module_index]
    except (ValueError, IndexError):
        print("Invalid module type.")
        return

    module_path = create_workspace(
        module_name,
        module_type,
    )

    print()
    print("Workspace created successfully!")
    print()
    print(f"Module: {module_name}")
    print(f"Type:   {module_type}")
    print(f"Path:   {module_path}")
    print(f"File:   {module_path / 'module.py'}")


