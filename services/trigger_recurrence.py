from collections import defaultdict


def build_trigger_recurrence(normalised_records):
    """
    Group normalised triggers and count how many
    distinct journal entries each trigger appears in.
    """

    trigger_data = defaultdict(lambda: {
        "entries": set(),
        "raw_triggers": set()
    })

    for record in normalised_records:
        normalised = record.get("normalised")
        entry_id = record.get("entry_id")
        raw = record.get("raw")

        if not normalised or not entry_id:
            continue

        key = normalised.strip().lower()

        trigger_data[key]["entries"].add(entry_id)

        if raw:
            trigger_data[key]["raw_triggers"].add(raw)

    all_triggers = []

    for key, data in trigger_data.items():

        entry_count = len(data["entries"])

        all_triggers.append({
            "trigger": key,
            "mentions": entry_count,
            "entry_ids": sorted(data["entries"]),
            "raw_triggers": sorted(data["raw_triggers"])
        })

    all_triggers.sort(
        key=lambda item: item["mentions"],
        reverse=True
    )

    recurring_triggers = [
        trigger
        for trigger in all_triggers
        if trigger["mentions"] >= 2
    ]

    return {
        "all": all_triggers,
        "recurring": recurring_triggers
    }