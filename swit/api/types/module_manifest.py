from collections.abc import Callable
from typing import Any

from swit.api.enums.module_type import ModuleType



class ModuleManifest:
    __slots__ = [
        "_metadata",
        "author",
        "dependencies_module",
        "dependencies_package",
        "description",
        "disable",
        "entry",
        "module_type",
        "name"
    ]

    def __init__(
        self,
        /,
        entry: type[Any] | Callable[..., Any],
        module_type: ModuleType,
        name: str,
        description: str,
        author: list[str] | None = None,
        dependencies_package: list[str] | None = None,
        dependencies_module: list[str] | None = None,
        disable: bool = False,
    ):

        self.entry = entry
        self.module_type = module_type
        self.name = name
        self.description = description
        self.author = author
        self.dependencies_package = dependencies_package
        self.dependencies_module = dependencies_module
        self.disable = disable

        #do not edit this
        self._metadata = {}
