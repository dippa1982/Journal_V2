from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models import Entry

from services.entry_analysis_service import analyse_entry

analyse_bp = Blueprint(
    "analyse",
    __name__
)
@analyse_bp.route(
    "/journal/<int:entry_id>/analyse"
)
@login_required
def analyse_journal_entry(entry_id):

    entry = Entry.query.filter_by(
        id=entry_id,
        user_id=current_user.id
    ).first_or_404()

    analysis = analyse_entry(entry)

    return analysis