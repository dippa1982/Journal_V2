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
    """