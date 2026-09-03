import json
import os

from google import genai


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


def build_prompt(conversation):

    return f"""
You are helping a person identify useful therapeutic and
self-reflection questions from a conversation.

The conversation below is between the user and an AI assistant.

Your job is to extract ONLY questions that the AI assistant
asked the user that could genuinely be useful for:

- personal reflection
- understanding emotions
- understanding behaviour
- understanding relationships
- understanding personal patterns
- exploring beliefs or assumptions
- identifying fears or needs
- discussing something further in therapy

Do NOT extract:

- questions asked by the user
- rhetorical questions
- questions that are simply part of normal conversation
- questions asking for clarification
- questions about technical problems
- questions that have no meaningful reflective value

Preserve the meaning of the original question.

You may lightly rewrite a question to make it clearer and
more suitable as a standalone journal reflection question.

Do not invent questions that were not present in the conversation.

For each useful question, provide:

- question
- context
- category

The context should briefly explain what the question appears
to be exploring.

The category should be a short useful label such as:

- Emotions
- Relationships
- Self-understanding
- Behaviour
- Fear
- Needs
- Boundaries
- Personal growth
- Therapy

IMPORTANT:

Return ONLY valid JSON.

Do not use Markdown.
Do not use ```json.
Do not write anything before or after the JSON.

Use exactly this structure:

{{
    "questions": [
        {{
            "question": "The question",
            "context": "What this question is exploring",
            "category": "Category"
        }}
    ]
}}

Rules:

- Every value must be valid JSON.
- Strings must use double quotes.
- Do not include trailing commas.
- If no useful questions are found, return:
  {{
      "questions": []
  }}
- Do not invent information.

CONVERSATION:

{conversation}
"""


def extract_questions(conversation):

    if not conversation or not conversation.strip():
        return []

    prompt = build_prompt(conversation)

    client = get_client()

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

    try:

        data = json.loads(result)

    except json.JSONDecodeError as error:

        print("INVALID THERAPY QUESTION JSON:")
        print(repr(result))

        raise ValueError(
            f"Gemini returned invalid JSON: {error}"
        )

    questions = data.get("questions", [])

    if not isinstance(questions, list):
        raise ValueError(
            "Gemini returned an invalid questions structure."
        )

    return questions