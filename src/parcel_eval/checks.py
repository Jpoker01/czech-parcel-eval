import json
import re

import jsonschema

RISKY_IMPACTS = {"could_block", "could_require_offer", "could_exclude_resale"}
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
    items = output.get("legal_flags", []) + output.get("resale_options", [])
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
        # The claim is text but the real value can be any type, so turn the real value into text.
        # Two ways, because the model writes strings without quotes but booleans and null as in JSON.
        # "silnice" -> silnice, False -> False, None -> None
        python_text = str(actual_value)
        # "silnice" -> "silnice" (with quotes), False -> false, None -> null
        json_text = json.dumps(actual_value, ensure_ascii=False)
        if claimed_value.strip() not in (python_text, json_text):
            errors.append(f"evidence: '{path}' is '{actual_value}', model claims '{claimed_value}'")
    return errors


def has_basic_land_register_data(parcel_input: dict) -> bool:
    """Return True when the input has enough land register data to evaluate the parcel."""
    land_register = parcel_input.get("land_register", {})
    if land_register.get("status") != "checked":
        return False
    land = land_register.get("land", {})
    if land.get("area_m2") is None or land.get("land_type") is None:
        return False
    # Owners are visible in the land register, but none were filled in
    if land_register.get("owners_visible") and not land_register.get("owners"):
        return False
    return True


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
    resale_options = output.get("resale_options", [])
    # Types of the legal flags the model raised, e.g. {"block", "offer"}
    flag_types = {flag["type"] for flag in output.get("legal_flags", [])}
    # Impacts of the data the model says is missing, e.g. {"could_block", "could_reduce_value"}
    impacts = {item["impact"] for item in output.get("missing_data", [])}

    # Rule 1: a block flag and BLOCKED always go together
    has_block_flag = "block" in flag_types
    is_blocked = decision == "BLOCKED"
    if has_block_flag != is_blocked:
        errors.append("rule 1: block flag and BLOCKED must go together")

    # Rule 2: an offer or consent flag rules out BUY_CANDIDATE
    has_offer_or_consent_flag = "offer" in flag_types or "consent" in flag_types
    if has_offer_or_consent_flag and decision == "BUY_CANDIDATE":
        errors.append("rule 2: offer or consent flag cannot end as BUY_CANDIDATE")

    # Rule 3: BUY_CANDIDATE needs someone to sell to and no risky missing data
    if decision == "BUY_CANDIDATE":
        # Is at least one resale option still open and has a buyer filled in (not null or empty)?
        has_open_option_with_buyer = False
        for resale_option in resale_options:
            if not resale_option["excluded"] and resale_option["buyer"]:
                has_open_option_with_buyer = True

        # Is any of the missing data risky, e.g. could_block?
        has_risky_missing_data = False
        for impact in impacts:
            if impact in RISKY_IMPACTS:
                has_risky_missing_data = True

        if not has_open_option_with_buyer or has_risky_missing_data:
            errors.append("rule 3: BUY_CANDIDATE needs a live named resale option and no risky missing data")

    # Rule 4: NOT_WORTH_IT means there is nobody left to sell to
    if decision == "NOT_WORTH_IT":
        # Is at least one resale option still open?
        has_open_option = False
        for resale_option in resale_options:
            if not resale_option["excluded"]:
                has_open_option = True

        # Does the model itself say missing data could still exclude a resale?
        exclusion_is_uncertain = "could_exclude_resale" in impacts

        if has_open_option or exclusion_is_uncertain:
            errors.append(
                "rule 4: NOT_WORTH_IT needs all resale options excluded and no could_exclude_resale"
            )

    # Rule 5: INSUFFICIENT_DATA exactly when the basic land register data is missing
    says_insufficient_data = decision == "INSUFFICIENT_DATA"
    data_is_missing = not has_basic_land_register_data(parcel_input)
    if says_insufficient_data != data_is_missing:
        errors.append("rule 5: INSUFFICIENT_DATA must match missing basic land register data")

    # Rule 6 (evidence matches the input) is checked in check_evidence

    # Rule 7: an excluded option has a reason, an open option does not
    for resale_option in resale_options:
        has_exclusion_reason = resale_option["exclusion_reason"] is not None
        if resale_option["excluded"] != has_exclusion_reason:
            errors.append(
                f"rule 7: resale option {resale_option['resale_type']} excluded and exclusion_reason disagree"
            )

    return errors


def compare_with_expected(output: dict, expected: dict) -> dict[str, bool]:
    """Compare the parts of the output that the eval scores.

    missing_data field paths are not scored, only their impact, because the
    model may name the same gap at a different path depth.

    Args:
        output: Model output.
        expected: Hand-written expected output.

    Returns:
        Match flags for decision, legal_flags, resale_options and risky missing data.
    """

    def flag_set(data: dict) -> set[tuple[str, str]]:
        """Reduce each legal flag to (type, code), e.g. ("block", "seal")."""
        flags = set()
        for flag in data.get("legal_flags", []):
            flags.add((flag["type"], flag["code"]))
        return flags

    def resale_option_set(data: dict) -> set[tuple[str, bool]]:
        """Reduce each resale option to (resale_type, excluded), e.g. ("co_owners", False)."""
        resale_options = set()
        for resale_option in data.get("resale_options", []):
            resale_options.add((resale_option["resale_type"], resale_option["excluded"]))
        return resale_options

    def risky_set(data: dict) -> set[str]:
        """Collect the impacts of missing data that are risky, e.g. {"could_block"}."""
        risky_impacts = set()
        for item in data.get("missing_data", []):
            if item["impact"] in RISKY_IMPACTS:
                risky_impacts.add(item["impact"])
        return risky_impacts

    # Each part matches only when it is exactly the same, there is no partial credit.
    # Sets ignore order, so the model may list flags and options in any order.
    decision_matches = output.get("decision") == expected.get("decision")
    flags_match = flag_set(output) == flag_set(expected)
    resale_options_match = resale_option_set(output) == resale_option_set(expected)
    risky_missing_data_matches = risky_set(output) == risky_set(expected)

    return {
        "decision": decision_matches,
        "legal_flags": flags_match,
        "resale_options": resale_options_match,
        "risky_missing_data": risky_missing_data_matches,
    }
