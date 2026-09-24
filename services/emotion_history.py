import json
import pandas as pd

from flask_login import current_user

from models.analyse import EntryAnalysis
from models.entry import Entry


def load_json(value):
    """Safely load a JSON string."""
    if not value:
        return []

    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return []


def build_emotion_history(user):
    """
    Build a Pandas DataFrame containing the user's
    emotional history over time.
    """

    rows = []

    analyses = (
        EntryAnalysis.query
        .join(Entry, Entry.id == EntryAnalysis.entry_id)
        .filter(Entry.user_id == user.id)
        .order_by(Entry.created_at.asc())
        .all()
    )

    for analysis in analyses:

        emotions = load_json(analysis.emotions)

        if not emotions:
            continue

        entry = analysis.entry

        for emotion in emotions:

            if isinstance(emotion, dict):
                name = emotion.get("name")
                intensity = emotion.get("intensity")
                confidence = emotion.get("confidence")
            else:
                name = emotion
                intensity = None
                confidence = None

            if not name:
                continue

            rows.append({
                "entry_id": entry.id,
                "date": entry.created_at.date(),
                "emotion": str(name).strip().lower(),
                "intensity": intensity,
                "confidence": confidence,
            })

    if not rows:
        return pd.DataFrame(
            columns=[
                "entry_id",
                "date",
                "emotion",
                "intensity",
                "confidence",
            ]
        )

    df = pd.DataFrame(rows)

    # An emotion should only count once per journal entry.
    df = df.drop_duplicates(
        subset=["entry_id", "emotion"]
    )

    return df