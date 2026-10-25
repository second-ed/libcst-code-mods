from collections.abc import Callable

import libcst as cst

CST_TYPES = {}


def cst_register(key: str) -> Callable[[Callable[..., cst.CSTNode]], Callable[..., cst.CSTNode]]:
    def wrapper(func: Callable[..., cst.CSTNode]) -> Callable[..., cst.CSTNode]:
        CST_TYPES[key] = func()
        return func

    return wrapper
