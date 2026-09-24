from flask import (
    Blueprint,
    render_template
)

from flask_login import (
    login_required,
    current_user
)

from services.intelligence_engine import build_intelligence

from services.insights_helper import get_insights

from services.pattern_detector import detect_patterns

from constants.moods import MOODS

insights_bp = Blueprint(
    "insights",
    __name__
)
@insights_bp.route("/insights")
@login_required
def insights():

    insights = get_insights(current_user)

    #intelligence = build_intelligence(current_user)

    intelligence = {
    "patterns": [
        {
            "type": "repeated_emotional_association",
            "trigger": "Nicola's explanation of the Roy incident, including her statement about someone grabbing her",
            "emotion": "anger",
            "entry_ids": [48, 50],
            "entry_count": 2
        },
        {
            "type": "repeated_emotional_association",
            "trigger": "Nicola's explanation of the Roy incident, including her statement about someone grabbing her",
            "emotion": "distress",
            "entry_ids": [48, 50],
            "entry_count": 2
        }
    ]
}

    report = detect_patterns(current_user)

    return render_template(
        "insights.html",
        moods = MOODS,
        intelligence = intelligence,
        report = report,
        **insights
    )
