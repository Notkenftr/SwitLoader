from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from swit.api import Swit

_swit: Swit | None = None

def set_swit(instance: Swit) -> None:
    global _swit

    if _swit is not None and _swit is not instance:
        raise RuntimeError("Swit instance has already been initialized")

    _swit = instance


def get_swit() -> Swit:
    if _swit is None:
        raise RuntimeError("Swit has not been initialized yet")
    return _swit