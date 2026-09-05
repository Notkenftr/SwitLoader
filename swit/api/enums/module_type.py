from enum import IntEnum

class ModuleType(IntEnum):
    PREFIX_COMMAND = 0
    SLASH_COMMAND = 1
    GROUP_COMMAND = 2
    LOOP_EVENT = 3
    EVENT = 4
    COG = 5
    HOOK_TO_SETUP_STEP = 6
    CALL_SETUP_FUNC = 7
