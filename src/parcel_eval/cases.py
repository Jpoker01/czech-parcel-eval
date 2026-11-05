"""Load test cases.

Real parcels live in input/examples/<case>.json with the expected output in tests/expected/<case>.json.
A synthetic case is one file in tests/cases/<case>.json that names a base case, lists the input
fields it changes and holds its expected output, so every variant can be read on its own.
"""

import copy
import json
from pathlib import Path

from parcel_eval.field_paths import set_path
from parcel_eval.paths import CASES_DIR, EXPECTED_DIR, INPUTS_DIR


def load_json(path: Path) -> dict:
    """Read a UTF-8 JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    """Write a UTF-8 JSON file, indented and with Czech characters kept readable."""
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def real_case_ids() -> set[str]:
    """Return the IDs of the real cases in input/examples/."""
    return {path.stem for path in INPUTS_DIR.glob("*.json")}


def synthetic_case_ids() -> set[str]:
    """Return the IDs of the synthetic cases in tests/cases/."""
    return {path.stem for path in CASES_DIR.glob("*.json")}


def expected_case_ids() -> set[str]:
    """Return the IDs of the hand-written expected outputs in tests/expected/."""
    return {path.stem for path in EXPECTED_DIR.glob("*.json")}


def list_case_ids() -> list[str]:
    """Return the IDs of all real and synthetic cases, sorted."""
    return sorted(real_case_ids() | synthetic_case_ids())


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
