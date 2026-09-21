from datetime import datetime

from extensions import db

from models.people import entry_people


class Entry(db.Model):

    __tablename__ = "entry"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    tags = db.Column(
        db.String(500),
        nullable=True
    )

    mood_score = db.Column(
        db.Integer,
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    is_timeline_event = db.Column(
    db.Boolean,
    default=False,
    nullable=False
    )

    people = db.relationship(

    "Person",

    secondary=entry_people,

    back_populates="entries"

    )

    relationship_score = db.Column(

    db.Integer

    )