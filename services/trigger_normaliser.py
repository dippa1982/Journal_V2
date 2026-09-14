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

Confidence must be one of:

"high" - the raw triggers clearly describe the same underlying event
or situation.

"medium" - the relationship is reasonably clear but there is some
uncertainty.

"low" - the relationship is questionable or based mainly on similarity.

If a trigger is not being merged with another trigger, use "high"
for its own normalised form.

Do not use confidence to express psychological certainty.
It only describes how confident you are that the raw trigger and
normalised trigger represent the same underlying event or situation.

Return ONLY valid JSON.

Format:

[
    {{
        "raw": "original trigger",
        "normalised": "normalised trigger"
        "confidence":"high"
    }}
]

Raw triggers:

{json.dumps(triggers, ensure_ascii=False, indent=2)}
"""

    result = ask_ai(prompt)

    return json.loads(result)