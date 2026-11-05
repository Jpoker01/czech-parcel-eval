from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROMPTS_DIR = PROJECT_ROOT / "prompts"
# Optional, versioned prompt add-ons, appended only when their run flag is on
ADDONS_DIR = PROMPTS_DIR / "addons"
INPUTS_DIR = PROJECT_ROOT / "input" / "examples"
EXPECTED_DIR = PROJECT_ROOT / "tests" / "expected"
CASES_DIR = PROJECT_ROOT / "tests" / "cases"
RUNS_DIR = PROJECT_ROOT / "runs"
SCHEMA_PATH = PROJECT_ROOT / "output" / "schema.json"
RUN_METADATA_FILE_NAME = "meta.json"
REPORT_FILE_NAME = "report.md"
# Model outputs in a run folder are named <case_id>__<repeat>.json.
# Build and parse the name only with the helpers below, so the rule lives in one place.
OUTPUT_FILE_SEPARATOR = "__"
OUTPUT_FILE_GLOB = f"*{OUTPUT_FILE_SEPARATOR}*.json"
HOLDOUT_PREFIX = "holdout_"


def output_file_name(case_id: str, repeat: int) -> str:
    """Return the file name of one model output, e.g. parcel_01__0.json."""
    return f"{case_id}{OUTPUT_FILE_SEPARATOR}{repeat}.json"


def parse_output_file_name(path: Path) -> tuple[str, int]:
    """Return (case_id, repeat) from a model output path made by output_file_name."""
    case_id, repeat = path.stem.rsplit(OUTPUT_FILE_SEPARATOR, 1)
    return case_id, int(repeat)
