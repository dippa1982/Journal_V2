from collections import Counter

from datetime import datetime


def build_relationship_dashboard(person):

    # -----------------------------------
    # Load Entries
    # -----------------------------------

    entries = sorted(
        person.entries,
        key=lambda e: e.created_at
    )

    # -----------------------------------
    # Default Values
    # -----------------------------------

    average_mood = 0
    first_mentioned = None
    last_mentioned = None

    average_relationship_score = 0

    best_day = None
    worst_day = None

    mood_labels = []
    mood_values = []

    tag_counter = Counter()

    timeline = []

    # -----------------------------------
    # Statistics
    # -----------------------------------

    if entries:

        average_mood = round(
            sum(e.mood_score for e in entries) / len(entries),
            1
        )

        first_mentioned = entries[0].created_at
        last_mentioned = entries[-1].created_at

        best_day = max(
            entries,
            key=lambda e: e.mood_score
        )

        worst_day = min(
            entries,
            key=lambda e: e.mood_score
        )

    days_since_last_mention = None
    if last_mentioned:
        days_since_last_mention = (datetime.now() - last_mentioned).days

    # -----------------------------------
    # Relationship Score
    # -----------------------------------

    scores = [

        e.relationship_score

        for e in entries

        if e.relationship_score is not None

    ]

    if scores:

        average_relationship_score = round(
            sum(scores) / len(scores),
            1
        )

    # -----------------------------------
    # Mood Chart
    # -----------------------------------

    for entry in entries:

        mood_labels.append(
            entry.created_at.strftime("%d %b")
        )

        mood_values.append(
            entry.mood_score
        )

    # -----------------------------------
    # Tags
    # -----------------------------------

    for entry in entries:

        if entry.tags:

            for tag in entry.tags.split(","):

                tag = tag.strip()

                if tag:

                    tag_counter[tag] += 1

    # -----------------------------------
    # Timeline Events
    # -----------------------------------

    timeline = [

        entry

        for entry in entries

        if entry.is_timeline_event

    ]

    # -----------------------------------
    # Build Report
    # -----------------------------------

    report = {

        "person": person,

        # Statistics

        "entry_count": len(entries),

        "average_mood": average_mood,

        "first_mentioned": first_mentioned,

        "last_mentioned": last_mentioned,

        "average_relationship_score": average_relationship_score,

        "best_day": best_day,

        "worst_day": worst_day,

        "days_since_last_mention": days_since_last_mention,

        # Charts

        "mood_labels": mood_labels,

        "mood_values": mood_values,

        # Lists

        "top_tags": tag_counter.most_common(5),

        "keywords": [],

        "recent_entries": entries[::-1][:5],

        "timeline": timeline,

        # AI

        "ai_summary": None

    }

    print(report)

    return report