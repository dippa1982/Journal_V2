from flask import Blueprint, render_template
from flask_login import login_required, current_user

from services.trend_engine import build_trend_report

trends_bp = Blueprint(
    "trends",
    __name__
)

@trends_bp.route("/trends")
@login_required
def trends():

    report = build_trend_report(current_user)

    return render_template(
        "trends.html",
        report = report
    )