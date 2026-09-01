from models import Entry, EntryAnalysis
from services.entry_analysis_service import analyse_entry


def backfill_user_entries(user):

    entries = (
        Entry.query
        .filter_by(user_id=user.id)
        .order_by(Entry.created_at.asc())
        .all()
    )

    total = len(entries)
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

        try:

            analyse_entry(entry)

            analysed += 1

            print(
                f"Analysed entry "
                f"{entry.id} "
                f"({analysed}/{total})"
            )

        except Exception as e:

            failed += 1

            print(
                f"Failed to analyse entry "
                f"{entry.id}: {e}"
            )

    return {
        "total": total,
        "analysed": analysed,
        "skipped": skipped,
        "failed": failed
    }