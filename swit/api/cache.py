from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Self

from swit.api.utils.path_api import PathAPI


class CacheManager:
    """
    Manages project runtime cache in the `.cache/` directory.

    Caches installed package checks, requirements file hash,
    and general metadata to accelerate startup and minimize redundant I/O.
    """

    _instance: CacheManager | None = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_cache()
        return cls._instance

    def _init_cache(self) -> None:
        self.cache_dir: Path = PathAPI.join_path(".cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.packages_file = self.cache_dir / "packages.json"
        self.req_hash_file = self.cache_dir / "requirements.hash"
        self._packages: set[str] = self._load_packages()

    def _load_packages(self) -> set[str]:
        if not self.packages_file.exists():
            return set()
        try:
            with self.packages_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return set(data) if isinstance(data, list) else set()
        except Exception:  # noqa: BLE001
            return set()

    def _save_packages(self) -> None:
        try:
            temp_file = self.packages_file.with_suffix(".tmp")
            with temp_file.open("w", encoding="utf-8") as f:
                json.dump(sorted(self._packages), f, indent=2)
            temp_file.replace(self.packages_file)
        except Exception:  # noqa: BLE001, S110
            pass

    @staticmethod
    def _normalize(name: str) -> str:
        return name.strip().lower().replace("-", "_")

    def is_package_cached(self, package_name: str) -> bool:
        """Check if package has already been verified and cached."""
        return self._normalize(package_name) in self._packages

    def cache_package(self, package_name: str) -> None:
        """Add verified package to cache."""
        norm = self._normalize(package_name)
        if norm not in self._packages:
            self._packages.add(norm)
            self._save_packages()

    def cache_packages(self, package_names: list[str]) -> None:
        """Add multiple packages to cache."""
        changed = False
        for name in package_names:
            norm = self._normalize(name)
            if norm and norm not in self._packages:
                self._packages.add(norm)
                changed = True
        if changed:
            self._save_packages()

    def is_requirements_synced(self, req_path: Path | None = None) -> bool:
        """Check if requirements.txt is unchanged since last recorded sync."""
        path = req_path or Path(PathAPI.join_path("requirements.txt"))
        if not path.exists() or not self.req_hash_file.exists():
            return False
        try:
            current_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            saved_hash = self.req_hash_file.read_text(encoding="utf-8").strip()
            return current_hash == saved_hash
        except Exception:  # noqa: BLE001
            return False

    def save_requirements_sync(self, req_path: Path | None = None) -> None:
        """Save current hash of requirements.txt to cache."""
        path = req_path or Path(PathAPI.join_path("requirements.txt"))
        if not path.exists():
            return
        try:
            current_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            self.req_hash_file.write_text(current_hash, encoding="utf-8")
        except Exception:  # noqa: BLE001, S110
            pass

    def get(self, key: str) -> Any | None:
        """Retrieve custom cached JSON data by key."""
        file_path = self.cache_dir / f"{key}.json"
        if not file_path.exists():
            return None
        try:
            with file_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:  # noqa: BLE001
            return None

    def set(self, key: str, value: Any) -> None:
        """Store custom data as JSON in cache."""
        file_path = self.cache_dir / f"{key}.json"
        try:
            temp_file = file_path.with_suffix(".tmp")
            with temp_file.open("w", encoding="utf-8") as f:
                json.dump(value, f, indent=2)
            temp_file.replace(file_path)
        except Exception:  # noqa: BLE001, S110
            pass

    def clear(self) -> None:
        """Clear all cached files."""
        self._packages.clear()
        for file in self.cache_dir.iterdir():
            if file.is_file():
                try:
                    file.unlink()
                except Exception:  # noqa: BLE001, S110
                    pass


# Global singleton instance
cache = CacheManager()
