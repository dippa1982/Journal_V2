import json

from extensions import db
from models.emotion_normalisation import EmotionNormalisation
from services.emotion_normaliser import normalise_emotions


def load_json(value):
    """Safely load a JSON string."""
    if not value:
        return []

    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return []


def build_normalised_emotions(analyses, batch_size=20, use_ai=True):
    """
    Normalise emotions while using the database as a cache.

    Existing emotions are loaded from the database.
    Only previously unseen emotions are sent to Gemini.
    """

    # ---------------------------------------------------------
    # Collect unique raw emotions
    # ---------------------------------------------------------

    raw_emotions = set()

    for analysis in analyses:

        emotions = load_json(analysis.emotions)

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

    # ---------------------------------------------------------
    # Load existing cached normalisations
    # ---------------------------------------------------------

    cached = {
        record.raw_emotion.lower(): record
        for record in EmotionNormalisation.query.all()
    }

    normalised_lookup = {}

    new_emotions = []

    for raw_emotion in sorted(raw_emotions):

        cached_record = cached.get(
            raw_emotion.lower()
        )

        if cached_record:

            normalised_lookup[
                raw_emotion.lower()
            ] = {
                "normalised": cached_record.normalised_emotion,
                "confidence": cached_record.confidence
            }

        else:

            new_emotions.append(raw_emotion)

    # ---------------------------------------------------------
    # Normalise new emotions with Gemini
    # ---------------------------------------------------------

    if use_ai:

        for start in range(
            0,
            len(new_emotions),
            batch_size
        ):

            batch = new_emotions[
                start:start + batch_size
            ]

            if not batch:
                continue

            results = normalise_emotions(batch)

            if not isinstance(results, list):
                continue

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

                if not existing:

                    existing = EmotionNormalisation(
                        raw_emotion=raw,
                        normalised_emotion=normalised,
                        confidence=confidence
                    )

                    db.session.add(existing)

                normalised_lookup[
                    original.lower()
                ] = {
                    "normalised": normalised,
                    "confidence": confidence
                }

            db.session.commit()

    return normalised_lookup