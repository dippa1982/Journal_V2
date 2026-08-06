from flask import Blueprint, render_template

from flask_login import login_required, current_user

from models import Entry

from constants.moods import MOODS

timeline_bp = Blueprint(
    "timeline",
    __name__
)


@timeline_bp.route("/timeline")
@login_required
def timeline():

    entries = (

        Entry.query

        .filter_by(

            user_id=current_user.id,

            is_timeline_event=True

        )

        .order_by(

            Entry.created_at.desc()

        )

        .all()

    )

    return render_template(

        "timeline.html",
        moods = MOODS,
        entries=entries

    )