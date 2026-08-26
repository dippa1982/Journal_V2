from collections import Counter,defaultdict

from models import Entry

def get_entries(user):

    return Entry.query.filter_by(
        user_id=user.id
    ).order_by(
        Entry.created_at.desc()
    ).all()


def detect_patterns(user):

    entries = get_entries(user)

    mood_patterns = {
        "values": [],
        "average": 0,
        "lowest": 0,
        "highest": 0,
        "recent_average": 0,
        "previous_average": 0,
        "change": 0,
        "trend": None,
    }

    report = {
        "emotional_patterns": [],
        "topic_patterns": [],
        "relationship_patterns":patterns,
        "mood_patterns": mood_patterns,
        "recurring_tags": [],
        "significant_changes": []
    }

    if not entries:
        return report


    # =================================
    # Detect recurring tags
    # =================================

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


    # =================================
    # Detect mood patterns
    # =================================

    for entry in entries:

        if entry.mood_score is not None:

            mood_patterns["values"].append(
                entry.mood_score
            )


    moods = mood_patterns["values"]


    if moods:

        mood_patterns["average"] = round(
            sum(moods) / len(moods),
            1
        )

        mood_patterns["lowest"] = min(moods)

        mood_patterns["highest"] = max(moods)


    # =================================
    # Compare recent vs previous moods
    # =================================

    recent = moods[:7]

    previous = moods[7:14]


    if recent and previous:

        recent_average = round(
            sum(recent) / len(recent),
            1
        )

        previous_average = round(
            sum(previous) / len(previous),
            1
        )

        change = round(
            recent_average - previous_average,
            1
        )


        mood_patterns["recent_average"] = recent_average

        mood_patterns["previous_average"] = previous_average

        mood_patterns["change"] = change


        if change > 1:

            mood_patterns["trend"] = "Mood is trending upwards"

        elif change < -1:

            mood_patterns["trend"] = "Mood is trending downwards"

        else:

            mood_patterns["trend"] = "Mood is stable"


    # =================================
    # Detect Relationship patterns
    # =================================

    relationship_patterns = defaultdict(list)

    for entry in entries:

        for person in entry.people:

            relationship_patterns[person].append(entry)

    patterns = []

    for person, relationship_patterns in relationship_patterns.items():

        relationship_patterns = sorted(relationship_patterns, key=lambda x: x.created_at)

        moods = [
            entry.mood_score
            for entry in relationship_patterns
            if entry.mood_score is not None
        ]

        average_mood = round(
        sum(moods) / len(moods),
        1)

        trend = "stable"

        if len(moods) >= 4:
            midpoint = len(moods) // 2
            ealier_moods = moods[:midpoint]
            recent_moods = moods[midpoint:]
            ealier_average = sum(ealier_moods) / len(ealier_moods)
            recent_avarage = sum(recent_moods) / len(recent_moods)
            difference = recent_average - ealier_average

            if difference > 1:
                trend = "upwards"
            elif difference < -1:
                trend = "downwards"

        patterns.append({
            "person": person,

            "mentions": len(relationship_patterns),

            "average_mood": average_mood,

            "first_mentioned": relationship_patterns[0].created_at,

            "last_mentioned": relationship_patterns[-1].created_at,

            "trend": trend
        })

    patterns.sort(
        key=lambda p: p["mentions"],
        reverse=True
    )

    return report