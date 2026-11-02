"""Run a prompt version on all (or selected) test cases and save raw outputs.

Usage:
    uv run --env-file .env python run.py --prompt v0
    uv run --env-file .env python run.py --prompt v0 --cases zalesni_lhota_1292-2 --repeats 3
"""

import argparse
import json
import logging
import os

import anthropic

from parcel_eval.llm import evaluate_parcel
from parcel_eval.paths import INPUTS_DIR, PROMPTS_DIR, RUNS_DIR, SCHEMA_PATH

# "or" also covers PARCEL_EVAL_MODEL left empty in .env
DEFAULT_MODEL = os.environ.get("PARCEL_EVAL_MODEL") or "claude-sonnet-5-5"
DEFAULT_REPEATS = 3

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True, help="Prompt version, e.g. v0")
    parser.add_argument("--cases", nargs="*", help="Case IDs, default all in input/examples")
    parser.add_argument("--repeats", type=int, default=DEFAULT_REPEATS)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    return parser.parse_args()


def main() -> None:
    """Evaluate each case N times and write outputs to runs/<prompt>/."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = parse_args()

    system_prompt = (PROMPTS_DIR / f"{args.prompt}.md").read_text(encoding="utf-8")
    output_schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    case_ids = args.cases or sorted(path.stem for path in INPUTS_DIR.glob("*.json"))

    run_dir = RUNS_DIR / args.prompt
    run_dir.mkdir(parents=True, exist_ok=True)
    client = anthropic.Anthropic()

    for case_id in case_ids:
        parcel_input = json.loads((INPUTS_DIR / f"{case_id}.json").read_text(encoding="utf-8"))
        for repeat in range(args.repeats):
            output = evaluate_parcel(
                client=client,
                model=args.model,
                system_prompt=system_prompt,
                output_schema=output_schema,
                parcel_input=parcel_input,
            )
            output_path = run_dir / f"{case_id}__{repeat}.json"
            output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
            logger.info(f"{case_id} #{repeat}: {output.get('decision')}")


if __name__ == "__main__":
    main()
