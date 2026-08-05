from collections import Counter, defaultdict
from statistics import mean

from models.entry import Entry
from constants.stop_words import STOP_WORDS

def build_trend_report(user):
    entries = Entry.query.filter_by(user_id=user.id).all()

    report = {

        "total_entries": 0,
        "average_mood": 0,
        "current_streak": 0,
        
        "mood_labels": [],
        "mood_values": [],

        "weekly_labels": [],
        "weekly_values": [],

        "monthly_labels": [],
        "monthly_values": [],

        "distribution_labels": [],
        "distribution_values": [],

        "top_tags": [],
        "keywords": [],

        "most_common_mood": None,
        "entries_this_month": 0,
        "best_month": None,
        "longest_entry_words": 0,
        "total_words":  0,
        "average_words":  0,

        "best_day": None,
        "worst_day": None,
        "most_productive_week":  None,
        "longest_gap": 0,
    }

    report["total_entries"] = len(entries)

    moods = [entry.mood_score for entry in entries
             if entry.mood_score]
    
    report["average_mood"] = (round(mean(moods), 1 )
                              if moods else 0
    )

    report["mood_labels"] = [
    entry.created_at.strftime("%d %b")
    for entry in entries
    ]

    report["mood_values"] = [
    entry.mood_score
    for entry in entries
    ]

    weeks = defaultdict(list)

    for entry in entries:

        if entry.mood_score is None:
            continue

        week = entry.created_at.strftime("%Y-%U")
        
        weeks[week].append(entry.mood_score)

    report["weekly_labels"] = list(weeks.keys())

    report["weekly_values"] = [
                    round(mean(scores), 1)
                    for scores in weeks.values()
    ]
    
    months = defaultdict(list)

    for entry in entries:

        if entry.mood_score is None:
            continue

        month = entry.created_at.strftime("%Y-%m")
        
        months[month].append(entry.mood_score)

    report["monthly_labels"] = list(months.keys())

    report["monthly_values"] = [
                        round(mean(scores), 1)
                        for scores in months.values()
    ]

    from constants.moods import MOODS

    distribution = Counter()

    for entry in entries:

        if not entry.mood_score:
            continue

        mood = MOODS.get(entry.mood_score)

        if mood:
            distribution[mood["name"]] += 1

    report["mood_distribution"] = dict(distribution)

    if distribution:

        report["distribution_labels"] = list(distribution.keys())
        report["distribution_values"] = list(distribution.values())

        report["most_common_mood"] = distribution.most_common(1)[0][0]

    else:

        report["distribution_labels"] = []
        report["distribution_values"] = []
        report["most_common_mood"] = "-"

    from datetime import datetime

    current_month = datetime.now().strftime("%Y-%m")

    report["entries_this_month"] = sum(1

    for entry in entries

    if entry.created_at.strftime("%Y-%m") == current_month

    )

    if months:

        averages = {

            month: round(mean(scores), 1)

            for month, scores in months.items()

        }

        report["best_month"] = max(
            averages,
            key=averages.get
        )

    else:

        report["best_month"] = "-"

    if entries:

        longest = max(

            entries,

            key=lambda e: len(e.content or "")

        )

        report["longest_entry_words"] = len(
            longest.content.split()
        )

    else:

        report["longest_entry_words"] = 0

    report["total_words"] = sum(

    len((entry.content or "").split())

    for entry in entries

)

    if entries:

        report["average_words"] = round(

        report["total_words"] / len(entries)

    )

    else:

         report["average_words"] = 0

    report["distribution_values"] = list(distribution.values())

    from datetime import date, timedelta

    unique_days = sorted(

        {

            entry.created_at.date()

            for entry in entries

        },

        reverse=True

    )

    today = date.today()

    streak = 0

    for day in unique_days:

        if day == today:

            streak += 1

            today -= timedelta(days=1)

        else:

            break

    report["current_streak"] = streak

    

    tags = Counter()

    for entry in entries:

        if not entry.tags:
            continue

        for tag in entry.tags.split(", "):
            tags[tag.strip().lower()] += 1

    report["top_tags"] = tags.most_common(20)

    report["first_entry"] = (
        entries[0].created_at.strftime("%d %b %Y")
        if entries else "-"
    )

    words = Counter()

    for entry in entries:

        if not entry.content:
            continue

        for word in entry.content.lower().split():
            word = word.strip(".,!?()[]{}\"':;")

            if len(word) < 3:
                continue

            if word in STOP_WORDS:
                continue

            words[word] += 1

    report["keywords"] = words.most_common(25)

    return report