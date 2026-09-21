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
    minimum_trigger_mentions=2
):
    """
    Connect recurring triggers with emotions recorded
    in the same journal entries.

    This identifies co-occurrence, not causation.
    """

    # ---------------------------------------------------------
    # STEP 1
    # Identify which triggers are actually recurring
    # across different journal entries.
    # ---------------------------------------------------------

    trigger_entries = defaultdict(set)

    for record in normalised_records:
        trigger = record.get("normalised")
        entry_id = record.get("entry_id")

        if not trigger or not entry_id:
            continue

        trigger_key = trigger.strip().lower()
        trigger_entries[trigger_key].add(entry_id)

    recurring_triggers = {
        trigger
        for trigger, entry_ids in trigger_entries.items()
        if len(entry_ids) >= minimum_trigger_mentions
    }

    # ---------------------------------------------------------
    # STEP 2
    # Build a lookup of emotions for each journal entry.
    # ---------------------------------------------------------

    emotions_by_entry = {}

    for analysis in analyses:
        emotions = load_json(analysis.emotions)

        emotion_names = []

        for emotion in emotions:

            if isinstance(emotion, dict):
                name = emotion.get("name")

            else:
                name = emotion

            if not name:
                continue

            name = str(name).strip()

            if name:
                emotion_names.append(name)

        emotions_by_entry[analysis.entry_id] = emotion_names

    # ---------------------------------------------------------
    # STEP 3
    # Connect recurring triggers to emotions
    # found in the same entries.
    # ---------------------------------------------------------

    relationships = defaultdict(lambda: {
        "entries": set()
    })

    for record in normalised_records:

        trigger = record.get("normalised")
        entry_id = record.get("entry_id")

        if not trigger or not entry_id:
            continue

        trigger_key = trigger.strip().lower()

        if trigger_key not in recurring_triggers:
            continue

        emotions = emotions_by_entry.get(entry_id, [])

        for emotion in emotions:

            emotion_key = emotion.lower()

            relationship_key = (
                trigger_key,
                emotion_key
            )

            relationships[relationship_key]["entries"].add(
                entry_id
            )

    results = []

    for (trigger, emotion), data in relationships.items():

        results.append({
            "trigger": trigger,
            "emotion": emotion,
            "mentions": len(data["entries"]),
            "entry_ids": sorted(data["entries"])
        })

    # Most frequently recurring relationships first.
    results.sort(
        key=lambda item: item["mentions"],
        reverse=True
    )

    return results