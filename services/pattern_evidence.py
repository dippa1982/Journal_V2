def build_pattern_evidence(trigger_emotion_relationships):
    """
    Summarise the emotional consistency of recurring triggers.

    This is evidence gathering only.
    It does not interpret or explain why emotions occurred.
    """

    results = []

    for relationship in trigger_emotion_relationships:

        trigger = relationship["trigger"]
        trigger_mentions = relationship["trigger_mentions"]
        emotions = relationship["emotions"]

        repeated_emotions = []
        variable_emotions = []

        for emotion in emotions:

            if emotion["mentions"] >= 2:
                repeated_emotions.append({
                    "emotion": emotion["emotion"],
                    "mentions": emotion["mentions"],
                    "entry_ids": emotion["entry_ids"]
                })

            else:
                variable_emotions.append({
                    "emotion": emotion["emotion"],
                    "mentions": emotion["mentions"],
                    "entry_ids": emotion["entry_ids"]
                })

        results.append({
            "trigger": trigger,
            "trigger_mentions": trigger_mentions,
            "repeated_emotions": repeated_emotions,
            "variable_emotions": variable_emotions
        })

    return results