from extensions import db

from datetime import datetime


class DailyCompass(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    compass_date = db.Column(
    db.Date,
    nullable=False
    )

    title = db.Column(
        db.String(50)
    )

    icon = db.Column(
        db.String(10)
    )

    observation = db.Column(
        db.Text
    )

    focus = db.Column(
        db.Text
    )

    question = db.Column(
        db.Text
    )

    confidence = db.Column(
        db.String(20)
    )