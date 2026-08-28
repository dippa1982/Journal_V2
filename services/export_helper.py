from datetime import datetime

from models import Entry, TherapyQuestion
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

    therapy_questions = (
        TherapyQuestion.query
        .filter_by(user_id=user.id)
        .order_by(TherapyQuestion.created_at.desc())
        .all()
    )

    journal = "\n\n".join(
        (entry.content or "").strip()
        for entry in entries
    )

    reflection_prompt = ai_prompt_export(journal) or ""

    markdown = "# Journal Export\n\n"

    # =================================
    # AI Reflection Prompt
    # =================================

    if reflection_prompt.strip():

        markdown += "## AI Reflection Prompt\n\n"

        markdown += reflection_prompt.strip()

        markdown += "\n\n---\n\n"


    # =================================
    # Journal Entries
    # =================================

    markdown += "## Journal Entries\n\n"

    for entry in entries:

        mood = MOODS.get(entry.mood_score, {})

        mood_name = (
            mood.get("name", "Unknown")
            if isinstance(mood, dict)
            else str(mood)
        )

        markdown += f"""### {entry.created_at.strftime('%A %d %B %Y %H:%M')}

**Mood:** {mood_name}

**Tags:** {entry.tags or "None"}

{entry.content or ""}

---

"""


    # =================================
    # Therapy Questions
    # =================================

    if therapy_questions:

        markdown += "## Therapy Questions\n\n"


        # ---------------------------------
        # Answered Questions
        # ---------------------------------

        answered_questions = [
            question
            for question in therapy_questions
            if question.answered
        ]

        if answered_questions:

            markdown += "### Answered\n\n"

            for question in answered_questions:

                markdown += f"#### {question.question}\n\n"


                if question.category:

                    markdown += (
                        f"**Category:** "
                        f"{question.category}\n\n"
                    )


                if question.context:

                    markdown += (
                        f"**Context:** "
                        f"{question.context}\n\n"
                    )


                markdown += "**Answer:**\n\n"

                markdown += (
                    f"{question.answer or 'No answer recorded.'}\n\n"
                )


                if question.answered_at:

                    markdown += (
                        f"**Answered:** "
                        f"{question.answered_at.strftime('%d %B %Y')}\n\n"
                    )


                markdown += "---\n\n"


        # ---------------------------------
        # Unanswered Questions
        # ---------------------------------

        unanswered_questions = [
            question
            for question in therapy_questions
            if not question.answered
        ]

        if unanswered_questions:

            markdown += "### Unanswered\n\n"

            for question in unanswered_questions:

                markdown += f"#### {question.question}\n\n"


                if question.category:

                    markdown += (
                        f"**Category:** "
                        f"{question.category}\n\n"
                    )


                if question.context:

                    markdown += (
                        f"**Context:** "
                        f"{question.context}\n\n"
                    )


                markdown += "---\n\n"


    filename = datetime.now().strftime(
        "journal_%Y-%m-%d_%H-%M.md"
    )

    return markdown, filename