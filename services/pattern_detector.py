from collections import Counter,defaultdict

import re

from models import Entry

from constants.stop_words import STOP_WORDS
from constants.topic_keyword import TOPIC_KEYWORDS

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

    patterns = []

    report = {
        #done
        "emotional_patterns": [],
        #done
        "topic_patterns": [],
        #done
        "relationship_patterns":patterns,
        #done
        "mood_patterns": mood_patterns,
        #done
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


    all_moods = mood_patterns["values"]

    if all_moods:

        mood_patterns["average"] = round(
            sum(all_moods) / len(all_moods),
            1
        )

        mood_patterns["lowest"] = min(all_moods)

        mood_patterns["highest"] = max(all_moods)


    # =================================
    # Compare recent vs previous moods
    # =================================

    recent = all_moods[:7]

    previous = all_moods[7:14]


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

        relationship_moods = [
            entry.mood_score
            for entry in relationship_patterns
            if entry.mood_score is not None
        ]

        average_mood = round(
        sum(relationship_moods) / len(relationship_moods),
        1)

        trend = "stable"

        if len(relationship_moods) >= 4:
            midpoint = len(relationship_moods) // 2
            ealier_moods = relationship_moods[:midpoint]
            recent_moods = relationship_moods[midpoint:]
            ealier_average = sum(ealier_moods) / len(ealier_moods)
            recent_average = sum(recent_moods) / len(recent_moods)
            difference = recent_average - ealier_average

            if difference > 1:
                trend = "upwards"
            elif difference < -1:
                trend = "downwards"

        patterns.append({
            "person": person.name,

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

    report["relationship_patterns"] = patterns

    # =================================
    # Detect Emotional Patterns
    # =================================

    emotional_patterns = []

    if len(all_moods) >= 3:

        average = mood_patterns["average"]

        # -----------------------------
        # Overall emotional state
        # -----------------------------

        if average > 7:

            emotional_patterns.append("Your overall mood has been positive")

        elif average >= 5:
            emotional_patterns.append("Your overall mood has generally been mixed or moderate.")

        else:

            emotional_patterns.append("Your overall mood has been negative.")

        # -----------------------------
        # Recent emotional state
        # -----------------------------

        changes = []

        for i in range(1, len(all_moods)):
            changes.append(abs(all_moods[i] - all_moods[i - 1]))

        average_change = sum(changes) / len(changes)

        if average_change >= 2:
            emotional_patterns.append("Your mood shows noticeable emotional swings between entries.")

        elif average_change <= 0.75:
            emotional_patterns.append("Your mood has been relatively stable across entries")

        else:
            emotional_patterns.append(
                "Your mood changes moderately between entries."
            )

        # -----------------------------
        # Recent emotional direction
        # -----------------------------

        if mood_patterns["trend"] == "Mood is trending upwards":

            emotional_patterns.append(
                "Your more recent entries suggest an improvement in emotional state."
            )

        elif mood_patterns["trend"] == "Mood is trending downwards":

            emotional_patterns.append(
                "Your more recent entries suggest a decline in emotional state."
            )


        # -----------------------------
        # Repeated lower moods
        # -----------------------------

        low_mood_entries = [
            mood for mood in all_moods
            if mood <= 4
        ]

        if len(low_mood_entries) >= 3:

            percentage = (
                len(low_mood_entries) / len(all_moods)
            ) * 100

            if percentage >= 40:

                emotional_patterns.append(
                    "Lower moods appear regularly rather than being isolated events."
                )


        # -----------------------------
        # Repeated higher moods
        # -----------------------------

        high_mood_entries = [
            mood for mood in all_moods
            if mood >= 7
        ]

        if len(high_mood_entries) >= 3:

            percentage = (
                len(high_mood_entries) / len(all_moods)
            ) * 100

            if percentage >= 40:

                emotional_patterns.append(
                    "Higher moods appear regularly across your journal entries."
                )


        # -----------------------------
        # Large emotional swings
        # -----------------------------

        large_changes = [
            changes[i]
            for i in range(len(changes))
            if changes[i] >= 3
        ]

        if len(large_changes) >= 2:

            emotional_patterns.append(
                "There are repeated significant changes in mood between entries."
            )

    report["emotional_patterns"] = emotional_patterns

    # =================================
    # Detect Topic Patterns
    # =================================     

    topic_entries = defaultdict(list)

    for entry in entries:

        if not entry.content:
            continue

        text = entry.content.lower()

        for topic, keywords in TOPIC_KEYWORDS.items():
            matched_keywords = [
            keyword
            for keyword in keywords
            if re.search(
                r"\b" + re.escape(keyword) + r"\b",
                text
            )
        ]

            if matched_keywords:
                topic_entries[topic].append({
                    "entry": entry,
                    "keywords": matched_keywords
                })

    topic_patterns = []

    for topic, matches in topic_entries.items():

        if len(matches) < 2:
            continue

        topic_moods = [
        match["entry"].mood_score
        for match in matches
        if match["entry"].mood_score is not None
        ]

        if topic_moods:

            average_mood = round(
                sum(topic_moods) / len(topic_moods),
                1
            )

        else:

            average_mood = None


        all_keywords = []

        for match in matches:
            all_keywords.extend(match["keywords"])


        keyword_counts = Counter(all_keywords)


        topic_patterns.append({

            "topic": topic,

            "mentions": len(matches),

            "average_mood": average_mood,

            "keywords": [
                keyword
                for keyword, count
                in keyword_counts.most_common(5)
            ]

        })


    topic_patterns.sort(
        key=lambda topic: topic["mentions"],
        reverse=True
    )


    report["topic_patterns"] = topic_patterns 

    overall_average = mood_patterns["average"]

    for pattern in topic_patterns:

        if pattern["average_mood"] is not None:

            pattern["mood_difference"] = round(
                pattern["average_mood"] - overall_average,
                1
            )

        else:

            pattern["mood_difference"] = None

    return report