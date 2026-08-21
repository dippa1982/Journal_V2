from flask import Blueprint, render_template
from flask_login import login_required, current_user

from services.trend_engine import build_trend_report

from services.daily_compass_helper import generate_daily_compass

trends_bp = Blueprint(
    "trends",
    __name__
)

@trends_bp.route("/trends")
@login_required
def trends():

    report = build_trend_report(current_user)

    compass = generate_daily_compass(current_user)

    print("DAILY COMPASS RETURNED:")
    print(compass)

    return render_template(
        "trends.html",
        report = report,
        compass = compass
    )