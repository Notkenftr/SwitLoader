from __future__ import annotations

import threading,asyncio
import sys, functools, linecache
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from swit.app import Swit


async def object_information(obj, swit: "Swit"):
    """
    Display information about an object for testing and debugging purposes.

    :param obj: The object whose information will be displayed.
    :param swit: The Swit instance used to access the logger.
    :return: None.
    """

    logger = swit.get_logger()
    await logger.info(f"{'==' * 15} Object: {obj}{'==' * 15}")
    await logger.info(f"Object ID: {obj.id}")
    await logger.info(f"Object Parent: {obj.parent}")
    await logger.info(f"Type: {type(obj)}")
    for name in dir(obj):
        try:
            await logger.info(f"{name}: {getattr(obj, name)}")
        except Exception as e: # noqa: BLE001
            await logger.info(f"{name}: <error: {e}>")

    await logger.info(f"{'==' * 15} End {'==' * 15}")

def function_debug(func):
    """
    A decorator used to trace the execution of a function,
    allowing you to see which line the function has reached.

    This decorator should be removed after testing/debugging is complete,
    as tracing can affect performance.

    :param func: The function to be debugged.
    :return: A wrapped function with execution tracing enabled.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Start debug: {func.__name__}")
        start = time.time()

        def trace(frame, event, arg):
            if event == "line" and frame.f_code is func.__code__:
                filename = frame.f_code.co_filename
                lineno = frame.f_lineno
                source = linecache.getline(filename, lineno).strip()
                print(f"[{filename}:{lineno}] {source}")

            return trace

        sys.settrace(trace)
        try:
            return func(*args, **kwargs)
        finally:
            sys.settrace(None)
            print(f"Done after: {round(time.time() - start, 10)}s")

    return wrapper

if __name__ == "__main__":
    @function_debug
    def main():
        a = 1
        b = 2
        c = 3

    main()