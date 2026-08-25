from collections import Counter

from datetime import datetime

from models import Entry
def get_entries(user):

    return Entry.query.filter_by(
        user_id=user.id
    ).order_by(
        Entry.created_at.desc()
    ).all()

def detect_patterns(user):
    entries = get_entries(user)

    report = {
    "emotional_patterns": [],
    "topic_patterns": [],
    "relationship_patterns": [],
    "mood_patterns": [],
    "recurring_tags": [],
    "significant_changes": []
    }

    mood_patterns = {
        "values": [],
        "average": 0,
        "lowest": 0,
        "highest": 0,
    }

    if not entries:
        return report

    # Detect recurring tags
    tag_counter = Counter()

    for entry in entries:

        if not entry.tags:
            continue

        for tag in entry.tags.split(","):
            tag = tag.strip()

            if tag:
                tag_counter[tag] += 1

        report["recurring_tags"] = [
        {
            "tag": tag,
            "count": count
        }
        for tag, count in tag_counter.most_common(10)
    ]

    # Detect mood patterns
    for entry in entries:
        if entry.mood_score:
            mood_patterns["values"].append(entry.mood_score)
            mood_patterns["average"] = round(sum(mood_patterns["values"]) / len(mood_patterns["values"]), 1)
            mood_patterns["lowest"] = min(mood_patterns["values"])
            mood_patterns["highest"] = max(mood_patterns["values"])

    print(mood_patterns)
    return report   
