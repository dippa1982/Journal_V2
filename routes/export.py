from flask import (
    Blueprint,
    Response
)

from flask_login import (
    login_required,
    current_user
)

from services.export_helper import (
    build_markdown
)

export_bp = Blueprint(
    "export",
    __name__
)

@export_bp.route("/export-markdown")
@login_required
def export_markdown():

    markdown, filename = build_markdown(
        current_user
    )

    return Response(

        markdown,

        mimetype="text/markdown",

        headers={

            "Content-Disposition":

            f"attachment; filename={filename}"

        }

    )