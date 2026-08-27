from datetime import datetime, timedelta

from models import Entry

from collections import Counter

def get_week_entries(user):

    today = datetime.now().date()

    start_date = today - timedelta(days=6)

    start_datetime = datetime.combine(
        start_date,
        datetime.min.time()
    )

    end_datetime = datetime.combine(
        today,
        datetime.max.time()
    )

    return Entry.query.filter(
        Entry.user_id == user.id,
        Entry.created_at >= start_datetime,
        Entry.created_at <= end_datetime
    ).order_by(
        Entry.created_at.desc()
    ).all()


def build_review(entries):

    mood_scores = []

    for entry in entries:

        if entry.mood_score is not None:
            mood_scores.append(entry.mood_score)

    mood_scores = list(reversed(mood_scores))

    weekly_report = {
        "entry_count": len(entries),
        "mood_scores": mood_scores,
        "average_score": 0,
        "best_score": 0,
        "worst_score": 0,
        "recurring_tags": [],
        "mood_trend": [],
    }


    if mood_scores:

        weekly_report["average_score"] = round(
            sum(mood_scores) / len(mood_scores),
            1
        )

        weekly_report["best_score"] = max(mood_scores)

        weekly_report["worst_score"] = min(mood_scores)

    tag_counter = Counter()

    for entry in entries:

        if not entry.tags:
            continue

        for tag in entry.tags.split(","):

            tag = tag.strip()

            if tag:
                tag_counter[tag] += 1


    weekly_report["recurring_tags"] = [
        {
            "tag": tag,
            "count": count
        }
        for tag, count in tag_counter.most_common(10)
    ]

    return weekly_report