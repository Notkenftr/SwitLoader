from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys


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

    module_name = package_name.replace("-", "_")

    if importlib.util.find_spec(module_name) is not None and not upgrade:
        return True

    if shutil.which("uv"):
        command = [
            "uv",
            "pip",
            "install",
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