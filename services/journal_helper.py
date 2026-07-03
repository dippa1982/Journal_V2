from datetime import datetime
from sqlalchemy import or_
from extensions import db
from models import Entry


def get_all_entries(user):

    return (
        Entry.query
        .filter_by(user_id=user.id)
        .order_by(Entry.created_at.desc())
        .all()
    )


def get_entry(entry_id, user):

    return Entry.query.filter_by(
        id=entry_id,
        user_id=user.id
    ).first_or_404()


def create_entry(user, form):

    entry = Entry(
        mood_score=int(form["mood_score"]),
        tags=form["tags"].strip(),
        content=form["content"].strip(),
        user_id=user.id,
        created_at=datetime.utcnow()
    )

    db.session.add(entry)
    db.session.commit()

    return entry


def update_entry(entry, form):

    entry.mood_score = int(form["mood_score"])
    entry.tags = form["tags"].strip()
    entry.content = form["content"].strip()

    db.session.commit()


def delete_entry(entry):

    db.session.delete(entry)

    db.session.commit()


def search_entries(user, search_text):

    if not search_text:

        return []

    return (
        Entry.query
        .filter(
            Entry.user_id == user.id,
            or_(
                Entry.content.ilike(f"%{search_text}%"),
                Entry.tags.ilike(f"%{search_text}%")
            )
        )
        .order_by(Entry.created_at.desc())
        .all()
    )