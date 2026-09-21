from extensions import db

# --------------------------------------------------
# Many-to-Many table
# --------------------------------------------------

entry_people = db.Table(

    "entry_people",

    db.Column(
        "entry_id",
        db.Integer,
        db.ForeignKey("entry.id"),
        primary_key=True
    ),

    db.Column(
        "person_id",
        db.Integer,
        db.ForeignKey("person.id"),
        primary_key=True
    )

)


# --------------------------------------------------
# Person
# --------------------------------------------------

class Person(db.Model):

    __tablename__ = "person"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    emoji = db.Column(
        db.String(10),
        default="🙂"
    )

    colour = db.Column(
        db.String(20),
        default="#6d5dfc"
    )

    relationship_type = db.Column(
        db.String(30),
        default="Other"
    )

    notes = db.Column(
        db.Text
    )

    favourite = db.Column(
        db.Boolean,
        default=False
    )

    active = db.Column(
        db.Boolean,
        default=True
    )

    entries = db.relationship(
    "Entry",
    secondary=entry_people,
    back_populates="people"
)