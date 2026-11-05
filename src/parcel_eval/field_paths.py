"""Read and write nested input fields by a path like land_register.owners[0].name.

Shared by the case loader (cases.py) and the evidence check (checks.py).
"""

import re

PATH_PART_PATTERN = re.compile(r"[^.\[\]]+")


def split_path(path: str) -> list[str | int]:
    """Split a path like land_register.owners[0].name into keys: ["land_register", "owners", 0, "name"].

    Only ASCII digits become list indexes; str.isdigit() alone also accepts e.g. "²", which int() rejects.
    """
    return [
        int(part) if part.isascii() and part.isdigit() else part for part in PATH_PART_PATTERN.findall(path)
    ]


def resolve_path(data: dict, path: str) -> object:
    """Read a value from nested input by a path like land_register.owners[0].name.

    Args:
        data: Parcel input.
        path: Dot path with [index] for list items.

    Returns:
        The value at the path.

    Raises:
        KeyError, IndexError, TypeError: If the path does not exist.
    """
    value: object = data
    for key in split_path(path):
        value = value[key]
    return value


def set_path(data: dict, path: str, value: object) -> None:
    """Write a value into nested input by a path like land_register.owners[0].name.

    Args:
        data: Parcel input, changed in place.
        path: Dot path with [index] for list items.
        value: New value of the field.

    Raises:
        KeyError, IndexError, TypeError: If the path is empty or its parent does not exist.
    """
    keys = split_path(path)
    if not keys:
        raise KeyError(f"empty path '{path}'")
    *parent_keys, last_key = keys
    target: object = data
    for key in parent_keys:
        target = target[key]
    target[last_key] = value
