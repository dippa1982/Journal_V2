from datetime import date, timedelta

from collections import Counter

from models import Entry

def get_insights(user):
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
            {entry.created_at.date() for entry in entries},
            reverse=True
        )

        current_day = date.today()

        for day in unique_days:

            if day == current_day:

                streak += 1
                current_day -= timedelta(days=1)

            else:

                break

    mood_counts = {
        "happy": 0,
        "calm": 0,
        "anxious": 0,
        "angry": 0,
        "sad": 0,
        "frustrated": 0,
        "grateful": 0,
        "fearful": 0
    }

    for entry in entries:

        if entry.mood_score == 8:
            mood_counts["happy"] += 1

        elif entry.mood_score == 7:
            mood_counts["calm"] += 1

        elif entry.mood_score == 6:
            mood_counts["anxious"] += 1

        elif entry.mood_score == 5:
            mood_counts["angry"] += 1

        elif entry.mood_score == 4:
            mood_counts["sad"] += 1

        elif entry.mood_score == 3:
            mood_counts["frustrated"] += 1

        elif entry.mood_score == 2:
            mood_counts["grateful"] += 1

        elif entry.mood_score == 1:
            mood_counts["fearful"] += 1

    tag_counter = Counter()

    for entry in entries:

        if entry.tags:

            tags = [
                tag.strip()
                for tag in entry.tags.split(",")
            ]

            tag_counter.update(tags)

    top_tags = tag_counter.most_common(10)

    total_tags = sum(tag_counter.values())

    return {
        "entries": entries,
        "total_entries": total_entries,
        "average_mood": average_mood,
        "streak": streak,
        "mood_counts": mood_counts,
        "top_tags": top_tags,
        "total_tags": total_tags
    }