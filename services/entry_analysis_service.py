from constants.ai_prompt import ai_prompt_entry_analysis

from services.ai_helper import (
    ask_ai,
    parse_ai_response
)

from extensions import db

from models import Entry, EntryAnalysis

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

    data = validate_analysis(data)

    analysis = save_entry_analysis(
        entry,
        data
    )

    return analysis

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

def save_entry_analysis(entry, data):

    analysis = EntryAnalysis.query.filter_by(
        entry_id=entry.id
    ).first()

    if analysis:

        analysis.emotions = data.get(
            "emotions",
            []
        )

        analysis.topics = data.get(
            "topics",
            []
        )

        analysis.triggers = data.get(
            "triggers",
            []
        )

        analysis.behaviours = data.get(
            "behaviours",
            []
        )

        analysis.needs = data.get(
            "needs",
            []
        )

        analysis.beliefs = data.get(
            "beliefs",
            []
        )

        analysis.positive_changes = data.get(
            "positive_changes",
            []
        )

        analysis.possible_patterns = data.get(
            "observations",
            []
        )

    else:

        analysis = EntryAnalysis(

            entry_id=entry.id,

            emotions=data.get(
                "emotions",
                []
            ),

            topics=data.get(
                "topics",
                []
            ),

            triggers=data.get(
                "triggers",
                []
            ),

            behaviours=data.get(
                "behaviours",
                []
            ),

            needs=data.get(
                "needs",
                []
            ),

            beliefs=data.get(
                "beliefs",
                []
            ),

            positive_changes=data.get(
                "positive_changes",
                []
            ),

            possible_patterns=data.get(
                "observations",
                []
            )
        )

        db.session.add(analysis)

    db.session.commit()

    return analysis