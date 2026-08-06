
from datetime import date, timedelta

from models import Entry

def get_dashboard_stats(user):

    print(user)
    print(user.id)
    entries = Entry.query.filter_by(
    user_id=user.id
    ).all()

    total_entries = len(entries)

    if total_entries:
        average_mood = round(
            sum(entry.mood_score for entry in entries)
            / total_entries,
            1
        )
    else:
        average_mood = 0

    streak = 0

    if entries:

        unique_days = sorted(
            {
                entry.created_at.date()
                for entry in entries
            },
            reverse=True
        )

        current_day = date.today()

        for day in unique_days:

            if day == current_day:

                streak += 1
                current_day -= timedelta(days=1)

            elif day == current_day - timedelta(days=1):

                streak += 1
                current_day -= timedelta(days=1)

            else:

                break

    return {
        "entries": entries,
        "total_entries": total_entries,
        "average_mood": average_mood,
        "streak": streak
    }