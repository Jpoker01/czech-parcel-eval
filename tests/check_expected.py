"""Check that the hand-written expected outputs are valid answers for their inputs.

Every expected output must pass the same checks a model output does in evaluate.py
(schema, consistency rules, evidence), and every input case must have an expected output.
Runs without the API, so it is safe for CI.

Usage:
    uv run python tests/check_expected.py
"""

import json
import logging
import sys

from parcel_eval.checks import check_consistency, check_evidence, validate_schema
from parcel_eval.paths import EXPECTED_DIR, INPUTS_DIR, SCHEMA_PATH

logger = logging.getLogger(__name__)


def find_errors() -> list[str]:
    """Return every problem found in the test cases, empty when all are fine."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    input_ids = {path.stem for path in INPUTS_DIR.glob("*.json")}
    expected_ids = {path.stem for path in EXPECTED_DIR.glob("*.json")}

    errors = [f"{case_id}: input has no expected output" for case_id in sorted(input_ids - expected_ids)]
    errors += [f"{case_id}: expected output has no input" for case_id in sorted(expected_ids - input_ids)]

    for case_id in sorted(input_ids & expected_ids):
        parcel_input = json.loads((INPUTS_DIR / f"{case_id}.json").read_text(encoding="utf-8"))
        expected = json.loads((EXPECTED_DIR / f"{case_id}.json").read_text(encoding="utf-8"))
        case_errors = (
            validate_schema(expected, schema)
            + check_consistency(expected, parcel_input)
            + check_evidence(expected, parcel_input)
        )
        errors += [f"{case_id}: {error}" for error in case_errors]
    return errors


def main() -> None:
    """Log every problem and exit with code 1 if there is any."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    errors = find_errors()
    for error in errors:
        logger.error(error)
    if errors:
        sys.exit(1)
    logger.info("All expected outputs are valid.")


if __name__ == "__main__":
    main()
