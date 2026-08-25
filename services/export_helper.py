from datetime import datetime

from models import Entry
from constants.moods import MOODS
from constants.ai_prompt import ai_prompt_export


def build_markdown(user):
    entries = (
        Entry.query
        .filter_by(user_id=user.id)
        .order_by(Entry.created_at.desc())
        .limit(7)
        .all()
    )

    reflection_prompt = ai_prompt_export("") or ""

    markdown = "# Journal Export\n\n"

    if reflection_prompt.strip():
        markdown += "## AI Reflection Prompt\n\n"
        markdown += reflection_prompt.strip()
        markdown += "\n\n---\n\n"

    markdown += "## Journal Entries\n\n"
    print(markdown)

    for entry in entries:
        mood = MOODS.get(entry.mood_score, {})
        mood_name = mood.get("name", "Unknown") if isinstance(mood, dict) else str(mood)

        markdown += f"""### {entry.created_at.strftime('%A %d %B %Y %H:%M')}

**Mood:** {mood_name}

**Tags:** {entry.tags or "None"}

{entry.content or ""}

---

"""

    filename = datetime.now().strftime("journal_%Y-%m-%d_%H-%M.md")
    return markdown, filename
