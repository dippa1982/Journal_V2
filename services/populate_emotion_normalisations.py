import json

from extensions import db
from models.entry import Entry
from models.analyse import EntryAnalysis
from models.emotion_normalisation import EmotionNormalisation
from services.emotion_normaliser import normalise_emotions


def load_json(value):
    if not value:
        return []

    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return []


def populate_emotion_normalisations(
    user_id,
    batch_size=20
):
    """
    Populate the emotion normalisation cache.

    Processes exactly ONE Gemini batch per call.

    This is deliberately designed so the live application
    can never accidentally make a large number of Gemini
    requests in one request.
    """

    analyses = (
        EntryAnalysis.query
        .join(
            Entry,
            Entry.id == EntryAnalysis.entry_id
        )
        .filter(
            Entry.user_id == user_id
        )
        .order_by(
            Entry.created_at.asc()
        )
        .all()
    )

    if not analyses:
        return {
            "status": "no_analysis",
            "message": "No EntryAnalysis records found.",
            "saved": 0,
            "remaining": 0,
        }

    # --------------------------------------------------
    # Collect all unique raw emotions
    # --------------------------------------------------

    raw_emotions = set()

    for analysis in analyses:

        emotions = load_json(
            analysis.emotions
        )

        for emotion in emotions:

            if isinstance(emotion, dict):
                name = emotion.get("name")
            else:
                name = emotion

            if not name:
                continue

            name = str(name).strip()

            if name:
                raw_emotions.add(name)

    # --------------------------------------------------
    # Find existing cache
    # --------------------------------------------------

    cached = {
        record.raw_emotion.lower()
        for record in EmotionNormalisation.query.all()
    }

    uncached = sorted(
        emotion
        for emotion in raw_emotions
        if emotion.lower() not in cached
    )

    if not uncached:
        return {
            "status": "complete",
            "message": (
                "All emotions are already normalised."
            ),
            "saved": 0,
            "remaining": 0,
        }

    # --------------------------------------------------
    # ONE Gemini batch only
    # --------------------------------------------------

    batch = uncached[:batch_size]

    try:

        results = normalise_emotions(
            batch
        )

    except Exception as exc:

        db.session.rollback()

        return {
            "status": "error",
            "message": str(exc),
            "saved": 0,
            "remaining": len(uncached),
        }

    if not isinstance(results, list):

        return {
            "status": "error",
            "message": (
                "Gemini returned an invalid response."
            ),
            "saved": 0,
            "remaining": len(uncached),
        }

    # --------------------------------------------------
    # Save results
    # --------------------------------------------------

    saved = 0

    for result in results:

        if not isinstance(result, dict):
            continue

        raw = result.get(
            "raw",
            ""
        ).strip()

        normalised = result.get(
            "normalised"
        )

        confidence = result.get(
            "confidence"
        )

        if not raw or not normalised:
            continue

        original = next(
            (
                emotion
                for emotion in batch
                if emotion.lower() == raw.lower()
            ),
            None
        )

        if not original:
            continue

        existing = (
            EmotionNormalisation.query
            .filter(
                db.func.lower(
                    EmotionNormalisation.raw_emotion
                ) == raw.lower()
            )
            .first()
        )

        if existing:
            continue

        db.session.add(
            EmotionNormalisation(
                raw_emotion=original,
                normalised_emotion=normalised,
                confidence=confidence
            )
        )

        saved += 1

    try:

        db.session.commit()

    except Exception as exc:

        db.session.rollback()

        return {
            "status": "error",
            "message": (
                f"Database save failed: {exc}"
            ),
            "saved": 0,
            "remaining": len(uncached),
        }

    remaining = len(uncached) - len(batch)

    return {
        "status": "success",
        "message": (
            f"Processed {len(batch)} emotions."
        ),
        "saved": saved,
        "remaining": max(
            remaining,
            0
        ),
        "batch": batch,
    }