"""Optional other_findings field: risks and opportunities that no enum covers.

The field is switched on per run (run.py --other-findings VERSION). It is appended to the
output schema and the prompt only for that run, so the base prompt versions and the
expected outputs stay unchanged. The add-on text is versioned like the prompts
(prompts/addons/other_findings_<version>.md), so every run can be reproduced.
Findings are never scored: they are listed in the report for a person to read, and
the ones that repeat become new codes.
"""

import copy

from parcel_eval.paths import ADDONS_DIR

OTHER_FINDINGS_FIELD = "other_findings"

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


def add_other_findings_prompt(system_prompt: str, addon_version: str) -> str:
    """Append one version of the other_findings instructions to a prompt version.

    Args:
        system_prompt: Text of prompts/<version>.md.
        addon_version: Add-on version, e.g. v2 for prompts/addons/other_findings_v2.md.

    Returns:
        The prompt followed by the add-on text.

    Raises:
        FileNotFoundError: If the add-on version does not exist.
    """
    addon = (ADDONS_DIR / f"other_findings_{addon_version}.md").read_text(encoding="utf-8")
    return system_prompt.rstrip() + "\n" + addon


def run_dir_name(prompt_version: str, addon_version: str | None) -> str:
    """Return the folder name under runs/, e.g. v1, or v1_findings_v2 with the add-on."""
    if addon_version is None:
        return prompt_version
    return f"{prompt_version}_findings_{addon_version}"
