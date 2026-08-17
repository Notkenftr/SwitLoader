from swit.app import Swit

from swit.context import get_swit

def get_swit_instance() -> Swit:
    """
    This function helps you get an instance of swit.
    :return: Swit instance
    """
    return get_swit()