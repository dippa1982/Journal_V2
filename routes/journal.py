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

from constants.moods import MOODS

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

    if request.method == "POST":

        create_entry(current_user, request.form)
        flash("Journal entry saved.",
              "success")

        return redirect(url_for("journal.journal"))
    
    return render_template(
        "new_entry.html",
        moods = MOODS
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

    return render_template(
        "edit_entry.html",
        entry=entry,
        moods = MOODS
    )

@journal_bp.route("/journal/<int:entry_id>/delete")
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