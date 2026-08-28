from flask import Blueprint, render_template

from flask_login import (
    login_required,
    current_user
)

from services.dashboard_helper import get_dashboard_stats
from services.trend_engine import build_trend_report
from services.pattern_detector import detect_patterns
from services.daily_compass_helper import generate_daily_compass

from models import TherapyQuestion


dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():

    stats = get_dashboard_stats(current_user)

    trends = build_trend_report(current_user)

    patterns = detect_patterns(current_user)

    compass = generate_daily_compass(current_user)

    unanswered_questions = TherapyQuestion.query.filter_by(
        user_id=current_user.id,
        answered=False
    ).order_by(
        TherapyQuestion.created_at.desc()
    ).all()


    return render_template(

        "dashboard.html",
        **stats,
        trends=trends,
        patterns=patterns,
        compass=compass,
        unanswered_questions=unanswered_questions)