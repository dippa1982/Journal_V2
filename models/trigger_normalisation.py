from datetime import datetime

from extensions import db

class TriggerNormalisation(db.Model):
    __tablename__ = "trigger_normalisation"

    id = db.Column(db.Integer, primary_key=True)

    raw_trigger = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    normalised_trigger = db.Column(
        db.Text,
        nullable=False
    )

    confidence = db.Column(
        db.String(20),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )