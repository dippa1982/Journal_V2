from models import Entry, Reflection

from google import genai

from datetime import date

from models import DailyCompass

import os

import json

from constants.moods import MOODS

MODEL_NAME = "gemini-2.5-flash"

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def get_client():

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is missing."
        )

    return genai.Client(
        api_key=api_key
    )

def get_recent_entries(user):

    return (
        Entry.query
        .filter_by(user_id=user.id)
        .order_by(Entry.created_at.desc())
        .limit(30)
        .all()
    )

def get_latest_reflection(user):

    return (
        Reflection.query
        .filter_by(user_id=user.id)
        .order_by(Reflection.created_at.desc())
        .first()
    )

def build_journal(entries):

    journal = ""

    for entry in entries:

        journal += f"""
Date:
{entry.created_at.strftime("%d %B %Y")}

Mood:
{MOODS[entry.mood_score]["emoji"]} {MOODS[entry.mood_score]["name"]}

Tags:
{entry.tags or "None"}

Entry:
{entry.content}
"""
    return journal

def build_prompt(journal, reflection):

    reflection_text = ""

    if reflection:

        reflection_text = f"""
Latest Reflection

Summary:
{reflection.summary}

Blind Spots:
{reflection.blind_spots}

Strengths:
{reflection.strengths}
"""

    return f"""
You are writing a Daily Compass for the owner of this journal.

The goal is NOT motivation.

The goal is honest encouragement.

Use the journal entries and reflection below.

Write:

A short observation.

One practical focus for today.

One thoughtful question.

Maximum 150 words.

Do not exaggerate.

Do not flatter.

Be warm, calm and supportive.

Do not sound like a motivational speaker.

Do not use clichés.

Do not say "you've got this".

Do not praise the user unless there is evidence in the journal.

Base every observation on the journal entries provided.

Never invent events that are not present.

Return valid JSON only.

Use exactly this structure:

{{
    "title": "Today's Direction",
    "icon": "🌱",
    "observation": "",
    "focus": "",
    "question": "",
    "confidence": ""
}}

The icon must be a single emoji.

The title must be short (2-4 words).

Return JSON only.

Do not use Markdown.

JOURNAL ENTRIES:

{journal}

REFLECTION:

{reflection_text}

"""

def ask_ai(prompt):

    client = get_client()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text

def generate_daily_compass(user):

    entries = get_recent_entries(user)

    reflection = get_latest_reflection(user)

    journal = build_journal(entries)

    prompt = build_prompt(
        journal,
        reflection
    )

    result = ask_ai(prompt).strip()

    try:

        return json.loads(result)

    except json.JSONDecodeError:

        return {
            "title": "Today's Direction",
            "icon": "🌱",
            "observation": result,
            "focus": "",
            "question": ""
        }