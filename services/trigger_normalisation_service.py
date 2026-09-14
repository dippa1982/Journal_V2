from services.trigger_normaliser import normalise_triggers

import json

def load_json(value):
    if not value:
        return []

    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return []

def build_normalised_triggers(analyses, batch_size=20):
    """
    Normalise raw triggers while keeping their original entry IDs.
    """

    # Collect raw triggers and the entry they came from.
    trigger_records = []

    for analysis in analyses:

        triggers = load_json(analysis.triggers)

        if not triggers:
            continue

        # Prevent duplicate trigger text within one entry.
        seen_triggers = set()

        for trigger in triggers:

            trigger_name = str(trigger).strip()

            if not trigger_name:
                continue

            key = trigger_name.lower()

            if key in seen_triggers:
                continue

            seen_triggers.add(key)

            trigger_records.append({
                "raw": trigger_name,
                "entry_id": analysis.entry_id
            })

    # Process the triggers in batches.
    normalised_records = []

    for start in range(0, len(trigger_records), batch_size):

        batch = trigger_records[start:start + batch_size]

        raw_triggers = [
            record["raw"]
            for record in batch
        ]

        results = normalise_triggers(raw_triggers)

        # Match Gemini's response back to the original entry IDs.
        for result in results:

            raw = result.get("raw", "").strip()

            matching_records = [
                record
                for record in batch
                if record["raw"].lower() == raw.lower()
            ]

            for record in matching_records:

                normalised_records.append({
                    "raw": record["raw"],
                    "normalised": result.get("normalised"),
                    "confidence": result.get("confidence"),
                    "entry_id": record["entry_id"]
                })

    return normalised_records