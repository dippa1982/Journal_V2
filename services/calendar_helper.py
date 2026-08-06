from calendar import monthcalendar
from datetime import datetime

from models import Entry

def get_calendar_data(user):

    current = datetime(year, month, 1)

    month = current.month
    year = current.year

    first_day = current.replace(day=1)

    previous_month = first_day - datetime.timedelta(days=1)

    next_month = (first_day.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)

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
        "previous_month": previous_month,
        "next_month": next_month,
        "entry_lookup": entry_lookup
    }