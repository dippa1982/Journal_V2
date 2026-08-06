from extensions import db

class Reflection(db.Model):
    
    title = db.Column(
    db.String(100),
    nullable=False,
    default="AI Reflection")

    id = db.Column(db.Integer, primary_key=True)
    
    created_at = (db.Column(db.DateTime, nullable=True, default=db.func.current_timestamp()))

    summary = db.Column(db.Text, nullable=True)

    strengths = db.Column(db.Text, nullable=True)

    blind_spots = db.Column(db.Text, nullable=True)

    relationship_patterns = db.Column(db.Text, nullable=True)

    emotional_patterns = db.Column(db.Text, nullable=True)

    therapy_topics = db.Column(db.Text, nullable=True)

    next_week = db.Column(db.Text, nullable=True)

    next_month = db.Column(db.Text, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

