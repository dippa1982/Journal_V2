import json

from services.ai_helper import ask_ai


def normalise_triggers(triggers):
    """
    Convert raw AI-generated trigger descriptions
    into consistent trigger concepts.
    """

    prompt = f"""
You are normalising extracted journal evidence.

You are NOT analysing the writer.
You are NOT identifying psychological patterns.
You are NOT diagnosing anything.
You are NOT giving advice.

Your only task is to determine whether different trigger descriptions
refer to the same underlying event or situation.

For each raw trigger:

1. Preserve the meaning of the original trigger.
2. Create a concise normalised trigger.
3. Do not add psychological interpretations.
4. Do not invent information.
5. Do not merge things merely because they are related.
6. Only merge descriptions when they clearly refer to the same
   underlying event or situation.

Examples:

"Nicola grabbed my arm"
"being grabbed"

can both become:

"Nicola grabbing the writer's arm"

But:

"Nicola's reassurance"
"Nicola's refusal of intimacy"

must remain separate.

Return ONLY valid JSON.

Format:

[
    {{
        "raw": "original trigger",
        "normalised": "normalised trigger"
    }}
]

Raw triggers:

{json.dumps(triggers, ensure_ascii=False, indent=2)}
"""

    result = ask_ai(prompt)

    return json.loads(result)