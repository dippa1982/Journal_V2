from constants.ai_prompt import ai_prompt_entry_analysis

from services.ai_helper import (
    ask_ai,
    parse_ai_response
)


def analyse_entry(entry):

    if not entry:
        raise ValueError(
            "An entry is required for analysis."
        )

    if not entry.content or not entry.content.strip():
        raise ValueError(
            "The entry has no content to analyse."
        )

    prompt = ai_prompt_entry_analysis(entry)

    result = ask_ai(prompt)

    data = parse_ai_response(result)

    return validate_analysis(data)

def validate_analysis(data):

    if not isinstance(data, dict):
        raise ValueError(
            "Entry analysis must be a JSON object."
        )

    list_fields = [
        "emotions",
        "topics",
        "people",
        "triggers",
        "behaviours",
        "needs",
        "beliefs",
        "observations",
        "positive_changes"
    ]

    cleaned = {}

    for field in list_fields:

        value = data.get(field, [])

        if not isinstance(value, list):
            value = []

        cleaned[field] = value

    cleaned["emotions"] = clean_emotions(
        cleaned["emotions"]
    )

    return cleaned

def clean_emotions(emotions):

    cleaned = []

    for emotion in emotions:

        if not isinstance(emotion, dict):
            continue

        name = str(
            emotion.get("name", "")
        ).strip().lower()

        if not name:
            continue

        try:
            intensity = int(
                emotion.get("intensity", 5)
            )

        except (TypeError, ValueError):
            intensity = 5

        intensity = max(
            1,
            min(10, intensity)
        )

        confidence = str(
            emotion.get(
                "confidence",
                "medium"
            )
        ).lower()

        if confidence not in {
            "high",
            "medium",
            "low"
        }:
            confidence = "medium"

        cleaned.append(
            {
                "name": name,
                "intensity": intensity,
                "confidence": confidence
            }
        )

    return cleaned