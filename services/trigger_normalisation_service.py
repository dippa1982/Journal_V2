import json

from services.trigger_normaliser import normalise_triggers
from models.trigger_normalisation import TriggerNormalisation
from extensions import db


def load_json(value):
    if not value:
        return []

    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return []


def build_normalised_triggers(analyses, batch_size=20):
    """
    Build normalised trigger records.

    Existing trigger normalisations are loaded from the database.
    Only genuinely new raw triggers are sent to Gemini.
    """

    # -------------------------------------------------
    # COLLECT RAW TRIGGERS
    # -------------------------------------------------

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

    # -------------------------------------------------
    # LOAD EXISTING NORMALISATIONS
    # -------------------------------------------------

    stored_normalisations = {
        record.raw_trigger.lower(): record
        for record in TriggerNormalisation.query.all()
    }

    # -------------------------------------------------
    # SEPARATE CACHED AND NEW TRIGGERS
    # -------------------------------------------------

    normalised_records = []
    new_trigger_records = []

    for record in trigger_records:

        raw = record["raw"]
        cached = stored_normalisations.get(raw.lower())

        if cached:

            normalised_records.append({
                "raw": raw,
                "normalised": cached.normalised_trigger,
                "confidence": cached.confidence,
                "entry_id": record["entry_id"]
            })

        else:

            new_trigger_records.append(record)

    # -------------------------------------------------
    # SEND ONLY NEW TRIGGERS TO GEMINI
    # -------------------------------------------------

    for start in range(
        0,
        len(new_trigger_records),
        batch_size
    ):

        batch = new_trigger_records[
            start:start + batch_size
        ]

        raw_triggers = [
            record["raw"]
            for record in batch
        ]

        if not raw_triggers:
            continue

        results = normalise_triggers(raw_triggers)

        # -------------------------------------------------
        # SAVE GEMINI RESULTS
        # -------------------------------------------------

        for result in results:

            raw = result.get("raw", "").strip()
            normalised = result.get("normalised")
            confidence = result.get("confidence")

            if not raw or not normalised:
                continue

            matching_records = [
                record
                for record in batch
                if record["raw"].lower() == raw.lower()
            ]

            # Save the normalisation to the database.
            existing = TriggerNormalisation.query.filter(
                db.func.lower(
                    TriggerNormalisation.raw_trigger
                ) == raw.lower()
            ).first()

            if not existing:

                existing = TriggerNormalisation(
                    raw_trigger=raw,
                    normalised_trigger=normalised,
                    confidence=confidence
                )

                db.session.add(existing)

            # Add the normalised result for each entry
            # where this trigger appeared.
            for record in matching_records:

                normalised_records.append({
                    "raw": record["raw"],
                    "normalised": normalised,
                    "confidence": confidence,
                    "entry_id": record["entry_id"]
                })

    # -------------------------------------------------
    # COMMIT NEW NORMALISATIONS
    # -------------------------------------------------

    db.session.commit()

    return normalised_records