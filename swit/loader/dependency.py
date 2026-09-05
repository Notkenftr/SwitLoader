from __future__ import annotations

import asyncio
import importlib.util
import shutil
import subprocess
import sys

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from swit.api.types.module_manifest import ModuleManifest
    from swit.loader.loader import Loader


def get_package_manager() -> list[str]:
    if shutil.which("uv") is not None:
        return ["uv", "pip"]

    return [sys.executable, "-m", "pip"]

def package_exists(package: str) -> bool:
    command = [
        *get_package_manager(),
        "show",
        package,
    ]
    result = subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0

async def install_dependency(package: str) -> bool:
    command = [
        *get_package_manager(),
        "install",
        package,
    ]
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        error = stderr.decode(errors="replace")

        raise RuntimeError(
            f"Failed to install package '{package}':\n"
            f"{error}"
        )
    return True


async def package_dependency(
    loader: Loader,
    manifest: ModuleManifest,
):

    for package in manifest.dependencies_package:
        package = package.strip()
        if not package:
            continue
        await loader.logger.info(
            f"Checking dependency: {package}"
        )

        if package_exists(package):
            await loader.logger.info(
                f"Dependency {package} already installed"
            )
            continue

        await loader.logger.info(
            f"Package {package} not installed, installing..."
        )
        try:
            await install_dependency(package)
        except Exception as exc:
            await loader.logger.error(
                f"Failed to install dependency "
                f"{package}: {exc}"
            )
            raise
        await loader.logger.info(
            f"Successfully installed {package}"
        )