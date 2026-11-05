"""Score saved outputs of one prompt version against the expected outputs.

Usage:
    uv run python evaluate.py --prompt v0
    uv run python evaluate.py --prompt v1_findings_v2   # run made with run.py --other-findings v2
"""

import argparse
import logging
from collections import Counter, defaultdict

from parcel_eval.cases import load_expected, load_input, load_json
from parcel_eval.checks import SCORED_PARTS, check_output, compare_with_expected, validate_schema
from parcel_eval.findings import OTHER_FINDINGS_FIELD, add_other_findings
from parcel_eval.metrics import build_confusion_matrix, compute_decision_scores, format_decision_metrics
from parcel_eval.paths import (
    OUTPUT_FILE_GLOB,
    REPORT_FILE_NAME,
    RUN_METADATA_FILE_NAME,
    RUNS_DIR,
    SCHEMA_PATH,
    parse_output_file_name,
)

logger = logging.getLogger(__name__)


def load_metadata(prompt_version: str) -> dict | None:
    """Read runs/<prompt>/meta.json, or None when the run has none."""
    metadata_path = RUNS_DIR / prompt_version / RUN_METADATA_FILE_NAME
    return load_json(metadata_path) if metadata_path.exists() else None


def format_metadata(metadata: dict | None) -> list[str]:
    """Describe how the run was made.

    Args:
        metadata: Content of runs/<prompt>/meta.json, or None.

    Returns:
        Markdown bullet lines for the top of the report.
    """
    if metadata is None:
        return ["- Metadata: not recorded (the run has no meta.json)"]

    # Runs made before the flag existed have no key and ran without other_findings
    addon_version = metadata.get("other_findings")
    other_findings = f"add-on {addon_version}" if addon_version else "off"
    return [
        f"- Model: {metadata['model']}",
        f"- Prompt: {metadata['prompt_version']} (sha256 {metadata['prompt_sha256']})",
        f"- Other findings: {other_findings}",
        f"- Run at: {metadata['run_at']}",
        f"- Cases: {len(metadata['cases'])}, repeats per case: {metadata['repeats']}",
    ]


def format_other_findings(
    findings_by_case: dict[str, list[str]],
    decision_misses: Counter,
    outputs_by_case: dict[str, list],
) -> list[str]:
    """List every other_finding by case, marking cases where the decision missed the expected one.

    A finding on a missed case may mean the taxonomy lacks a code, not that the model failed.

    Args:
        findings_by_case: Formatted finding lines per case.
        decision_misses: Runs per case where the decision differed from the expected one.
        outputs_by_case: Outputs per case, for the number of runs.

    Returns:
        Markdown lines of the "Other findings" section.
    """
    lines = [
        "## Other findings",
        "",
        "Not scored. A finding that repeats across cases is a candidate for a new code or resale type. "
        "On a case where the decision missed, check whether the finding explains it before calling it "
        "a model error.",
        "",
    ]
    if not findings_by_case:
        return [*lines, "None."]

    for case_id, finding_lines in findings_by_case.items():
        title = f"### {case_id}"
        if decision_misses[case_id]:
            title += f" (decision missed in {decision_misses[case_id]}/{len(outputs_by_case[case_id])} runs)"
        lines += [title, "", *finding_lines, ""]
    return lines


def build_report(prompt_version: str) -> str:
    """Score every saved run of a prompt version and return a markdown report.

    Args:
        prompt_version: Folder name under runs/, e.g. v0.

    Returns:
        Markdown with a per-case table, totals, a decision confusion matrix and all errors found.
    """
    metadata = load_metadata(prompt_version)
    other_findings_enabled = bool(metadata and metadata.get("other_findings"))
    schema = load_json(SCHEMA_PATH)
    # Validate against the same schema the model got, so the add-on field is not reported as extra
    if other_findings_enabled:
        schema = add_other_findings(schema)
    run_dir = RUNS_DIR / prompt_version
    outputs_by_case = defaultdict(list)
    for output_path in sorted(run_dir.glob(OUTPUT_FILE_GLOB)):
        case_id, repeat = parse_output_file_name(output_path)
        outputs_by_case[case_id].append((repeat, load_json(output_path)))

    header = "| Case | Expected | Got | " + " | ".join(SCORED_PARTS) + " | Consistency | Errors |"
    rows = [header, "|" + "---|" * (len(SCORED_PARTS) + 5)]
    error_lines = []
    decision_pairs = []
    totals = Counter()

    unanimous_cases = 0
    modal_count_sum = 0
    findings_by_case = defaultdict(list)
    decision_misses = Counter()
    for case_id, outputs in outputs_by_case.items():
        parcel_input = load_input(case_id)
        expected = load_expected(case_id)
        decisions = Counter(output.get("decision") for _, output in outputs)
        modal_decision, modal_count = decisions.most_common(1)[0]
        if modal_count == len(outputs):
            unanimous_cases += 1
        modal_count_sum += modal_count

        case_scores = Counter()
        case_error_count = 0
        for repeat, output in outputs:
            decision_pairs.append((expected["decision"], output.get("decision")))
            errors = check_output(output, parcel_input, schema)
            case_error_count += len(errors)
            error_lines += [f"- `{case_id}` #{repeat}: {error}" for error in errors]
            # Scoring and the findings read required fields, so an output with a broken shape
            # counts as a miss on every part and its findings are skipped
            if validate_schema(output, schema):
                continue
            for finding in output.get(OTHER_FINDINGS_FIELD, []):
                findings_by_case[case_id].append(f"- #{repeat} {finding['type']}: {finding['description']}")
            for part, matched in compare_with_expected(output, expected).items():
                case_scores[part] += matched

        totals.update(case_scores)
        decision_misses[case_id] = len(outputs) - case_scores["decision"]
        scores = " | ".join(f"{case_scores[part]}/{len(outputs)}" for part in SCORED_PARTS)
        rows.append(
            f"| {case_id} | {expected['decision']} | {modal_decision} | {scores} "
            f"| {modal_count}/{len(outputs)} | {case_error_count} |"
        )

    # Across the whole run: cases that agreed on every repeat (strict) and the average modal rate (lenient)
    total_runs = sum(len(outputs) for outputs in outputs_by_case.values())
    total_scores = " | ".join(f"{totals[part]}/{total_runs}" for part in SCORED_PARTS)
    case_count = len(outputs_by_case)
    total_consistency = "-"
    if case_count:
        modal_rate = modal_count_sum / total_runs
        total_consistency = f"{unanimous_cases}/{case_count} unanimous, avg {modal_rate:.0%}"
    rows.append(f"| **total** | | | {total_scores} | {total_consistency} | {len(error_lines)} |")

    matrix = build_confusion_matrix(decision_pairs)
    report = [
        f"# Report {prompt_version}",
        "",
        *format_metadata(metadata),
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
    if other_findings_enabled:
        report += ["", *format_other_findings(findings_by_case, decision_misses, outputs_by_case)]
    return "\n".join(report).rstrip() + "\n"


def main() -> None:
    """Write runs/<prompt>/report.md and print it."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    args = parser.parse_args()

    report = build_report(args.prompt)
    (RUNS_DIR / args.prompt / REPORT_FILE_NAME).write_text(report, encoding="utf-8")
    logger.info(report)


if __name__ == "__main__":
    main()
