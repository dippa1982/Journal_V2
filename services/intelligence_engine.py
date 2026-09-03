import json

from models import Entry, EntryAnalysis

def load_json(value):

    if not value:
        return []

    try:
        data = json.loads(value)

        if isinstance(data, list):
            return data

        return []

    except (json.JSONDecodeError, TypeError):
        return []

def build_intelligence(user):

    analyses = (
        EntryAnalysis.query
        .join(Entry)
        .filter(Entry.user_id == user.id)
        .order_by(Entry.created_at.asc())
        .all()
    )

    intelligence_report = {
    "emotions": [],
    "topics": [],
    "triggers": [],
    "behaviours": [],
    "needs": [],
    "beliefs": [],
    "positive_changes": [],
    "trends": [],
    }

    if not analyses:
        return intelligence_report

    # ---------------------------------------------------------
    # EMOTIONS
    # ---------------------------------------------------------

    emotion_data = {}

    for analysis in analyses:

        emotions = load_json(analysis.emotions)

        for emotion in emotions:

            if not isinstance(emotion, dict):
                continue

            name = emotion.get("name")

            if not name:
                continue

            intensity = emotion.get("intensity", 0)

            try:

                intensity = int(intensity)

            except (ValueError, TypeError):

                intensity = 0

            if name not in emotion_data:
                emotion_data[name] = {
                    "name": name,
                    "mentions": 0,
                    "total_intensity": 0,
                    "intensities": [],
                }

            emotion_data[name]["mentions"] += 1
            emotion_data[name]["total_intensity"] += intensity
            emotion_data[name]["intensities"].append(intensity)

    for emotion in emotion_data.values():

        mentions = emotion["mentions"]
        average_intensity = emotion["total_intensity"] / mentions if mentions else 0
        intelligence_report["emotions"].append({
            "name": emotion["name"],
            "mentions": mentions,
            "average_intensity": round(average_intensity, 1)
        })

    intelligence_report["emotions"].sort(key=lambda x: x["mentions"], reverse=True)

    # ---------------------------------------------------------
    # TRIGGERS
    # ---------------------------------------------------------

    trigger_data = {}

    for analysis in analyses:

        triggers = load_json(analysis.triggers)

        for trigger in triggers:

            if not isinstance(trigger, str):
                continue

            trigger = trigger.strip()

            if not trigger:
                continue

            key = trigger.lower()

            if key not in trigger_data:
                trigger_data[key] = {
                    "trigger": trigger,
                    "mentions": 0,
                }

            trigger_data[key]["mentions"] += 1

    intelligence_report["triggers"] = sorted(
        trigger_data.values(),
        key=lambda x: x["mentions"],
        reverse=True
    )

    # ---------------------------------------------------------
    # BEHAVIOURS
    # ---------------------------------------------------------

    behaviour_data = {}

    for analysis in analyses:

        behaviours = load_json(analysis.behaviours)

        for behaviour in behaviours:

            if not isinstance(behaviour, str):
                continue

            behaviour = behaviour.strip()

            if not behaviour:
                continue

            key = behaviour.lower()

            if key not in behaviour_data:
                behaviour_data[key] = {
                    "behaviour": behaviour,
                    "mentions": 0,
                }

            behaviour_data[key]["mentions"] += 1

    intelligence_report["behaviours"] = sorted(
        behaviour_data.values(),
        key=lambda x: x["mentions"],
        reverse=True
    )


    # ---------------------------------------------------------
    # TOPICS
    # ---------------------------------------------------------
    
    topic_data = {}

    for analysis in analyses:
        topics = load_json(analysis.topics)

        for topic in topics:
            if not isinstance(topic, str):
                continue

            topic = topic.strip()

            if not topic:
                continue

            key = topic.lower()

            if key not in topic_data:
                topic_data[key] = {
                    "topic": topic,
                    "mentions": 0
                }

            topic_data[key]["mentions"] += 1

    intelligence_report["topics"] = sorted(
        topic_data.values(),
        key=lambda x: x["mentions"],
        reverse=True
    )

    # ---------------------------------------------------------
    # NEEDS
    # ---------------------------------------------------------

    need_data = {}

    for analysis in analyses:
        needs = load_json(analysis.needs)

        for need in needs:
            if not isinstance(need, str):
                continue

            need = need.strip()

            if not need:
                continue

            key = need.lower()

            if key not in need_data:
                need_data[key] = {
                    "need": need,
                    "mentions": 0
                }

            need_data[key]["mentions"] += 1

    intelligence_report["needs"] = sorted(
        need_data.values(),
        key=lambda x: x["mentions"],
        reverse=True
    )

    # ---------------------------------------------------------
    # BELIEFS
    # ---------------------------------------------------------
    belief_data = {}

    for analysis in analyses:
        beliefs = load_json(analysis.beliefs)

        for belief in beliefs:
            if not isinstance(belief, str):
                continue

            belief = belief.strip()

            if not belief:
                continue

            key = belief.lower()

            if key not in belief_data:
                belief_data[key] = {
                    "belief": belief,
                    "mentions": 0
                }

            belief_data[key]["mentions"] += 1

    intelligence_report["beliefs"] = sorted(
        belief_data.values(),
        key=lambda x: x["mentions"],
        reverse=True
    )
    
    return intelligence_report

    
