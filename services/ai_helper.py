import os
import json
import time

from google import genai

from constants.ai_prompt import ai_prompt_reflection
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
        Entry.created_at.desc()
    ).limit(30).all()

    


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

    return ai_prompt_reflection(journal)   


def ask_ai(prompt):

    client = get_client()

    for attempt in range(3):

        try:

            response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
            "response_mime_type": "application/json"
            }
)

            result = response.text

            if not result:
                raise ValueError(
                    "Gemini returned an empty response."
                )

            return result

        except Exception as error:

            print(
                f"Gemini attempt {attempt + 1} failed: "
                f"{error}"
            )

            if attempt == 2:
                raise

            time.sleep(2 ** attempt)

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

        summary=data.get(
            "summary",
            "No summary generated."
        ),

        title=data.get(
        "title",
        "Journal Reflection"
        ),

        strengths=json.dumps(data.get("strengths",[])),

        blind_spots=json.dumps(data.get("blind_spots",[])),

        relationship_patterns=json.dumps(data.get("relationship_patterns",[])),

        emotional_patterns=json.dumps(data.get("emotional_patterns",[])),

        therapy_topics=json.dumps(data.get("therapy_topics",[])),

        next_week=data.get(
            "weekly_focus",
            "No weekly focus generated."
        ),

        next_month=data.get(
            "monthly_focus",
            "No monthly focus generated."
        ),

        concerns=json.dumps(data.get("concerns",[])),

        growth=json.dumps(data.get("growth",[])),

        practical_focus=json.dumps(data.get("practical_focus",[])),

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