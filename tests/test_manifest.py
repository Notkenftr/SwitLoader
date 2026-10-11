from swit.api.enums.module_type import ModuleType
from swit.api.types.module_manifest import ModuleManifest


def test_module_manifest_initialization():
    dummy_entry = lambda bot: None

    manifest = ModuleManifest(
        entry=dummy_entry,
        module_type=ModuleType.SLASH_COMMAND,
        name="TestModule",
        description="A test module",
        author=["Tester"],
        dependencies_package=["rich"],
        dependencies_module=[],
    )

    assert manifest.name == "TestModule"
    assert manifest.module_type == ModuleType.SLASH_COMMAND
    assert manifest.author == ["Tester"]
    assert manifest.disable is False
    assert isinstance(manifest._metadata, dict)
