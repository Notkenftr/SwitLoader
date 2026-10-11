import asyncio
import os

import pytest

from swit.api.database import JsonDb, name_to_path


@pytest.mark.asyncio
async def test_json_db_create_and_load():
    db_name = "test_db_sample"
    db = JsonDb(db_name)
    path = name_to_path(db_name)

    try:
        if path.exists():
            os.remove(path)

        await db.create()
        assert path.exists()
        assert path.is_file()

        data = await db.load()
        assert data == {}

        await db.save({"key": "value", "count": 42})
        loaded = await db.load()
        assert loaded == {"key": "value", "count": 42}
    finally:
        if path.exists():
            os.remove(path)
        if path.parent.exists() and not os.listdir(path.parent):
            os.rmdir(path.parent)


@pytest.mark.asyncio
async def test_json_db_concurrent_saves():
    db_name = "test_concurrent_db"
    db = JsonDb(db_name)
    path = name_to_path(db_name)

    try:
        await db.create()

        async def worker(idx: int):
            for i in range(10):
                await db.save({"worker": idx, "iteration": i})

        await asyncio.gather(*(worker(w) for w in range(5)))

        result = await db.load()
        assert "worker" in result
        assert "iteration" in result
    finally:
        if path.exists():
            os.remove(path)
        if path.parent.exists() and not os.listdir(path.parent):
            os.rmdir(path.parent)
