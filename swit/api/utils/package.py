from __future__ import annotations

import importlib.metadata
import importlib.util
import shutil
import subprocess
import sys

PACKAGE_TO_MODULE = {
    "pyyaml": "yaml",
    "discord-py": "discord",
    "discord.py": "discord",
    "pillow": "PIL",
    "python-dateutil": "dateutil",
    "beautifulsoup4": "bs4",
    "pydantic-settings": "pydantic_settings",
}


def install_package(package_name: str, *, upgrade: bool = False) -> bool:
    """
    Check and install a Python package if missing.

    Args:
        package_name: Package name on PyPI.
        upgrade: Upgrade package if already installed.

    Returns:
        True if package is available.

    Raises:
        subprocess.CalledProcessError: If pip install fails.
    """
    from swit.api.cache import cache

    clean_name = package_name.strip()

    if not upgrade and cache.is_package_cached(clean_name):
        return True

    if not upgrade:
        try:
            importlib.metadata.distribution(clean_name)
            cache.cache_package(clean_name)
            return True
        except (importlib.metadata.PackageNotFoundError, ValueError):
            pass

        module_name = PACKAGE_TO_MODULE.get(clean_name.lower(), clean_name.replace("-", "_"))
        if importlib.util.find_spec(module_name) is not None:
            cache.cache_package(clean_name)
            return True

    if shutil.which("uv"):
        command = [
            "uv",
            "pip",
            "install",
            "--python",
            sys.executable,
        ]
    else:
        command = [
            sys.executable,
            "-m",
            "pip",
            "install",
        ]

    if upgrade:
        command.append("--upgrade")

    command.append(package_name)

    subprocess.check_call(command)

    return True
