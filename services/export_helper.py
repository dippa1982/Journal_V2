from datetime import datetime

from models import Entry

from constants.moods import MOODS
from constants.ai_prompt import AI_Prompt
def build_markdown(user):

    entries = (
        Entry.query
        .filter_by(user_id=user.id)
        .order_by(Entry.created_at.asc())
        .all()
    )

    markdown = AI_Prompt

    for entry in entries:

        markdown += f"""

## {entry.created_at.strftime('%A %d %B %Y %H:%M')}

Mood: {MOODS.get(entry.mood_score)}

Tags: {entry.tags or "None"}

{entry.content}

---

"""

    filename = datetime.now().strftime(
        "journal_%Y-%m-%d_%H-%M.md"
    )

    return markdown, filename