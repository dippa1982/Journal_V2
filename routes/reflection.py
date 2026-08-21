import json

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request
)

from flask_login import (
    login_required,
    current_user
)

from models import Reflection

from services.ai_helper import (
    generate_reflection
)

reflection_bp = Blueprint(
    "reflection",
    __name__
)


def prepare_reflection(reflection):

    list_fields = [
        "strengths",
        "blind_spots",
        "relationship_patterns",
        "emotional_patterns",
        "therapy_topics",
        "concerns",
        "growth",
        "practical_focus",
    ]

    for field in list_fields:

        value = getattr(reflection, field, None)

        if value:
            try:
                setattr(
                    reflection,
                    field,
                    json.loads(value)
                )
            except (json.JSONDecodeError, TypeError):
                setattr(
                    reflection,
                    field,
                    []
                )
        else:
            setattr(
                reflection,
                field,
                [])

    return reflection

@reflection_bp.route(
    "/reflection",
    methods=["GET", "POST"]
)
@login_required
def reflection():

    if request.method == "POST":

        try:

            generate_reflection(current_user)

            flash(
                "AI Reflection generated successfully."
            )

        except Exception as e:

            flash(
                f"Reflection failed: {e}"
            )

        return redirect(
            url_for("reflection.reflection")
        )

    latest_reflection = Reflection.query.filter_by(
    user_id=current_user.id
    ).order_by(
    Reflection.created_at.desc()
    ).first()

    if latest_reflection:
        latest_reflection = prepare_reflection(
        latest_reflection
    )

    return render_template(
        "ai_reflection.html",
        reflection=latest_reflection
    )