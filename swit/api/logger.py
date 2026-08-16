from __future__ import annotations

import asyncio
import os
from datetime import datetime
from enum import Enum

import aiofiles
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
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


class Logger:

    def __init__(self, debug: bool = False, custom_colors: dict[LoggerLevel, str] | None = None):
        self.debug_mode = debug
        self.log_path = PathAPI.join_path("logs")
        os.makedirs(self.log_path, exist_ok=True)
        self.log_file = self.get_log_name()
        self.lock = asyncio.Lock()
        self.colors = {**LEVEL_COLOR, **(custom_colors or {})}

    def get_log_name(self):
        date = datetime.now().strftime("%Y-%m-%d")
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

    async def _write(
            self,
            level: LoggerLevel,
            message: str
    ):
        timestamp = get_now()
        prefix = f"[{level.value}] [{timestamp}] "
        text = f"{prefix}{message}\n"
        color = self.colors.get(level, "")

        if level in (LoggerLevel.ERROR, LoggerLevel.FATAL):
            console.print(f"[{color}]{prefix}{message}[/]")
        elif level == LoggerLevel.SUCCESS:
            console.print(f"[{color}]{prefix}[/][bright_white]{message}[/]")
        else:
            print(f"{color}{prefix}{Style.RESET_ALL}{Fore.LIGHTWHITE_EX}{message}{Style.RESET_ALL}\n", end="")

        async with aiofiles.open(
                self.log_file,
                "a",
                encoding="utf-8"
        ) as file:
            await file.write(text)

    async def log(self, level: LoggerLevel, message: str):
        async with self.lock:
            await self._write(level, message)

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