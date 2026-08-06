from flask import Blueprint
from sqlalchemy import text

from extensions import db


admin_bp = Blueprint(
    "admin",
    __name__
)


@admin_bp.route("/admin/stamp-db")
def stamp_db():

    NEW_REVISION = "b593f917dc2e"

    try:

        # Does the alembic table exist?

        db.session.execute(
            text(
                "SELECT version_num FROM alembic_version"
            )
        )

    except Exception:

        # Create it if missing

        db.session.execute(
            text(
                """
                CREATE TABLE alembic_version (
                    version_num VARCHAR(32)
                    NOT NULL PRIMARY KEY
                )
                """
            )
        )

        db.session.execute(
            text(
                """
                INSERT INTO alembic_version
                (version_num)

                VALUES (:revision)
                """
            ),
            {
                "revision": NEW_REVISION
            }
        )

        db.session.commit()

        return (
            f"Created alembic_version "
            f"with revision {NEW_REVISION}"
        )

    # Table exists

    db.session.execute(
        text(
            """
            UPDATE alembic_version

            SET version_num = :revision
            """
        ),
        {
            "revision": NEW_REVISION
        }
    )

    db.session.commit()

    return (
        f"Stamped database to "
        f"{NEW_REVISION}"
    )