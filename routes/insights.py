from flask import (
    Blueprint,
    render_template
)

from flask_login import (
    login_required,
    current_user
)

from services.insights_helper import get_insights

insights_bp = Blueprint(
    "insights",
    __name__
)
@insights_bp.route("/insights")
@login_required
def insights():

    insights = get_insights(current_user)

    return render_template(
        "insights.html",
        **insights
    )
