from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from swit.api.types.module_manifest import ModuleManifest
    from swit.loader.loader import Loader

from swit.api.utils.package import install_package

def dependency(loader: Loader,manifest: ModuleManifest):
    pass