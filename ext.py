import os
import importlib.util
from functools import lru_cache
from typing import Callable

from setting import ext_path

@lru_cache(maxsize=None)
def extMethod(ns:str, method:str) -> None | Callable:
    ext_file = os.path.join(ext_path, ns + '.py')

    if os.path.exists(ext_file):
        spec = importlib.util.spec_from_file_location(ns, ext_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, method):
            return getattr(module, method)
