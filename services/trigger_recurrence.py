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

    recurring_triggers = []

    for key, data in trigger_data.items():

        entry_count = len(data["entries"])

        recurring_triggers.append({
            "trigger": key,
            "mentions": entry_count,
            "raw_triggers": sorted(data["raw_triggers"])
        })

    recurring_triggers.sort(
        key=lambda item: item["mentions"],
        reverse=True
    )

    return recurring_triggers