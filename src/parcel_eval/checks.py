import json
import re

import jsonschema

RISKY_IMPACTS = {"could_block", "could_require_offer", "could_kill_exit"}
PATH_PART_PATTERN = re.compile(r"[^.\[\]]+")


def validate_schema(output: dict, schema: dict) -> list[str]:
    """Return schema validation errors for one model output.

    Args:
        output: Model output.
        schema: Output JSON schema.

    Returns:
        Error messages, empty when the output is valid.
    """
    validator = jsonschema.Draft202012Validator(schema)
    return [f"schema: {error.message}" for error in validator.iter_errors(output)]


def resolve_path(data: dict, path: str) -> object:
    """Read a value from nested input by a path like cadastre.owners[0].name.

    Args:
        data: Parcel input.
        path: Dot path with [index] for list items.

    Returns:
        The value at the path.

    Raises:
        KeyError, IndexError, TypeError: If the path does not exist.
    """
    value: object = data
    for part in PATH_PART_PATTERN.findall(path):
        value = value[int(part)] if part.isdigit() else value[part]
    return value


def check_evidence(output: dict, parcel_input: dict) -> list[str]:
    """Check that every evidence string points to a real input field and value.

    Args:
        output: Model output.
        parcel_input: Parcel input the model received.

    Returns:
        Error messages for evidence that does not match the input.
    """
    errors = []
    items = output.get("legal_flags", []) + output.get("exits", [])
    for item in items:
        evidence = item.get("evidence", "")
        if " = " not in evidence:
            errors.append(f"evidence: bad format '{evidence}'")
            continue
        path, claimed_value = evidence.split(" = ", 1)
        try:
            actual_value = resolve_path(parcel_input, path.strip())
        except (KeyError, IndexError, TypeError):
            errors.append(f"evidence: path does not exist '{path}'")
            continue
        # Model may write a bool as true or True, so accept both str() and JSON forms
        accepted_forms = {str(actual_value), json.dumps(actual_value, ensure_ascii=False)}
        if claimed_value.strip() not in accepted_forms:
            errors.append(f"evidence: '{path}' is '{actual_value}', model claims '{claimed_value}'")
    return errors


def has_basic_cadastre_data(parcel_input: dict) -> bool:
    """Return True when the input has enough cadastre data to evaluate the parcel."""
    cadastre = parcel_input.get("cadastre", {})
    if cadastre.get("status") != "checked":
        return False
    land = cadastre.get("land", {})
    if land.get("area_m2") is None or land.get("land_type") is None:
        return False
    return not (cadastre.get("owners_visible") and not cadastre.get("owners"))


def check_consistency(output: dict, parcel_input: dict) -> list[str]:
    """Check the decision against the rules in docs/output_schema.md.

    Args:
        output: Model output.
        parcel_input: Parcel input the model received.

    Returns:
        Error messages, one per broken rule.
    """
    errors = []
    decision = output.get("decision")
    flag_types = {flag["type"] for flag in output.get("legal_flags", [])}
    exits = output.get("exits", [])
    impacts = {item["impact"] for item in output.get("missing_data", [])}

    if ("block" in flag_types) != (decision == "BLOCKED"):
        errors.append("rule 1: block flag and BLOCKED must go together")

    if flag_types & {"offer", "consent"} and decision == "BUY_CANDIDATE":
        errors.append("rule 2: offer or consent flag cannot end as BUY_CANDIDATE")

    if decision == "BUY_CANDIDATE":
        has_live_named_exit = any(not exit_["killed"] and exit_["buyer"] for exit_ in exits)
        if not has_live_named_exit or impacts & {"could_block", "could_kill_exit"}:
            errors.append("rule 3: BUY_CANDIDATE needs a live named exit and no blocking missing data")

    if decision == "NOT_WORTH_IT":
        if any(not exit_["killed"] for exit_ in exits) or "could_kill_exit" in impacts:
            errors.append("rule 4: NOT_WORTH_IT needs all exits killed and no could_kill_exit")

    if (decision == "INSUFFICIENT_DATA") == has_basic_cadastre_data(parcel_input):
        errors.append("rule 5: INSUFFICIENT_DATA must match missing basic cadastre data")

    for exit_ in exits:
        if exit_["killed"] != (exit_["kill_reason"] is not None):
            errors.append(f"rule 7: exit {exit_['exit_type']} killed and kill_reason disagree")

    return errors


def compare_with_expected(output: dict, expected: dict) -> dict[str, bool]:
    """Compare the parts of the output that the eval scores.

    missing_data field paths are not scored, only their impact, because the
    model may name the same gap at a different path depth.

    Args:
        output: Model output.
        expected: Hand-written expected output.

    Returns:
        Match flags for decision, legal_flags, exits and risky missing data.
    """

    def flag_set(data: dict) -> set[tuple[str, str]]:
        return {(flag["type"], flag["code"]) for flag in data.get("legal_flags", [])}

    def exit_set(data: dict) -> set[tuple[str, bool]]:
        return {(exit_["exit_type"], exit_["killed"]) for exit_ in data.get("exits", [])}

    def risky_set(data: dict) -> set[str]:
        return {item["impact"] for item in data.get("missing_data", [])} & RISKY_IMPACTS

    return {
        "decision": output.get("decision") == expected.get("decision"),
        "legal_flags": flag_set(output) == flag_set(expected),
        "exits": exit_set(output) == exit_set(expected),
        "risky_missing_data": risky_set(output) == risky_set(expected),
    }
