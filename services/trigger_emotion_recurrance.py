import json
from collections import defaultdict


def load_json(value):
    if not value:
        return []

    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return []


def build_trigger_emotion_recurrence(
    normalised_records,
    analyses,
    normalised_emotions=None,
    minimum_trigger_mentions=2
):
    """
    Build recurring trigger → emotion relationships.

    Emotion labels are normalised using the database cache
    when available.

    This is evidence gathering only.
    It does not infer causation.
    """

    # --------------------------------------------------
    # Build recurring trigger data
    # --------------------------------------------------

    trigger_entries = defaultdict(set)

    for record in normalised_records:

        trigger = record.get("normalised")
        entry_id = record.get("entry_id")

        if not trigger or not entry_id:
            continue

        trigger_key = trigger.strip().lower()

        trigger_entries[trigger_key].add(
            entry_id
        )

    recurring_triggers = {
        trigger
        for trigger, entry_ids
        in trigger_entries.items()
        if len(entry_ids) >= minimum_trigger_mentions
    }

    # --------------------------------------------------
    # Build emotions by entry
    # --------------------------------------------------

    emotions_by_entry = {}

    for analysis in analyses:

        emotions = load_json(
            analysis.emotions
        )

        emotion_names = []

        for emotion in emotions:

            if isinstance(emotion, dict):
                name = emotion.get("name")
            else:
                name = emotion

            if not name:
                continue

            raw_name = str(name).strip()

            if not raw_name:
                continue

            # ------------------------------------------
            # Apply cached normalisation
            # ------------------------------------------

            normalised_name = raw_name

            if normalised_emotions:

                cached = normalised_emotions.get(
                    raw_name.lower()
                )

                if cached:
                    normalised_name = (
                        cached.get("normalised")
                        or raw_name
                    )

            emotion_names.append(
                normalised_name
            )

        emotions_by_entry[
            analysis.entry_id
        ] = emotion_names

    # --------------------------------------------------
    # Build trigger → emotion relationships
    # --------------------------------------------------

    relationship_data = defaultdict(
        lambda: {
            "entries": set()
        }
    )

    for record in normalised_records:

        trigger = record.get("normalised")
        entry_id = record.get("entry_id")

        if not trigger or not entry_id:
            continue

        trigger_key = trigger.strip().lower()

        if trigger_key not in recurring_triggers:
            continue

        emotions = emotions_by_entry.get(
            entry_id,
            []
        )

        seen_emotions = set()

        for emotion in emotions:

            emotion_key = emotion.strip().lower()

            if not emotion_key:
                continue

            if emotion_key in seen_emotions:
                continue

            seen_emotions.add(
                emotion_key
            )

            relationship_data[
                (trigger_key, emotion_key)
            ]["entries"].add(
                entry_id
            )

    # --------------------------------------------------
    # Group relationships by trigger
    # --------------------------------------------------

    grouped = defaultdict(list)

    for (
        trigger,
        emotion
    ), data in relationship_data.items():

        grouped[trigger].append({
            "emotion": emotion,
            "mentions": len(
                data["entries"]
            ),
            "entry_ids": sorted(
                data["entries"]
            )
        })

    # --------------------------------------------------
    # Build final results
    # --------------------------------------------------

    results = []

    for trigger in recurring_triggers:

        emotions = grouped.get(
            trigger,
            []
        )

        emotions.sort(
            key=lambda item: item["mentions"],
            reverse=True
        )

        results.append({
            "trigger": trigger,
            "trigger_mentions": len(
                trigger_entries[trigger]
            ),
            "emotions": emotions
        })

    results.sort(
        key=lambda item: item["trigger_mentions"],
        reverse=True
    )

    return results