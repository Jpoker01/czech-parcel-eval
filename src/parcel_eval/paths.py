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
HOLDOUT_PREFIX = "holdout_"
