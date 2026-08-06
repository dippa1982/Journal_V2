from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for
)

from flask_login import (
    login_required,
    current_user
)

from services.calendar_helper import get_calendar_data

settings_bp = Blueprint(
    "settings",
    __name__
)
from services.settings_helper import change_password

@settings_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():

    if request.method == "POST":

        success, message = change_password(

            current_user,

            request.form["current_password"],

            request.form["new_password"],

            request.form["confirm_password"]

        )

        flash(
            message,
            "success" if success else "danger"
        )

        return redirect(
            url_for("settings.settings")
        )

    return render_template(
        "settings.html"
    )