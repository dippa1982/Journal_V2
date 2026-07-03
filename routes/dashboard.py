from flask import (
    Blueprint,
    render_template,
    request,
)

from services.dashboard_helper import get_dashboard_stats

from flask_login import (
    login_required,
    current_user
)

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():

    stats = get_dashboard_stats(current_user)

    return render_template(
        "dashboard.html",**stats
    )
