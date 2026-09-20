from pathlib import Path


root = Path(__file__).parents[1]


def get_class_name(module_name: str) -> str:
    return "".join(
        part.capitalize()
        for part in module_name.replace("-", "_").split("_")
    )


def get_module_patterns() -> dict[str, str]:
    pattern_path = root / "cli" / "pattern"

    result = {}

    for file in pattern_path.iterdir():
        if file.is_file() and file.suffix == ".py":
            result[file.stem] = file.read_text(encoding="utf-8")

    return result


def create_workspace(
    module_name: str,
    module_pattern: str,
    module_pattern_data: dict[str, str],
) -> Path:
    externals_path = [
        "views",
        "utils",
        "logic",
        "services",
        "configs",
        "assets",
    ]

    module_path = root / "modules" / module_name
    module_path.mkdir(parents=True, exist_ok=True)

    template = module_pattern_data[module_pattern]

    module_content = (
        template
        .replace("ModuleName", module_name)
        .replace(
            "ModuleClassName",
            get_class_name(module_name),
        )
        .replace("{module_name}", module_name)
    )

    for external_path in externals_path:
        path = module_path / external_path

        if "." not in external_path:
            path.mkdir(
                parents=True,
                exist_ok=True,
            )
        else:
            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            path.touch(exist_ok=True)

    module_file = module_path / "module.py"

    module_file.write_text(
        module_content,
        encoding="utf-8",
    )

    return module_path


def build_workspace() -> None:
    print("Workspace Setup:\n")

    module_name = input("> Enter your module name: ").strip()

    if not module_name:
        print("Module name cannot be empty.")
        return

    module_pattern_data = get_module_patterns()

    if not module_pattern_data:
        print("No module patterns found.")
        return

    print()
    print("Available Module Pattern:")
    print()

    module_patterns = list(module_pattern_data)
    print("index | module name")
    for index, module_pattern in enumerate(module_patterns, start=1):
        padding = " " * (2 - len(str(index)))
        print(f"{index}.{padding}   {module_pattern.upper()}")

    try:
        module_index = int(
            input("Select module pattern: ")
        ) - 1

        module_pattern = module_patterns[module_index]

    except (ValueError, IndexError):
        print("Invalid module pattern.")
        return

    module_path = create_workspace(
        module_name=module_name,
        module_pattern=module_pattern,
        module_pattern_data=module_pattern_data,
    )

    print()
    print("Workspace created successfully!")
    print()
    print(f"Module: {module_name}")
    print(f"Pattern:   {module_pattern}")
    print(f"Path:   {module_path}")
    print(f"File:   {module_path / 'module.py'}")


if __name__ == "__main__":
    build_workspace()