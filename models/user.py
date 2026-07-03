from extensions import db
from flask_login import UserMixin

class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    display_name = db.Column(
    db.String(50),
    nullable=True
    )
    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    entries = db.relationship(
    "Entry",
    backref="author",
    lazy=True,
    cascade="all, delete-orphan"
)
    
    def __repr__(self):

        return f"<User {self.username}>"
