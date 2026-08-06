from flask import Blueprint
from sqlalchemy import text
from extensions import db

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin/fix-db")
def fix_db():

    statements = [

        """
        ALTER TABLE entry
        ADD COLUMN IF NOT EXISTS is_timeline_event BOOLEAN DEFAULT FALSE;
        """,

        """
        ALTER TABLE entry
        ADD COLUMN IF NOT EXISTS relationship_score INTEGER DEFAULT 0;
        """

    ]

    for sql in statements:
        db.session.execute(text(sql))

    db.session.commit()

    return "Database updated!"