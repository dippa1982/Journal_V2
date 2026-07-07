from google import genai

from extensions import db

from models import Entry
from models import Reflection

import os
import json


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def get_entries(user):

    return Entry.query.filter_by(
        user_id=user.id
    ).order_by(
        Entry.created_at.asc()
    ).all()


def build_journal(entries):

    journal = ""

    for entry in entries:

        journal += f"""

Date:
{entry.created_at.strftime('%d %B %Y')}

Mood:
{entry.mood_score}

Tags:
{entry.tags or "None"}

Entry:
{entry.content}

-----------------------

"""

    return journal


def build_prompt(journal):

    return f"""
You are acting as a thoughtful psychological coach.

Do not simply agree with the writer.

Challenge assumptions where appropriate.

Look for:

Relationship patterns

Emotional triggers

Evidence vs assumptions

Cognitive distortions

Growth

Blind spots

Therapy topics

Focus for next week

Focus for next month

Return ONLY valid JSON.

Use exactly this format:

{{
"summary":"",
"strengths":"",
"blind_spots":"",
"relationship_patterns":"",
"emotional_patterns":"",
"therapy_topics":"",
"next_week":"",
"next_month":""
}}

Journal:

{journal}
"""


def ask_ai(prompt):

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


def save_reflection(user, result):

    data = json.loads(result)

    reflection = Reflection(

        model="gemini-2.5-flash",

        summary=data["summary"],

        strengths=data["strengths"],

        blind_spots=data["blind_spots"],

        relationship_patterns=data["relationship_patterns"],

        emotional_patterns=data["emotional_patterns"],

        therapy_topics=data["therapy_topics"],

        next_week=data["next_week"],

        next_month=data["next_month"],

        user_id=user.id

    )

    db.session.add(reflection)

    db.session.commit()

    return reflection


def generate_reflection(user):

    entries = get_entries(user)

    journal = build_journal(entries)

    prompt = build_prompt(journal)

    result = ask_ai(prompt)

    reflection = save_reflection(
        user,
        result
    )

    return reflection
