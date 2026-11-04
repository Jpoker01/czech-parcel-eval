"""Run a prompt version on all (or selected) test cases and save raw outputs.

Usage:
    uv run python run.py --prompt v0
    uv run python run.py --prompt v0 --cases zalesni_lhota_1292-2 --repeats 3
    uv run python run.py --prompt v0 --force   # replace an existing run of the same version
    uv run python run.py --prompt v0 --include-holdout   # final run, holdout parcels included
    uv run python run.py --prompt v1 --other-findings    # adds other_findings, saved to runs/v1-findings/
"""

import argparse
import hashlib
import json
import logging
import os
from datetime import date, datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from parcel_eval.cases import list_case_ids, load_input
from parcel_eval.findings import add_other_findings, add_other_findings_prompt, run_dir_name
from parcel_eval.llm import evaluate_parcel
from parcel_eval.paths import (
    HOLDOUT_PREFIX,
    PROMPTS_DIR,
    RUN_METADATA_FILE_NAME,
    RUNS_DIR,
    SCHEMA_PATH,
)

load_dotenv()

DEFAULT_MODEL = os.environ.get("PARCEL_EVAL_MODEL") or "claude-sonnet-5-5"
DEFAULT_REPEATS = 3

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True, help="Prompt version, e.g. v0")
    parser.add_argument("--cases", nargs="*", help="Case IDs, default all real and synthetic cases")
    parser.add_argument("--repeats", type=int, default=DEFAULT_REPEATS)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--force", action="store_true", help="Replace an existing run of this prompt version")
    parser.add_argument(
        "--include-holdout",
        action="store_true",
        help=f"Also run the {HOLDOUT_PREFIX}* cases, which are kept out of prompt iterations",
    )
    parser.add_argument(
        "--other-findings",
        action="store_true",
        help="Ask the model for other_findings (risks and opportunities outside the enums, never scored)",
    )
    return parser.parse_args()


def select_case_ids(args: argparse.Namespace) -> list[str]:
    """Return the cases to run: the explicit --cases list, or every case minus the holdout set.

    Args:
        args: Parsed command line arguments.

    Returns:
        Case IDs in the order they run.
    """
    if args.cases:
        return args.cases
    case_ids = list_case_ids()
    if not args.include_holdout:
        case_ids = [case_id for case_id in case_ids if not case_id.startswith(HOLDOUT_PREFIX)]
    return case_ids


def reference_date(parcel_input: dict) -> date | None:
    """Return the date the land register was checked, so time-based rules stay reproducible.

    Args:
        parcel_input: Filled input for one parcel.

    Returns:
        meta.checked_at as a date, or None when the case has no date (the model then gets today).
    """
    checked_at = parcel_input.get("meta", {}).get("checked_at")
    return date.fromisoformat(checked_at) if checked_at else None


def build_run_metadata(args: argparse.Namespace, case_ids: list[str], system_prompt: str) -> dict:
    """Describe how a run was made, so a saved result can be traced back.

    Args:
        args: Parsed command line arguments.
        case_ids: Cases included in the run.
        system_prompt: Text of the prompt used, including any add-on.

    Returns:
        Dict that is saved as meta.json next to the outputs.
    """
    return {
        "prompt_version": args.prompt,
        # Hash of the text, so a prompt edited after the run can be recognised
        "prompt_sha256": hashlib.sha256(system_prompt.encode("utf-8")).hexdigest()[:12],
        "model": args.model,
        "repeats": args.repeats,
        # evaluate.py reads this to validate against the same schema the model got
        "other_findings": args.other_findings,
        "cases": case_ids,
        "run_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }


def prepare_run_dir(run_dir: Path, force: bool) -> None:
    """Create the run folder without mixing results of two different runs.

    Args:
        run_dir: Folder runs/<prompt>/ or runs/<prompt>-findings/.
        force: Delete the previous results of this prompt version instead of refusing.

    Raises:
        FileExistsError: If the folder already has results and force is False.
    """
    previous_files = [
        *run_dir.glob("*__*.json"),
        run_dir / RUN_METADATA_FILE_NAME,
        run_dir / "report.md",
    ]
    previous_files = [path for path in previous_files if path.exists()]
    if previous_files and not force:
        raise FileExistsError(
            f"{run_dir} already has results. Use a new --prompt version or pass --force to replace them."
        )
    for path in previous_files:
        path.unlink()
    run_dir.mkdir(parents=True, exist_ok=True)


def main() -> None:
    """Evaluate each case N times and write outputs and meta.json to the run folder."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = parse_args()

    system_prompt = (PROMPTS_DIR / f"{args.prompt}.md").read_text(encoding="utf-8")
    output_schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    if args.other_findings:
        system_prompt = add_other_findings_prompt(system_prompt)
        output_schema = add_other_findings(output_schema)
    case_ids = select_case_ids(args)

    run_dir = RUNS_DIR / run_dir_name(args.prompt, args.other_findings)
    try:
        prepare_run_dir(run_dir, args.force)
    except FileExistsError as error:
        raise SystemExit(str(error)) from error

    metadata = build_run_metadata(args, case_ids, system_prompt)
    (run_dir / RUN_METADATA_FILE_NAME).write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    client = anthropic.Anthropic()

    for case_id in case_ids:
        parcel_input = load_input(case_id)
        for repeat in range(args.repeats):
            output = evaluate_parcel(
                client=client,
                model=args.model,
                system_prompt=system_prompt,
                output_schema=output_schema,
                parcel_input=parcel_input,
                today=reference_date(parcel_input),
            )
            output_path = run_dir / f"{case_id}__{repeat}.json"
            output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            logger.info(f"{case_id} #{repeat}: {output.get('decision')}")


if __name__ == "__main__":
    main()
