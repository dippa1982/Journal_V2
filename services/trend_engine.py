from collections import Counter, defaultdict
from statistics import mean

from models.entry import Entry
from constants.stop_words import STOP_WORDS

def build_trend_report(user):
    entries = Entry.query.filter_by(user_id=user.id).all()

    report = {}

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

    distribution = Counter()
    
    for entry in entries:

        if entry.mood_score:
            distribution[entry.mood_score] += 1

    report["distribution_labels"] = [
    str(mood)
    for mood in distribution.keys()
]

    report["distribution_values"] = list(distribution.values())

    tags = Counter()

    for entry in entries:

        if not entry.tags:
            continue

        for tag in entry.tags.split(", "):
            tags[tag.strip().lower()] += 1

    report["top_tags"] = tags.most_common(20)

    report["current_streak"] = 0

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