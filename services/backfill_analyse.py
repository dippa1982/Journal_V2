from models import Entry, EntryAnalysis
from services.entry_analysis_service import analyse_entry


def backfill_user_entries(user, batch_size=3):

    entries = (
        Entry.query
        .filter_by(user_id=user.id)
        .order_by(Entry.created_at.asc())
        .all()
    )

    analysed = 0
    skipped = 0
    failed = 0

    for entry in entries:

        existing = EntryAnalysis.query.filter_by(
            entry_id=entry.id
        ).first()

        if existing:
            skipped += 1
            continue

        if analysed >= batch_size:
            break

        try:

            analyse_entry(entry)

            analysed += 1

            print(
                f"Analysed entry {entry.id}"
            )

        except Exception as e:

            failed += 1

            print(
                f"Failed entry {entry.id}: {e}"
            )

    remaining = (
        Entry.query
        .filter_by(user_id=user.id)
        .count()
        -
        EntryAnalysis.query
        .join(Entry)
        .filter(
            Entry.user_id == user.id
        )
        .count()
    )

    return {
        "analysed_this_run": analysed,
        "skipped": skipped,
        "failed": failed,
        "remaining": max(remaining, 0)
    }