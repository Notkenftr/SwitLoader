from __future__ import annotations

from swit.api import ModuleManifest, ModuleType
from swit.app import Swit


async def hooker(bot: Swit):
    pass


Manifest = ModuleManifest(
    entry=hooker,
    module_type=ModuleType.HOOK_TO_SETUP_STEP,
    name="{module_name}",
    description="",
    author=[],
    dependencies_package=[],
    dependencies_module=[]
)