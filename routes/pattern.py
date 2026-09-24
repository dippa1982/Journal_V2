from flask import Blueprint, render_template
from flask_login import login_required, current_user

from services.pattern_detector import detect_patterns

from services.intelligence_engine import build_intelligence

patterns_bp = Blueprint(
    "patterns",
    __name__
)

@patterns_bp.route("/patterns")
@login_required
def patterns():

    report = detect_patterns(current_user)

    intelligence = build_intelligence(current_user)

    return render_template(
        "patterns.html",
        report = report,
        intelligence = intelligence
    )