import importlib


def hotswap_function(func):
    """
    Reload the module containing the specified function.

    This function uses the function's ``__module__`` attribute to locate
    its module and reloads that module using :func:`importlib.reload`.

    Reloading the module updates its module-level definitions, but existing
    references to objects imported from that module may still point to the
    previous objects.

    :param func: A callable whose containing module should be reloaded.
    :raises TypeError: If ``func`` is not callable.
    :return: ``None``.
    """
    if callable(func):
        module = importlib.import_module(func.__module__)
        importlib.reload(module)
    else:
        raise TypeError("hotswap_function must be callable")