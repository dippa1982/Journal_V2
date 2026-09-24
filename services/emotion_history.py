import json
import os

import pandas as pd
import matplotlib.pyplot as plt

from extensions import db

from flask import current_app
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


def build_emotion_history():
    """
    Build the user's emotional history,
    create a chart, and return the chart URL.
    """

    analyses = (
    db.session.query(EntryAnalysis, Entry)
    .join(Entry, Entry.id == EntryAnalysis.entry_id)
    .filter(Entry.user_id == current_user.id)
    .order_by(Entry.created_at.asc())
    .all()
    )

    rows = []

    for analysis in analyses:

        emotions = load_json(analysis.emotions)

        if not emotions:
            continue

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
        return None

    df = pd.DataFrame(rows)

    # Don't count the same emotion twice in one entry.
    df = df.drop_duplicates(
        subset=["entry_id", "emotion"]
    )

    # Find the most common emotions.
    top_emotions = (
        df["emotion"]
        .value_counts()
        .head(6)
        .index
        .tolist()
    )

    df = df[df["emotion"].isin(top_emotions)]

    # Count emotion occurrences per day.
    history = (
        df.groupby(["date", "emotion"])
        .size()
        .unstack(fill_value=0)
        .sort_index()
    )

    # Make sure the output directory exists.
    output_dir = os.path.join(
        current_app.static_folder,
        "generated"
    )

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    filename = (
        f"emotion_history_{current_user.id}.png"
    )

    output_path = os.path.join(
        output_dir,
        filename
    )

    # Create chart.
    plt.figure(figsize=(12, 5))

    for emotion in history.columns:
        plt.plot(
            history.index,
            history[emotion],
            marker="o",
            linewidth=2,
            label=emotion.title()
        )

    plt.title("Emotion History")
    plt.xlabel("Date")
    plt.ylabel("Entries")
    plt.legend(
        loc="upper left",
        bbox_to_anchor=(1, 1)
    )

    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    return f"generated/{filename}"