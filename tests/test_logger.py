import os

import pytest

from swit.api.logger import Logger


@pytest.mark.asyncio
async def test_logger_queued_writes():
    logger = Logger(debug=True)
    await logger.info("Test queued log info")
    await logger.debug("Test queued log debug")
    await logger.success("Test queued log success")
    await logger.flush()

    assert os.path.exists(logger.log_file)
    with open(logger.log_file, "r", encoding="utf-8") as f:  # noqa: ASYNC230
        content = f.read()
    assert "Test queued log info" in content
    assert "Test queued log debug" in content
    assert "Test queued log success" in content
