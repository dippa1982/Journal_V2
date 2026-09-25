from services.ai_helper import ask_ai

import json


def normalise_emotions(raw_emotions):
    """
    Normalise raw emotion names into consistent emotion labels.

    This function only normalises wording.
    It does not interpret, diagnose, or change the meaning
    of the emotion.
    """

    if not raw_emotions:
        return []

    emotion_list = "\n".join(
        f"- {emotion}"
        for emotion in raw_emotions
    )

    prompt = f"""
You are normalising emotion labels extracted from journal entries.

Your ONLY task is to make different wordings for the same
emotion consistent.

Rules:

- Preserve the meaning of the original emotion.
- Do not invent emotions.
- Do not interpret the emotion.
- Do not infer psychological meaning.
- Do not combine emotions that are meaningfully different.
- Different grammatical forms of the same emotion should be
  normalised to the same concise label.
- Prefer a simple noun form where appropriate.
- "tired" and "tiredness" should become "tiredness".
- "angry" and "anger" should become "anger".
- "sad" and "sadness" should become "sadness".
- Keep genuinely different emotions separate.
- Return ONLY valid JSON.
- Return one result for every input emotion.

Input emotions:

{emotion_list}

Return exactly this structure:

[
    {{
        "raw": "original emotion",
        "normalised": "normalised emotion",
        "confidence": "high"
    }}
]

Confidence refers ONLY to how confident you are that the
normalised label preserves the meaning of the original label.
Use only:
- high
- medium
- low
"""

    result = ask_ai(prompt)

    if isinstance(result, str):

        try:
            result = json.loads(result)

        except json.JSONDecodeError:
            return []

    if not isinstance(result, list):
        return []

    return result