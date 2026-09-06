import inspect
import importlib


def hotswap_function(func):
    if callable(func):
        module = importlib.import_module(func.__module__)
        importlib.reload(module)
    else:
        raise TypeError("hotswap_function must be callable")
