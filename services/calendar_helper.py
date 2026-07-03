from calendar import monthcalendar
from datetime import datetime

from models import Entry


def get_calendar_data(user):

    today = datetime.today()

    month = today.month
    year = today.year

    weeks = monthcalendar(year, month)

    entries = Entry.query.filter_by(
        user_id=user.id
    ).all()

    entry_lookup = {}

    for entry in entries:

        if (
            entry.created_at.month == month and
            entry.created_at.year == year
        ):

            entry_lookup[
                entry.created_at.day
            ] = entry

    return {
        "weeks": weeks,
        "month": month,
        "year": year,
        "entry_lookup": entry_lookup
    }