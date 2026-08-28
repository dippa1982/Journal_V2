from datetime import datetime

from extensions import db

class TherapyQuestion(db.Model):

    __tablename__ = "therapy_question"

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    context = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    answered = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    answer = db.Column(db.Text,nullable=True)
    answered_at = db.Column(db.DateTime,nullable=True)

