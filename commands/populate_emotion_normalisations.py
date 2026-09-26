import json

import click
from flask import current_app
from flask.cli import with_appcontext

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


@click.command("populate-emotion-normalisations")
@click.option(
    "--user-id",
    type=int,
    required=True,
    help="User ID to process."
)
@click.option(
    "--batch-size",
    default=20,
    show_default=True,
    help="Number of emotion labels sent to Gemini per request."
)
@click.option(
    "--max-batches",
    default=1,
    show_default=True,
    help="Maximum number of Gemini requests to make."
)
@with_appcontext
def populate_emotion_normalisations(
    user_id,
    batch_size,
    max_batches
):
    """
    Populate the emotion normalisation cache using Gemini.
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
        click.echo(
            f"No EntryAnalysis records found for user {user_id}."
        )
        return

    # --------------------------------------------------
    # Collect unique raw emotions
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Find emotions already cached
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

    click.echo(
        f"Found {len(raw_emotions)} unique emotions."
    )

    click.echo(
        f"{len(cached)} emotions already cached."
    )

    click.echo(
        f"{len(uncached)} emotions still need normalising."
    )

    if not uncached:
        click.echo(
            "Nothing to do. Emotion normalisation cache is complete."
        )
        return

    # --------------------------------------------------
    # Process controlled batches
    # --------------------------------------------------

    processed_batches = 0

    for start in range(
        0,
        len(uncached),
        batch_size
    ):
        if processed_batches >= max_batches:
            break

        batch = uncached[
            start:start + batch_size
        ]

        click.echo("")
        click.echo(
            f"Sending batch {processed_batches + 1}:"
        )

        for emotion in batch:
            click.echo(f"  - {emotion}")

        try:
            results = normalise_emotions(batch)

        except Exception as exc:
            db.session.rollback()

            click.echo("")
            click.echo(
                "Gemini request failed."
            )
            click.echo(
                f"Error: {exc}"
            )
            click.echo(
                "Stopping safely. Previously cached "
                "normalisations have been preserved."
            )
            break

        if not isinstance(results, list):
            click.echo(
                "Gemini returned an invalid response."
            )
            break

        saved = 0

        for result in results:

            if not isinstance(result, dict):
                continue

            raw = result.get("raw", "").strip()
            normalised = result.get("normalised")
            confidence = result.get("confidence")

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

            record = EmotionNormalisation(
                raw_emotion=original,
                normalised_emotion=normalised,
                confidence=confidence
            )

            db.session.add(record)
            saved += 1

        try:
            db.session.commit()

        except Exception as exc:
            db.session.rollback()

            click.echo("")
            click.echo(
                f"Database save failed: {exc}"
            )
            click.echo(
                "Stopping safely."
            )
            break

        processed_batches += 1

        click.echo("")
        click.echo(
            f"Saved {saved} emotion normalisations."
        )

    click.echo("")
    click.echo(
        f"Finished. Gemini batches used: "
        f"{processed_batches}"
    )