import json
from datetime import date

import anthropic

# A full output is roughly 300 - 1,000 tokens; the cap only prevents truncated JSON and costs nothing extra
MAX_OUTPUT_TOKENS = 4_000


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
        ValueError: If the output was cut off at MAX_OUTPUT_TOKENS or the response contains no text block.
    """
    today = today or date.today()
    # Date goes into the message, not the prompt, so the prompt stays versioned and stable
    user_message = (
        f"Dnešní datum: {today.isoformat()}\n\n"
        f"Data o parcele:\n```json\n{json.dumps(parcel_input, ensure_ascii=False, indent=2)}\n```"
    )

    response = client.messages.create(
        model=model,
        max_tokens=MAX_OUTPUT_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
        output_config={
            "format": {
                "type": "json_schema",
                "schema": output_schema,
            },
        },
    )

    if response.stop_reason == "max_tokens":
        raise ValueError(f"Output was cut off at {MAX_OUTPUT_TOKENS} tokens, raise MAX_OUTPUT_TOKENS")

    for block in response.content:
        if block.type == "text":
            return json.loads(block.text)
    raise ValueError(f"Model returned no text block, stop_reason={response.stop_reason}")
