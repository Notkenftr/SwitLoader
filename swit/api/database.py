from __future__ import annotations

import asyncio
import json
import random

import aiofiles

from pathlib import Path
from swit.api import PathAPI

def name_to_path(name: str) -> Path:
    return PathAPI.join_path(
        "database",
        "modules_database",
        f"{name}.json",
        create_parent=True,
    )
class JsonDb:
    def __init__(self,database_file_name: str):
        self.database_file_name = database_file_name.removesuffix(".json")
        self.lock_table = {}
    async def create(self, database_name: str | None = None):
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
            /,
            retry_count: int = 0,
    ) -> None | bool:
        database_name = database_name or self.database_file_name
        if database_name is None:
            raise ValueError(
                "Either database_name or database_file_name must be provided."
            )
        if database_name in self.lock_table:
            if self.lock_table.get(database_name, False) is not True:
                if retry_count >= 50:
                    return False
                await asyncio.sleep(random.uniform(0.000001,0.0005))
                return await self.save(
                    data,
                    database_name,
                    indent,
                    retry_count=retry_count + 1,
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
                await f.write(json.dumps(data, indent=indent))
        finally:
            self.lock_table[database_name] = False

        return None