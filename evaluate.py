"""Score saved outputs of one prompt version against the expected outputs.

Usage:
    uv run python evaluate.py --prompt v0
"""

import argparse
import json
import logging
from collections import Counter, defaultdict
from pathlib import Path

from parcel_eval.checks import check_consistency, check_evidence, compare_with_expected, validate_schema
from parcel_eval.metrics import build_confusion_matrix, compute_decision_scores, format_decision_metrics
from parcel_eval.paths import EXPECTED_DIR, INPUTS_DIR, RUN_METADATA_FILE_NAME, RUNS_DIR, SCHEMA_PATH

SCORED_PARTS = ["decision", "legal_flags", "resale_options", "risky_missing_data"]

logger = logging.getLogger(__name__)


def load_json(path: Path) -> dict:
    """Read a UTF-8 JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def format_metadata(prompt_version: str) -> list[str]:
    """Describe how the run was made, from runs/<prompt>/meta.json.

    Args:
        prompt_version: Folder name under runs/, e.g. v0.

    Returns:
        Markdown bullet lines for the top of the report.
    """
    metadata_path = RUNS_DIR / prompt_version / RUN_METADATA_FILE_NAME
    if not metadata_path.exists():
        return ["- Metadata: not recorded (the run has no meta.json)"]

    metadata = load_json(metadata_path)
    return [
        f"- Model: {metadata['model']}",
        f"- Prompt: {metadata['prompt_version']} (sha256 {metadata['prompt_sha256']})",
        f"- Run at: {metadata['run_at']}",
        f"- Cases: {len(metadata['cases'])}, repeats per case: {metadata['repeats']}",
    ]


def build_report(prompt_version: str) -> str:
    """Score every saved run of a prompt version and return a markdown report.

    Args:
        prompt_version: Folder name under runs/, e.g. v0.

    Returns:
        Markdown with a per-case table, totals, a decision confusion matrix and all errors found.
    """
    schema = load_json(SCHEMA_PATH)
    run_dir = RUNS_DIR / prompt_version
    outputs_by_case = defaultdict(list)
    for output_path in sorted(run_dir.glob("*__*.json")):
        case_id, repeat = output_path.stem.rsplit("__", 1)
        outputs_by_case[case_id].append((int(repeat), load_json(output_path)))

    header = "| Case | Expected | Got | " + " | ".join(SCORED_PARTS) + " | Consistency | Errors |"
    rows = [header, "|" + "---|" * (len(SCORED_PARTS) + 5)]
    error_lines = []
    decision_pairs = []
    totals = Counter()
    total_runs = 0

    for case_id, outputs in outputs_by_case.items():
        parcel_input = load_json(INPUTS_DIR / f"{case_id}.json")
        expected = load_json(EXPECTED_DIR / f"{case_id}.json")
        decisions = Counter(output.get("decision") for _, output in outputs)
        modal_decision, modal_count = decisions.most_common(1)[0]

        case_scores = Counter()
        case_error_count = 0
        for repeat, output in outputs:
            decision_pairs.append((expected["decision"], output.get("decision")))
            errors = (
                validate_schema(output, schema)
                + check_consistency(output, parcel_input)
                + check_evidence(output, parcel_input)
            )
            case_error_count += len(errors)
            error_lines += [f"- `{case_id}` #{repeat}: {error}" for error in errors]
            for part, matched in compare_with_expected(output, expected).items():
                case_scores[part] += matched

        totals.update(case_scores)
        total_runs += len(outputs)
        scores = " | ".join(f"{case_scores[part]}/{len(outputs)}" for part in SCORED_PARTS)
        rows.append(
            f"| {case_id} | {expected['decision']} | {modal_decision} | {scores} "
            f"| {modal_count}/{len(outputs)} | {case_error_count} |"
        )

    total_scores = " | ".join(f"{totals[part]}/{total_runs}" for part in SCORED_PARTS)
    rows.append(f"| **total** | | | {total_scores} | | {len(error_lines)} |")

    matrix = build_confusion_matrix(decision_pairs)
    report = [
        f"# Report {prompt_version}",
        "",
        *format_metadata(prompt_version),
        "",
        *rows,
        "",
        "## Decision confusion matrix",
        "",
        "Rows are the expected decision, columns the returned one, counted over every run.",
        "",
        *format_decision_metrics(matrix, compute_decision_scores(matrix)),
        "",
        "## Errors",
        "",
        *(error_lines or ["None."]),
    ]
    return "\n".join(report) + "\n"


def main() -> None:
    """Write runs/<prompt>/report.md and print it."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    args = parser.parse_args()

    report = build_report(args.prompt)
    (RUNS_DIR / args.prompt / "report.md").write_text(report, encoding="utf-8")
    logger.info(report)


if __name__ == "__main__":
    main()
