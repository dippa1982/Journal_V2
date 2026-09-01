from datetime import datetime

from extensions import db

class EntryAnalysis(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    entry_id = db.Column(
        db.Integer,
        db.ForeignKey("entry.id"),
        nullable=False,
        unique=True
    )

    emotions = db.Column(
        db.Text,
        nullable=True
    )

    topics = db.Column(
        db.Text,
        nullable=True
    )

    triggers = db.Column(
        db.Text,
        nullable=True
    )

    behaviours = db.Column(
        db.Text,
        nullable=True
    )

    needs = db.Column(
        db.Text,
        nullable=True
    )

    beliefs = db.Column(
        db.Text,
        nullable=True
    )

    positive_changes = db.Column(
        db.Text,
        nullable=True
    )

    possible_patterns = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )