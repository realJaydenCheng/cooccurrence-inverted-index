import functools
import time
from typing import Callable

from pympler import asizeof

from .co_occ import _NetworkConstructor


def _time_recode(func: Callable):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        result.time = end - start

        return result

    return wrapper


def _memory_recode(func: Callable):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        result.memory = asizeof.asizeof(result)/1024

        return result

    return wrapper


def profile(constructor: _NetworkConstructor) -> _NetworkConstructor:
    constructor.get_network_time = _time_recode(constructor.get_network)
    constructor.get_network_memory = _memory_recode(constructor.get_network)
    return constructor
