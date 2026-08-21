def ai_prompt_reflection(journal):
    AI_Prompt_Reflection = f"""

    # AI Reflection Request

    Please analyse these journal entries.

    Focus specifically on:

    - Relationship patterns
    - Assumptions versus evidence
    - Evidence collected for emotions
    - Emotional regulation
    - Progress over time
    - Situations where I may be catastrophising or mind-reading
    - Situations where my concerns appear well-founded

    Do not simply validate my perspective.

    Identify strengths.

    Identify blind spots.

    Provide practical advice.

    ---
    JOURNAL ENTRIES:

    {journal}

    """
    return AI_Prompt_Reflection

def ai_prompt_compass(compass):

    AI_Prompt_Compass = f"""

# Daily Compass Request

Analyse the personal journal entries below.

Provide a balanced and thoughtful daily compass.

Do not simply validate the writer's perspective.

Distinguish between:

- facts and assumptions
- evidence and interpretations
- reasonable concerns and catastrophising
- recurring patterns and isolated incidents

Look specifically for:

- emotional patterns
- relationship patterns
- strengths
- blind spots
- evidence of progress
- what deserves attention today
- one practical focus for today
- one useful reflection question

Return valid JSON containing exactly these fields:

{{
    "title": "string",
    "icon": "emoji",
    "observation": "string",
    "focus": "string",
    "question": "string",
    "confidence": "string"
}}

Return JSON only.

Do not use Markdown code fences.

JOURNAL ENTRIES:

{compass}

"""

    return AI_Prompt_Compass