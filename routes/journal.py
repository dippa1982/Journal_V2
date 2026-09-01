from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from services.journal_helper import (get_all_entries,
    create_entry,
    get_entry,
    update_entry,
    delete_entry as delete_entry_service,
    search_entries,
    )

from models import Entry, db

from constants.moods import MOODS

from models.people import Person

from services.entry_analysis_service import analyse_entry

journal_bp = Blueprint(
    "journal",
    __name__
)

@journal_bp.route("/journal")
@login_required
def journal():

    entries = get_all_entries(current_user)

    return render_template(
        "journal.html",
        entries=entries,
        moods = MOODS
    )

@journal_bp.route("/journal/new", methods=["GET", "POST"])
@login_required
def new_entry():

    people = (
            Person.query
            .filter_by(user_id=current_user.id, active=True)
            .order_by(Person.name)
            .all()
            )

    if request.method == "POST":

        entry = create_entry(
            current_user,
            request.form
        )

        try:

            analyse_entry(entry)

        except Exception as e:

            db.session.rollback()

            print(
                f"Analysis failed for entry "
                f"{entry.id}: {e}"
            )

        flash(
            "Journal entry saved.",
            "success"
        )

        return redirect(
            url_for("journal.journal")        
        )

@journal_bp.route("/journal/<int:entry_id>")
@login_required
def view_entry(entry_id):
    entry = get_entry(entry_id, current_user)

    return render_template(
        "view_entry.html",
        entry=entry,
        moods = MOODS
    )

@journal_bp.route("/journal/<int:entry_id>/edit", methods=["GET", "POST"])
@login_required
def edit_entry(entry_id):

    entry = get_entry(
        entry_id,
        current_user
    )

    if request.method == "POST":

        update_entry(
            entry,
            request.form
        )

        try:

            analyse_entry(entry)

        except Exception as e:

            db.session.rollback()

            print(
                f"Re-analysis failed for entry "
                f"{entry.id}: {e}"
            )

        flash(
            "Journal entry updated.",
            "success"
        )

        return redirect(
            url_for(
                "journal.view_entry",
                entry_id=entry.id
            )
        )

@journal_bp.route("/journal/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete_entry(entry_id):
    entry = get_entry(entry_id, current_user)

    delete_entry_service(entry)

    flash("Journal entry deleted.",
          "success")

    return redirect(url_for("journal.journal"))

@journal_bp.route("/journal/search")
@login_required
def search():

    search_text = request.args.get(
        "q",
        ""
    ).strip()

    entries = search_entries(
        current_user,
        search_text
    )

    return render_template(
        "search_results.html",
        entries=entries,
        search_text=search_text,
        moods = MOODS
    )

@journal_bp.route(
    "/journal/<int:entry_id>/analyse"
)
@login_required
def analyse_journal_entry(entry_id):

    entry = Entry.query.filter_by(
        id=entry_id,
        user_id=current_user.id
    ).first_or_404()

    analysis = analyse_entry(entry)

    return {
        "message": "Entry analysed successfully.",
        "entry_id": entry.id,
        "analysis_id": analysis.id
    }