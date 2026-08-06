print("Compass blueprint loaded")

from flask import (
    Blueprint,
    jsonify
)

from flask_login import (
    login_required,
    current_user
)

from services.daily_compass_helper import generate_daily_compass

compass_bp = Blueprint(
    "compass",
    __name__
)


@compass_bp.route("/compass")
@login_required
def compass_test():

    compass = generate_daily_compass(current_user)

    return jsonify(compass)