"""Load test cases.

Real parcels live in input/examples/<case>.json with the expected output in tests/expected/<case>.json.
A synthetic case is one file in tests/cases/<case>.json that names a base case, lists the input
fields it changes and holds its expected output, so every variant can be read on its own.
"""

import copy
import json
from pathlib import Path

from parcel_eval.checks import PATH_PART_PATTERN
from parcel_eval.paths import CASES_DIR, EXPECTED_DIR, INPUTS_DIR


def load_json(path: Path) -> dict:
    """Read a UTF-8 JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def list_case_ids() -> list[str]:
    """Return the IDs of all real and synthetic cases, sorted."""
    real_ids = {path.stem for path in INPUTS_DIR.glob("*.json")}
    synthetic_ids = {path.stem for path in CASES_DIR.glob("*.json")}
    return sorted(real_ids | synthetic_ids)


def set_path(data: dict, path: str, value: object) -> None:
    """Write a value into nested input by a path like land_register.owners[0].name.

    Args:
        data: Parcel input, changed in place.
        path: Dot path with [index] for list items.
        value: New value of the field.
    """
    parts = PATH_PART_PATTERN.findall(path)
    target: object = data
    for part in parts[:-1]:
        target = target[int(part)] if part.isdigit() else target[part]
    last_part = parts[-1]
    target[int(last_part) if last_part.isdigit() else last_part] = value


def load_input(case_id: str) -> dict:
    """Return the parcel input of a case.

    Args:
        case_id: Real or synthetic case ID.

    Returns:
        The real input, or the base input with the synthetic case's changes applied.
        The base can itself be a synthetic case.
    """
    real_path = INPUTS_DIR / f"{case_id}.json"
    if real_path.exists():
        return load_json(real_path)

    case = load_json(CASES_DIR / f"{case_id}.json")
    parcel_input = load_input(case["base"])
    for path, value in case["changes"].items():
        set_path(parcel_input, path, copy.deepcopy(value))
    parcel_input["meta"]["case_id"] = case_id
    return parcel_input


def load_expected(case_id: str) -> dict:
    """Return the hand-written expected output of a real or synthetic case."""
    synthetic_path = CASES_DIR / f"{case_id}.json"
    if synthetic_path.exists():
        return load_json(synthetic_path)["expected"]
    return load_json(EXPECTED_DIR / f"{case_id}.json")
