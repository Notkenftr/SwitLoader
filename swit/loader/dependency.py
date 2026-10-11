from __future__ import annotations

import asyncio
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from swit.api.types.module_manifest import ModuleManifest
    from swit.loader.loader import Loader


import importlib.metadata
import importlib.util

from swit.api.cache import cache


def get_package_manager() -> list[str]:
    if shutil.which("uv") is not None:
        return ["uv", "pip"]

    return [sys.executable, "-m", "pip"]


def package_exists(package: str) -> bool:
    clean_name = package.strip()
    if cache.is_package_cached(clean_name):
        return True

    try:
        importlib.metadata.distribution(clean_name)
        cache.cache_package(clean_name)
        return True
    except (importlib.metadata.PackageNotFoundError, ValueError):
        pass

    module_name = clean_name.replace("-", "_")
    if importlib.util.find_spec(module_name) is not None:
        cache.cache_package(clean_name)
        return True

    command = [
        *get_package_manager(),
        "show",
        clean_name,
    ]
    result = subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode == 0:
        cache.cache_package(clean_name)
        return True
    return False


async def install_dependency(package: str) -> bool:
    pm = get_package_manager()
    if pm[0] == "uv":
        command = [*pm, "install", "--python", sys.executable, package]
    else:
        command = [*pm, "install", package]
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await process.communicate()
    if process.returncode != 0:
        error = stderr.decode(errors="replace")

        raise RuntimeError(f"Failed to install package '{package}':\n{error}")
    cache.cache_package(package)
    return True


async def package_dependency(
    loader: Loader,
    manifest: ModuleManifest,
):

    for package in manifest.dependencies_package:
        package = package.strip()
        if not package:
            continue

        if cache.is_package_cached(package):
            continue

        await loader.logger.info(f"Checking dependency: {package}")

        if package_exists(package):
            await loader.logger.info(f"Dependency {package} already installed")
            continue

        await loader.logger.info(f"Package {package} not installed, installing...")
        try:
            await install_dependency(package)
        except Exception as exc:
            await loader.logger.error(f"Failed to install dependency {package}: {exc}")
            raise
        await loader.logger.info(f"Successfully installed {package}")
