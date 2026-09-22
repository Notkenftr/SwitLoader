from __future__ import annotations

import asyncio
import json
import random
from pathlib import Path

import aiofiles

from swit.api import PathAPI


def name_to_path(name: str) -> Path:
    return PathAPI.join_path(
        "database",
        "modules_database",
        f"{name}.json",
        create_parent=True,
    )
class JsonDb:
    """
    Asynchronous JSON database manager.

    ``JsonDb`` provides basic operations for creating, loading, and saving
    JSON-based databases. Each database is stored as a separate JSON file
    under the ``database/modules_database`` directory.

    The class also maintains a per-database lock table to prevent multiple
    save operations from modifying the same database simultaneously.

    :param database_file_name: Default database name used when no
        ``database_name`` is provided to an operation.
    """
    def __init__(self, database_file_name: str):
        """
        Initialize a JSON database manager.

        The ``.json`` suffix is removed from ``database_file_name`` if
        present. The resulting name is used as the default database name
        for database operations.

        :param database_file_name: Default database file name.
        """
        self.database_file_name = database_file_name.removesuffix(".json")
        self.lock_table = {}

    async def create(self, database_name: str | None = None):
        """
        Create an empty JSON database.

        If the database already exists, this method does nothing. Otherwise,
        a new database containing an empty JSON object is created.

        :param database_name: Name of the database to create. If omitted,
            ``database_file_name`` is used.
        :return: ``None``.
        """
        database_name = database_name or self.database_file_name
        if name_to_path(database_name).exists():
            return
        async with aiofiles.open(name_to_path(database_name), mode="w") as f:
            await f.write(json.dumps({}))

    async def create_with_default(
            self,
            database_name: str | None = None,
            default_jsondb_path: str | None = None,
            default_jsondb_dict: dict | None = None,
            /,
            indent: int = 4,
    ):
        """
        Create a JSON database using default data.

        The default data can either be loaded from an existing JSON file or
        provided directly as a dictionary. If the database already exists,
        this method does nothing.

        Exactly one source of default data should be provided through
        ``default_jsondb_path`` or ``default_jsondb_dict``.

        :param database_name: Name of the database to create. If omitted,
            ``database_file_name`` is used.
        :param default_jsondb_path: Path to a JSON file containing the
            default database data.
        :param default_jsondb_dict: Dictionary containing the default
            database data.
        :param indent: Number of spaces used for JSON indentation.
        :raises ValueError: If neither ``default_jsondb_path`` nor
            ``default_jsondb_dict`` is provided.
        :return: ``None``.
        """
        if default_jsondb_path is None and default_jsondb_dict is None:
            raise ValueError(
                "Either default_jsondb_path or default_jsondb_dict must be provided."
            )
        database_name = database_name or self.database_file_name
        if database_name is None:
            raise ValueError(
                "Either database_name or database_file_name must be provided."
            )
        if name_to_path(database_name).exists():
            return
        if default_jsondb_path is not None:
            async with aiofiles.open(default_jsondb_path, mode="r") as f:
                data = json.loads(await f.read())
        else:
            data = default_jsondb_dict
        async with aiofiles.open(name_to_path(database_name), mode="w") as f:
            await f.write(json.dumps(data, indent=indent))

    async def load(self, database_name: str | None = None) -> dict:
        """
        Load and parse a JSON database.

        The database file is read asynchronously and its JSON contents are
        deserialized into a Python dictionary.

        :param database_name: Name of the database to load. If omitted,
            ``database_file_name`` is used.
        :raises ValueError: If no database name is available.
        :raises FileNotFoundError: If the database file does not exist.
        :raises json.JSONDecodeError: If the database contains invalid JSON.
        :return: The parsed database contents.
        """
        database_name = database_name or self.database_file_name
        if database_name is None:
            raise ValueError(
                "Either database_name or database_file_name must be provided."
            )
        async with aiofiles.open(name_to_path(database_name), mode="r") as f:
            return json.loads(await f.read())

    async def save(
            self,
            data: dict,
            database_name: str | None = None,
            indent: int = 4,
            waiting_table_rand_a: float = 0.000001,
            waiting_table_rand_b: float = 0.0005,
            /,
            dyn_retry_count: int = 0,
    ) -> None | bool:
        """
        Save a complete database to a JSON file.

        The provided dictionary replaces the entire contents of the selected
        database. The operation uses a per-database lock to prevent concurrent
        save operations from writing to the same database at the same time.

        If the database is currently locked, the method waits for a random
        interval between ``waiting_table_rand_a`` and
        ``waiting_table_rand_b`` seconds before retrying. After 50 retry
        attempts, ``False`` is returned.

        :param data: Complete database contents to save.
        :param database_name: Name of the database to save. If omitted,
            ``database_file_name`` is used.
        :param indent: Number of spaces used for JSON indentation.
        :param waiting_table_rand_a: Minimum waiting time in seconds before
            retrying.
        :param waiting_table_rand_b: Maximum waiting time in seconds before
            retrying.
        :param dyn_retry_count: Internal retry counter used when waiting for
            another save operation to finish.
        :raises ValueError: If no database name is available.
        :raises RuntimeError: If the specified database does not exist.
        :return: ``None`` when the database is saved successfully, or
            ``False`` if the maximum number of retries is reached.
        """
        database_name = database_name or self.database_file_name

        if database_name is None:
            raise ValueError(
                "Either database_name or database_file_name must be provided."
            )

        if database_name in self.lock_table and self.lock_table.get(database_name, False) is not True:
            if dyn_retry_count >= 50:
                return False

            await asyncio.sleep(
                random.uniform(
                    waiting_table_rand_a,
                    waiting_table_rand_b,
                )
            )

            return await self.save(
                data,
                database_name,
                indent,
                waiting_table_rand_a,
                waiting_table_rand_b,
                dyn_retry_count=dyn_retry_count + 1,
            )

        self.lock_table[database_name] = True

        try:
            if not name_to_path(database_name).exists():
                raise RuntimeError(
                    f"database {database_name} does not exist"
                )

            async with aiofiles.open(
                    name_to_path(database_name),
                    mode="w",
            ) as f:
                await f.write(
                    json.dumps(data, indent=indent)
                )

        finally:
            self.lock_table[database_name] = False

        return None