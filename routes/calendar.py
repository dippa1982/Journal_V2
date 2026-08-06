from datetime import datetime
import calendar as Cal

from flask import (
    Blueprint,
    render_template,
    request
)

from flask_login import (
    login_required,
    current_user
)

from models import Entry
from constants.moods import MOODS

calendar_bp = Blueprint(
    "calendar",
    __name__
)


@calendar_bp.route("/calendar")
@login_required
def calendar():

    # ----------------------------
    # Get month/year from URL
    # ----------------------------

    today = datetime.today()

    year = request.args.get(
        "year",
        default=today.year,
        type=int
    )

    month = request.args.get(
        "month",
        default=today.month,
        type=int
    )

    # ----------------------------
    # Calendar
    # ----------------------------

    calender_obj = Cal.Calendar(firstweekday=0)

    weeks = calender_obj.monthdayscalendar(year, month)

    # ----------------------------
    # Entries for this month
    # ----------------------------

    entries = Entry.query.filter_by(
        user_id=current_user.id
    ).all()

    entry_lookup = {}

    for entry in entries:

        if (
            entry.created_at.year == year
            and
            entry.created_at.month == month
        ):

            entry_lookup[entry.created_at.day] = entry

    # ----------------------------
    # Previous month
    # ----------------------------

    if month == 1:

        previous_month = 12
        previous_year = year - 1

    else:

        previous_month = month - 1
        previous_year = year

    # ----------------------------
    # Next month
    # ----------------------------

    if month == 12:

        next_month = 1
        next_year = year + 1

    else:

        next_month = month + 1
        next_year = year

    # ----------------------------
    # Render
    # ----------------------------

    return render_template(

    "calendar.html",

    month=Cal.month_name[month],
    year=year,

    weeks=weeks,

    entry_lookup=entry_lookup,

    moods=MOODS,

    previous_month=previous_month,
    previous_year=previous_year,

    next_month=next_month,
    next_year=next_year

)