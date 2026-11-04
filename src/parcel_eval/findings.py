"""Optional other_findings field: risks and opportunities that no enum covers.

The field is switched on per run (run.py --other-findings). It is appended to the
output schema and the prompt only for that run, so the base prompt versions and
the expected outputs stay unchanged. Findings are never scored: they are listed in
the report for a person to read, and the ones that repeat become new codes.
"""

import copy

from parcel_eval.paths import OTHER_FINDINGS_PROMPT_PATH

OTHER_FINDINGS_FIELD = "other_findings"
# Suffix of the run folder, so runs/v1 and runs/v1-findings never overwrite each other
FINDINGS_RUN_SUFFIX = "-findings"

OTHER_FINDINGS_PROPERTY = {
    "type": "array",
    "description": (
        "Risks or opportunities that no code, resale_type or missing_data covers. "
        "Never changes the other fields and is never scored. Empty when there is nothing to add."
    ),
    "items": {
        "type": "object",
        "additionalProperties": False,
        "required": ["type", "description"],
        "properties": {
            "type": {"type": "string", "enum": ["risk", "opportunity"]},
            "description": {
                "type": "string",
                "description": "One sentence in Czech naming the fact and the input field it comes from.",
            },
        },
    },
}


def add_other_findings(output_schema: dict) -> dict:
    """Return a copy of the output schema with the required other_findings field.

    Args:
        output_schema: Base output schema from output/schema.json.

    Returns:
        New schema; the base schema is not modified.
    """
    schema = copy.deepcopy(output_schema)
    schema["properties"][OTHER_FINDINGS_FIELD] = OTHER_FINDINGS_PROPERTY
    schema["required"].append(OTHER_FINDINGS_FIELD)
    return schema


def add_other_findings_prompt(system_prompt: str) -> str:
    """Append the other_findings instructions to a prompt version.

    Args:
        system_prompt: Text of prompts/<version>.md.

    Returns:
        The prompt followed by prompts/addons/other_findings.md.
    """
    addon = OTHER_FINDINGS_PROMPT_PATH.read_text(encoding="utf-8")
    return system_prompt.rstrip() + "\n" + addon


def run_dir_name(prompt_version: str, other_findings: bool) -> str:
    """Return the folder name under runs/ for a prompt version, e.g. v1 or v1-findings."""
    return prompt_version + FINDINGS_RUN_SUFFIX if other_findings else prompt_version
