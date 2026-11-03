from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROMPTS_DIR = PROJECT_ROOT / "prompts"
INPUTS_DIR = PROJECT_ROOT / "input" / "examples"
EXPECTED_DIR = PROJECT_ROOT / "tests" / "expected"
RUNS_DIR = PROJECT_ROOT / "runs"
SCHEMA_PATH = PROJECT_ROOT / "output" / "schema.json"
RUN_METADATA_FILE_NAME = "meta.json"
