import copy
import json
from datetime import date

import anthropic

UNSUPPORTED_SCHEMA_KEYS = ("$schema", "$id", "title", "$defs")


def build_output_format_schema(schema: dict) -> dict:
    """Inline $defs references and drop metadata keys for the structured output API.

    Args:
        schema: Output JSON schema loaded from output/schema.json.

    Returns:
        A copy of the schema without $schema, $id, title, $defs and $ref keys.
    """
    definitions = schema.get("$defs", {})

    def resolve(node: object) -> object:
        if isinstance(node, dict):
            if "$ref" in node:
                definition_name = node["$ref"].split("/")[-1]
                return resolve(copy.deepcopy(definitions[definition_name]))
            return {key: resolve(value) for key, value in node.items() if key not in UNSUPPORTED_SCHEMA_KEYS}
        if isinstance(node, list):
            return [resolve(item) for item in node]
        return node

    return resolve(schema)


def evaluate_parcel(
    client: anthropic.Anthropic,
    model: str,
    system_prompt: str,
    output_schema: dict,
    parcel_input: dict,
    today: date | None = None,
) -> dict:
    """Send one parcel to the model and return its structured evaluation.

    The output schema is passed as a structured output format, so the API only
    returns JSON that matches it.

    Args:
        client: Anthropic API client.
        model: Model ID, e.g. claude-sonnet-5-5.
        system_prompt: Prompt text from prompts/<version>.md.
        output_schema: Output JSON schema.
        parcel_input: Filled input for one parcel.
        today: Date used for time-based rules (6-month inheritance window).

    Returns:
        The evaluation dict produced by the model.

    Raises:
        ValueError: If the response contains no text block.
    """
    today = today or date.today()
    # Date goes into the message, not the prompt, so the prompt stays versioned and stable
    user_message = (
        f"Dnešní datum: {today.isoformat()}\n\n"
        f"Data o parcele:\n```json\n{json.dumps(parcel_input, ensure_ascii=False, indent=2)}\n```"
    )

    response = client.messages.create(
        model=model,
        max_tokens=4_000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
        output_config={
            "format": {
                "type": "json_schema",
                "schema": build_output_format_schema(output_schema),
            },
        },
    )

    for block in response.content:
        if block.type == "text":
            return json.loads(block.text)
    raise ValueError(f"Model returned no text block, stop_reason={response.stop_reason}")
