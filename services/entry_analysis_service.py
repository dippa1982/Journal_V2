from constants.ai_prompt import ai_prompt_entry_analysis

from services.ai_helper import (
    ask_ai,
    parse_ai_response
)

from extensions import db

import json

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

    values = {
        "emotions": json.dumps(
            data.get("emotions", []),
            ensure_ascii=False
        ),

        "topics": json.dumps(
            data.get("topics", []),
            ensure_ascii=False
        ),

        "triggers": json.dumps(
            data.get("triggers", []),
            ensure_ascii=False
        ),

        "behaviours": json.dumps(
            data.get("behaviours", []),
            ensure_ascii=False
        ),

        "needs": json.dumps(
            data.get("needs", []),
            ensure_ascii=False
        ),

        "beliefs": json.dumps(
            data.get("beliefs", []),
            ensure_ascii=False
        ),

        "positive_changes": json.dumps(
            data.get("positive_changes", []),
            ensure_ascii=False
        ),

        "observations": json.dumps(
            data.get("observations", []),
            ensure_ascii=False
        )
    }

    if analysis:

        analysis.emotions = values["emotions"]
        analysis.topics = values["topics"]
        analysis.triggers = values["triggers"]
        analysis.behaviours = values["behaviours"]
        analysis.needs = values["needs"]
        analysis.beliefs = values["beliefs"]
        analysis.positive_changes = values["positive_changes"]
        analysis.observations = values["observations"]

    else:

        analysis = EntryAnalysis(
            entry_id=entry.id,

            emotions=values["emotions"],
            topics=values["topics"],
            triggers=values["triggers"],
            behaviours=values["behaviours"],
            needs=values["needs"],
            beliefs=values["beliefs"],
            positive_changes=values["positive_changes"],
            observations=values["observations"]
        )

        db.session.add(analysis)

    db.session.commit()

    print(analysis)
    return analysis