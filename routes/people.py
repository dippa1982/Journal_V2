from flask import (
    Blueprint,
    render_template
)

from flask_login import (
    login_required,
    current_user
)

from flask import redirect, url_for, flash, request
from extensions import db

from constants.moods import MOODS
from constants.people_emoji import PEOPLE_EMOJI

people_bp = Blueprint(
    "people",
    __name__
)

from models.people import Person

@people_bp.route("/people")
@login_required
def people():
    people = (
        Person.query
        .filter_by(user_id=current_user.id)
        .order_by(Person.name)
        .all()
    )

    return render_template(
        "people.html",
        people=people
    )

@people_bp.route("/people/new", methods=["GET", "POST"])
@login_required
def new_person():

    if request.method == "POST":

        selection = int(request.form["relationship_type"])

        person_info = PEOPLE_EMOJI[selection]

        person = Person(

            user_id=current_user.id,

            name=request.form["name"],

            relationship_type=person_info["name"],

            emoji=person_info["emoji"],

            colour=request.form["colour"],

            notes=request.form.get("notes", ""),

            favourite="favourite" in request.form

)

        db.session.add(person)

        db.session.commit()

        flash(
            "Person added successfully.",
            "success"
        )

        return redirect(
            url_for("people.people")
        )

    return render_template(
        "new_person.html",
        people_emojis=PEOPLE_EMOJI
    )

@people_bp.route("/people/<int:person_id>")
@login_required
def view_person(person_id):

    person = Person.query.filter_by(
        id=person_id,
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        "view_person.html",
        people_emoji = PEOPLE_EMOJI,
        person=person
    )

@people_bp.route("/people/<int:person_id>/edit", methods=["GET", "POST"])
@login_required
def edit_person(person_id):

    person = Person.query.filter_by(
        id=person_id,
        user_id=current_user.id
    ).first_or_404()

    if request.method == "POST":

        selection = int(request.form["relationship_type"])
        person_info = PEOPLE_EMOJI[selection]

        person.name = request.form["name"]
        person.relationship_type = person_info["name"]
        person.emoji = person_info["emoji"]
        person.colour = request.form["colour"]
        person.notes = request.form.get("notes", "")
        person.favourite = "favourite" in request.form
        person.active = "active" in request.form

        db.session.commit()

        flash(
            "Person updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "people.view_person",
                person_id=person.id
            )
        )

    return render_template(
        "edit_person.html",
        person=person,
        people_emojis=PEOPLE_EMOJI
    )

@people_bp.route("/people/<int:person_id>/delete", methods=["POST"])
@login_required
def delete_person(person_id):

    person = Person.query.filter_by(
        id=person_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(person)

    db.session.commit()

    flash(
        "Person deleted.",
        "success"
    )

    return redirect(
        url_for("people.people")
    )