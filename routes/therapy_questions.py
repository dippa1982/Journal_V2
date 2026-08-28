from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required, current_user

from extensions import db

from models import TherapyQuestion

from services.therapy_question_helper import extract_questions


therapy_questions_bp = Blueprint(
    "therapy_questions",
    __name__,
    url_prefix="/therapy-questions"
)


@therapy_questions_bp.route("/", methods=["GET", "POST"])
@login_required
def therapy_questions():

    questions = []

    if request.method == "POST":

        conversation = request.form.get(
            "conversation",
            ""
        ).strip()

        if not conversation:

            flash(
                "Please paste a conversation first.",
                "warning"
            )

            return redirect(
                url_for(
                    "therapy_questions.therapy_questions"
                )
            )

        try:

            questions = extract_questions(
                conversation
            )

        except Exception as error:

            print(
                f"Therapy question extraction failed: {error}"
            )

            flash(
                "Unable to extract questions. Please try again.",
                "danger"
            )

    saved_questions = TherapyQuestion.query.filter_by(
        user_id=current_user.id
    ).order_by(
        TherapyQuestion.created_at.desc()
    ).all()

    return render_template(
        "therapy_questions.html",
        questions=questions,
        saved_questions=saved_questions
    )


@therapy_questions_bp.route("/save", methods=["POST"])
@login_required
def save_questions():

    selected_questions = request.form.getlist(
        "selected_questions"
    )

    if not selected_questions:

        flash(
            "No questions were selected.",
            "warning"
        )

        return redirect(
            url_for(
                "therapy_questions.therapy_questions"
            )
        )

    for question in selected_questions:

        question_data = None

        try:
            import json

            question_data = json.loads(question)

        except (json.JSONDecodeError, TypeError):

            continue

        therapy_question = TherapyQuestion(

            question=question_data.get(
                "question",
                ""
            ),

            context=question_data.get(
                "context"
            ),

            category=question_data.get(
                "category"
            ),

            user_id=current_user.id

        )

        db.session.add(
            therapy_question
        )

    db.session.commit()

    flash(
        "Selected therapy questions saved.",
        "success"
    )

    return redirect(
        url_for(
            "therapy_questions.therapy_questions"
        )
    )