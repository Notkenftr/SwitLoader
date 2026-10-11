from __future__ import annotations

import asyncio
import atexit
import os
from datetime import datetime
from enum import Enum

from colorama import Fore, Style, init
from rich.console import Console

from swit.api.utils.path_api import PathAPI

init(autoreset=True)
console = Console()


class LoggerLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"
    SUCCESS = "SUCCESS"


LEVEL_COLOR = {
    LoggerLevel.DEBUG: Fore.CYAN,
    LoggerLevel.INFO: Fore.GREEN,
    LoggerLevel.WARNING: Fore.YELLOW,
    LoggerLevel.ERROR: "bold white on red",
    LoggerLevel.FATAL: "bold white on red",
    LoggerLevel.SUCCESS: "bright_green",
}


def get_now():
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")

class Logger:
    INSTANCE = None

    def __new__(cls, *args, **kwargs):
        if not cls.INSTANCE:
            cls.INSTANCE = super().__new__(cls)
        return cls.INSTANCE

    def __init__(
        self, debug: bool = False, custom_colors: dict[LoggerLevel, str] | None = None
    ):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.debug_mode = debug
        self.log_path = PathAPI.join_path("logs")
        os.makedirs(self.log_path, exist_ok=True)
        self.log_file = self.get_log_name()
        self.colors = {**LEVEL_COLOR, **(custom_colors or {})}

        # Persistent open file handle to avoid open/close I/O penalty on each log line
        self._file = open(self.log_file, "a", encoding="utf-8")  # noqa: SIM115
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._worker_task: asyncio.Task | None = None
        atexit.register(self._sync_flush)

    def _sync_flush(self):
        """Flush remaining logs on process exit."""
        try:
            while not self._queue.empty():
                text = self._queue.get_nowait()
                if self._file and not self._file.closed:
                    self._file.write(text)
            if self._file and not self._file.closed:
                self._file.flush()
                self._file.close()
        except Exception:  # noqa: BLE001, S110
            pass

    def get_log_name(self):
        date = datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M-%S")
        base_name = f"{date}.log"
        file_path = os.path.join(self.log_path, base_name)

        if not os.path.exists(file_path):
            return file_path

        counter = 1
        while True:
            new_name = f"{date}-{counter}.log"
            file_path = os.path.join(self.log_path, new_name)
            if not os.path.exists(file_path):
                return file_path
            counter += 1

    def _ensure_worker(self):
        if self._worker_task is None or self._worker_task.done():
            try:
                loop = asyncio.get_running_loop()
                self._worker_task = loop.create_task(self._log_writer())
            except RuntimeError:
                pass

    async def _log_writer(self):
        """Background worker that batches and writes queued logs to file."""
        while True:
            try:
                # Wait for next item
                text = await self._queue.get()
                batch = [text]

                # Drain available items in queue for bulk write
                while not self._queue.empty() and len(batch) < 100:
                    try:
                        batch.append(self._queue.get_nowait())
                    except asyncio.QueueEmpty:
                        break

                if self._file and not self._file.closed:
                    self._file.write("".join(batch))
                    self._file.flush()

                for _ in range(len(batch)):
                    self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception:  # noqa: BLE001, S110
                pass

    async def _write(self, level: LoggerLevel, message: str):
        timestamp = get_now()
        prefix = f"[{level.value}] [{timestamp}] "
        text = f"{prefix}{message}\n"
        color = self.colors.get(level, "")

        if level in (LoggerLevel.ERROR, LoggerLevel.FATAL):
            console.print(f"[{color}]{prefix}{message}[/]")
        elif level == LoggerLevel.SUCCESS:
            console.print(f"[{color}]{prefix}[/][bright_white]{message}[/]")
        else:
            print(
                f"{color}{prefix}{Style.RESET_ALL}{Fore.LIGHTWHITE_EX}{message}{Style.RESET_ALL}\n",
                end="",
            )

        self._ensure_worker()
        if self._worker_task and not self._worker_task.done():
            self._queue.put_nowait(text)
        else:
            # Direct write fallback before loop starts
            if self._file and not self._file.closed:
                self._file.write(text)
                self._file.flush()

    async def log(self, level: LoggerLevel, message: str):
        await self._write(level, message)

    async def flush(self):
        """Wait for all queued log lines to be flushed to disk."""
        if not self._queue.empty():
            await self._queue.join()
        if self._file and not self._file.closed:
            self._file.flush()

    async def debug(self, message: str):
        if self.debug_mode:
            await self.log(LoggerLevel.DEBUG, message)

    async def info(self, message: str):
        await self.log(LoggerLevel.INFO, message)

    async def warning(self, message: str):
        await self.log(LoggerLevel.WARNING, message)

    async def error(self, message: str):
        await self.log(LoggerLevel.ERROR, message)

    async def fatal(self, message: str):
        await self.log(LoggerLevel.FATAL, message)

    async def success(self, message: str):
        await self.log(LoggerLevel.SUCCESS, message)

    async def using(self, obj, user, *, message_method=False):
        if message_method:
            content = (
                f"User {user.author.name} "
                f"({user.author.id}) "
                f"used command "
                f"{obj.__class__.__name__}"
            )
        else:
            content = (
                f"User {user.user.name} "
                f"({user.user.id}) "
                f"used command "
                f"{obj.__class__.__name__}"
            )

        await self.info(content)