from __future__ import annotations

from swit.app import Swit
from swit.api import ModuleManifest, ModuleType


async def setup(bot: Swit):
    print("hello world")
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