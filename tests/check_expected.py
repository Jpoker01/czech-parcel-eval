"""Check that the hand-written expected outputs are valid answers for their inputs.

Every expected output must pass the same checks a model output does in evaluate.py
(schema, consistency rules, evidence), every real input must have an expected output,
and every synthetic case must build from an existing base. Runs without the API, so it is safe for CI.

Usage:
    uv run python tests/check_expected.py
"""

import logging
import sys

from parcel_eval.cases import (
    list_case_ids,
    load_expected,
    load_input,
    load_json,
    real_case_ids,
    synthetic_case_ids,
)
from parcel_eval.checks import check_output
from parcel_eval.paths import EXPECTED_DIR, SCHEMA_PATH

logger = logging.getLogger(__name__)


def find_errors() -> list[str]:
    """Return every problem found in the test cases, empty when all are fine."""
    schema = load_json(SCHEMA_PATH)
    real_ids = real_case_ids()
    expected_ids = {path.stem for path in EXPECTED_DIR.glob("*.json")}
    synthetic_ids = synthetic_case_ids()

    errors = [f"{case_id}: input has no expected output" for case_id in sorted(real_ids - expected_ids)]
    errors += [f"{case_id}: expected output has no input" for case_id in sorted(expected_ids - real_ids)]
    errors += [f"{case_id}: both a real and a synthetic case" for case_id in sorted(real_ids & synthetic_ids)]

    for case_id in list_case_ids():
        try:
            parcel_input = load_input(case_id)
            expected = load_expected(case_id)
        # A synthetic case whose base or changed path does not exist
        except (FileNotFoundError, KeyError, IndexError, TypeError) as error:
            errors.append(f"{case_id}: cannot be built ({error!r})")
            continue
        errors += [f"{case_id}: {error}" for error in check_output(expected, parcel_input, schema)]
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
