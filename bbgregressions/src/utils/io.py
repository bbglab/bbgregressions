"""
Small I/O helpers for the bbgregressions package.
"""
from typing import Any
import os
import gzip
import yaml


def read_yaml(path: str) -> Any:
    """
    Read a YAML file (supports .gz) and return the parsed object.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    opener = gzip.open if path.endswith((".gz", ".gzip")) else open
    with opener(path, mode="rt") as fh:
        return yaml.safe_load(fh)