from enum import IntEnum

class ModuleType(IntEnum):
    PREFIX_COMMAND = 0
    SLASH_COMMAND = 1
    GROUP_COMMAND = 2
    LOOP_EVENT = 3
    CALL_SETUP_FUNC = 4
