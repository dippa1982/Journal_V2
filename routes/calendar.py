from flask import (
    Blueprint,
    render_template
)

from flask_login import (
    login_required,
    current_user
)

from services.calendar_helper import get_calendar_data

calendar_bp = Blueprint(
    "calendar",
    __name__
)

@calendar_bp.route("/calendar")
@login_required
def calendar():

    calendar_data = get_calendar_data(current_user)

    return render_template(
        "calendar.html",
        **calendar_data
    )