import copy
import json
from datetime import date

import anthropic

TOOL_NAME = "submit_evaluation"


def build_tool_schema(schema: dict) -> dict:
    """Inline $defs references so the schema works as a tool input_schema.

    Args:
        schema: Output JSON schema loaded from output/schema.json.

    Returns:
        A copy of the schema without $schema, title, $defs and $ref keys.
    """
    definitions = schema.get("$defs", {})

    def resolve(node: object) -> object:
        if isinstance(node, dict):
            if "$ref" in node:
                definition_name = node["$ref"].split("/")[-1]
                return resolve(copy.deepcopy(definitions[definition_name]))
            return {
                key: resolve(value)
                for key, value in node.items()
                if key not in ("$schema", "title", "$defs", "$id")
            }
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

    The output is forced through a single tool call, so the model can only
    answer with JSON matching the output schema.

    Args:
        client: Anthropic API client.
        model: Model ID, e.g. claude-sonnet-5-5.
        system_prompt: Prompt text from prompts/<version>.md.
        output_schema: Output JSON schema.
        parcel_input: Filled input template for one parcel.
        today: Date used for time-based rules (6-month inheritance window).

    Returns:
        The evaluation dict produced by the model.

    Raises:
        ValueError: If the response contains no tool call.
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
        temperature=0,
        system=system_prompt,
        tools=[
            {
                "name": TOOL_NAME,
                "description": "Vrátí strukturované vyhodnocení parcely.",
                "input_schema": build_tool_schema(output_schema),
            },
        ],
        tool_choice={"type": "tool", "name": TOOL_NAME},
        messages=[{"role": "user", "content": user_message}],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == TOOL_NAME:
            return block.input
    raise ValueError(f"Model returned no {TOOL_NAME} call, stop_reason={response.stop_reason}")
