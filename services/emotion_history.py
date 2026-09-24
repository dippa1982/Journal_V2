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
    create a chart, and return the chart path.
    """

    analyses = (
        db.session.query(EntryAnalysis, Entry)
        .join(
            Entry,
            Entry.id == EntryAnalysis.entry_id
        )
        .filter(
            Entry.user_id == current_user.id
        )
        .order_by(
            Entry.created_at.asc()
        )
        .all()
    )

    rows = []

    for analysis, entry in analyses:

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

    df = df.drop_duplicates(
        subset=["entry_id", "emotion"]
    )

    top_emotions = (
        df["emotion"]
        .value_counts()
        .head(6)
        .index
        .tolist()
    )

    df = df[
        df["emotion"].isin(top_emotions)
    ]

        # ---------------------------------------------------------
    # Build weekly emotion counts
    # ---------------------------------------------------------

    df["date"] = pd.to_datetime(df["date"])

    weekly = (
        df
        .set_index("date")
        .groupby("emotion")
        .resample("W-MON")
        .size()
        .unstack(level=0, fill_value=0)
    )

    # Keep the emotions as rows and weeks as columns.
    weekly = weekly.T

    # ---------------------------------------------------------
    # Create output directory
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Create dark heatmap
    # ---------------------------------------------------------

    plt.style.use("dark_background")

    fig, ax = plt.subplots(
        figsize=(12, 5.5)
    )

    fig.patch.set_facecolor("#1f2937")
    ax.set_facecolor("#1f2937")

    # Heatmap values
    values = weekly.values

    image = ax.imshow(
        values,
        aspect="auto",
        cmap="viridis",
        interpolation="nearest"
    )

    # ---------------------------------------------------------
    # Axis labels
    # ---------------------------------------------------------

    ax.set_yticks(
        range(len(weekly.index))
    )

    ax.set_yticklabels(
        [emotion.title() for emotion in weekly.index]
    )

    ax.set_xticks(
        range(len(weekly.columns))
    )

    ax.set_xticklabels(
        [
            date.strftime("%d %b")
            for date in weekly.columns
        ],
        rotation=45,
        ha="right"
    )

    ax.set_title(
        "Emotion History — Weekly Frequency",
        fontsize=16,
        fontweight="bold",
        pad=20
    )

    ax.set_xlabel(
        "Week"
    )

    ax.set_ylabel(
        "Emotion"
    )

    # ---------------------------------------------------------
    # Add values inside cells
    # ---------------------------------------------------------

    for row in range(values.shape[0]):

        for column in range(values.shape[1]):

            value = values[row, column]

            if value > 0:

                ax.text(
                    column,
                    row,
                    int(value),
                    ha="center",
                    va="center",
                    fontsize=9,
                    color="white",
                    fontweight="bold"
                )

    # ---------------------------------------------------------
    # Colour scale
    # ---------------------------------------------------------

    colorbar = fig.colorbar(
        image,
        ax=ax,
        pad=0.02
    )

    colorbar.set_label(
        "Occurrences"
    )

    # ---------------------------------------------------------
    # Clean up chart
    # ---------------------------------------------------------

    ax.grid(
        False
    )

    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight",
        facecolor=fig.get_facecolor()
    )

    plt.close()

        # ---------------------------------------------------------
    # Most frequent emotions
    # ---------------------------------------------------------

    emotion_counts = (
        df.groupby("emotion")["entry_id"]
        .nunique()
        .sort_values(ascending=False)
    )

    summary = [
        {
            "emotion": emotion,
            "count": int(count)
        }
        for emotion, count in emotion_counts.items()
    ]

    return {
    "chart": f"generated/{filename}",
    "summary": summary
    }