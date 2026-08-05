from datetime import date

import json
import os

from google import genai

from extensions import db
from models import Entry, Reflection, DailyCompass

from constants.moods import MOODS


MODEL_NAME = "gemini-2.5-flash"


# ---------------------------------------------------
# Gemini
# ---------------------------------------------------

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ---------------------------------------------------
# Journal
# ---------------------------------------------------

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


# ---------------------------------------------------
# Build journal text
# ---------------------------------------------------

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


# ---------------------------------------------------
# Prompt
# ---------------------------------------------------

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
You are writing today's Daily Compass.

Your audience is a man recovering from childhood trauma,
trying to become calmer, emotionally stronger,
and more self-aware.

Your job is NOT motivation.

Avoid clichés.

Avoid sounding like a life coach.

Avoid praise unless the journal supports it.

Base every sentence on the journal.

Never invent events.

Return valid JSON only.

Use EXACTLY this structure.

{{
    "title":"Today's Direction",
    "icon":"🌱",
    "observation":"",
    "focus":"",
    "question":"",
    "confidence":"High"
}}

Journal

{journal}

Reflection

{reflection_text}
"""


# ---------------------------------------------------
# Gemini
# ---------------------------------------------------

def ask_ai(prompt):

    try:

        response = client.models.generate_content(

             model=MODEL_NAME,

             contents=prompt

    )

        return response.text.strip()

    except Exception as error:

        print("GEMINI ERROR:")
        print(repr(error))


# ---------------------------------------------------
# Parse JSON
# ---------------------------------------------------

def parse_response(result):

    try:

        return json.loads(result)

    except Exception:

        return {

            "title": "Today's Direction",

            "icon": "🌱",

            "observation": result,

            "focus": "",

            "question": "",

            "confidence": "Low"

        }


# ---------------------------------------------------
# Daily Compass
# ---------------------------------------------------

def generate_daily_compass(user):

    today = date.today()

    existing = DailyCompass.query.filter_by(

        user_id=user.id,

        compass_date=today

    ).first()

    if existing:

        return {

            "title": existing.title,

            "icon": existing.icon,

            "observation": existing.observation,

            "focus": existing.focus,

            "question": existing.question,

            "confidence": existing.confidence

        }

    entries = get_recent_entries(user)

    reflection = get_latest_reflection(user)

    journal = build_journal(entries)

    prompt = build_prompt(

        journal,

        reflection

    )

    result = ask_ai(prompt)

    compass = parse_response(result)

    db_compass = DailyCompass(

        user_id=user.id,

        compass_date=today,

        title=compass["title"],

        icon=compass["icon"],

        observation=compass["observation"],

        focus=compass["focus"],

        question=compass["question"],

        confidence=compass["confidence"]

    )

    db.session.add(db_compass)

    db.session.commit()

    return compass