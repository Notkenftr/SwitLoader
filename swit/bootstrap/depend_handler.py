from __future__ import annotations

import re
from pathlib import Path

from swit.api.cache import cache
from swit.api.utils.package import install_package
from swit.api.utils.path_api import PathAPI


def depend_handler():
    req_path = Path(PathAPI.join_path("requirements.txt"))
    if not req_path.exists():
        return

    if cache.is_requirements_synced(req_path):
        return

    with open(req_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    packages_to_cache = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        line = line.split("#")[0].strip()
        match = re.match(r"^([A-Za-z0-9_.\-]+)", line)
        if not match:
            continue
        package = match.group(1).strip()
        if package:
            if not cache.is_package_cached(package):
                install_package(package)
            packages_to_cache.append(package)

    cache.cache_packages(packages_to_cache)
    cache.save_requirements_sync(req_path)
