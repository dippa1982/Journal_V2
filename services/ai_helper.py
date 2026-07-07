import os
import json

from google import genai

from extensions import db
from models import Entry, Reflection


MODEL_NAME = "gemini-2.5-flash"


def get_client():

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is missing."
        )

    return genai.Client(
        api_key=api_key
    )


def get_entries(user):

    return Entry.query.filter_by(
        user_id=user.id
    ).order_by(
        Entry.created_at.asc()
    ).all()


def build_journal(entries):

    journal_parts = []

    for entry in entries:

        journal_parts.append(
            f"""
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
        )

    return "\n".join(journal_parts)


def build_prompt(journal):

    return f"""
Analyse the personal journal entries below.

Provide a balanced and thoughtful reflection.

Do not simply validate the writer's perspective.

Distinguish between:

- facts and assumptions
- evidence and interpretations
- reasonable concerns and catastrophising
- recurring patterns and isolated incidents

Look specifically for:

- strengths
- blind spots
- relationship patterns
- emotional patterns
- evidence of progress
- useful topics to discuss in therapy
- practical focus for the next week
- practical focus for the next month

Return valid JSON containing exactly these fields:

{{
    "summary": "string",
    "strengths": "string",
    "blind_spots": "string",
    "relationship_patterns": "string",
    "emotional_patterns": "string",
    "therapy_topics": "string",
    "next_week": "string",
    "next_month": "string"
}}

Return JSON only.

Do not use Markdown code fences.

JOURNAL ENTRIES:

{journal}
"""


def ask_ai(prompt):

    client = get_client()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    result = response.text

    print("RAW GEMINI RESPONSE:")
    print(repr(result))

    if not result:
        raise ValueError(
            "Gemini returned an empty response."
        )

    return result


def parse_ai_response(result):

    cleaned_result = result.strip()

    # Remove Markdown JSON fences if Gemini adds them

    if cleaned_result.startswith("```json"):
        cleaned_result = cleaned_result[7:]

    elif cleaned_result.startswith("```"):
        cleaned_result = cleaned_result[3:]

    if cleaned_result.endswith("```"):
        cleaned_result = cleaned_result[:-3]

    cleaned_result = cleaned_result.strip()

    try:

        return json.loads(cleaned_result)

    except json.JSONDecodeError as error:

        print("INVALID GEMINI JSON:")
        print(repr(cleaned_result))

        raise ValueError(
            f"Gemini returned invalid JSON: {error}"
        )


def save_reflection(user, data):

    reflection = Reflection(

        model=MODEL_NAME,

        summary=data.get(
            "summary",
            "No summary generated."
        ),

        strengths=data.get(
            "strengths",
            "No strengths generated."
        ),

        blind_spots=data.get(
            "blind_spots",
            "No blind spots generated."
        ),

        relationship_patterns=data.get(
            "relationship_patterns",
            "No relationship patterns generated."
        ),

        emotional_patterns=data.get(
            "emotional_patterns",
            "No emotional patterns generated."
        ),

        therapy_topics=data.get(
            "therapy_topics",
            "No therapy topics generated."
        ),

        next_week=data.get(
            "next_week",
            "No weekly focus generated."
        ),

        next_month=data.get(
            "next_month",
            "No monthly focus generated."
        ),

        user_id=user.id

    )

    db.session.add(reflection)

    db.session.commit()

    return reflection


def generate_reflection(user):

    entries = get_entries(user)

    if not entries:

        raise ValueError(
            "You need at least one journal entry "
            "before generating a reflection."
        )

    journal = build_journal(entries)

    prompt = build_prompt(journal)

    result = ask_ai(prompt)

    data = parse_ai_response(result)

    reflection = save_reflection(
        user,
        data
    )

    return reflection