
from typing import Type

from swit.api.enums.module_type import ModuleType


class ModuleManifest:
    __slots__ = ['entry',
                 'module_type',
                 'name',
                 'description',
                 'author',
                 'dependencies_package',
                 'dependencies_module']
    def __init__(self,
                 /,
                 entry: Type[object],
                 module_type: ModuleType,
                 name: str,
                 description: str,
                 author: list[str] = None,
                 dependencies_package: list[str] = None,
                 dependencies_module: list[str] = None
                 ):

        self.entry = entry
        self.module_type = module_type
        self.name = name
        self.description = description
        self.author = author
        self.dependencies_package = dependencies_package
        self.dependencies_module = dependencies_module

