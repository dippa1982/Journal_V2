from flask import Blueprint, render_template
from flask_login import login_required, current_user

from services.weekly_review_helper import (
    get_week_entries,
    build_review
)


weekly_review_bp = Blueprint(
    "weekly_review",
    __name__
)


@weekly_review_bp.route("/weekly-review")
@login_required
def weekly_review():

    entries = get_week_entries(current_user)

    weekly_report = build_review(entries)

    return render_template(
        "weekly_review.html",
        weekly_report=weekly_report
    )