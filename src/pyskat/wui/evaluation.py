from flask import (
    render_template,
    g,
    Blueprint,
)
from ..plugins import report_content

bp = Blueprint("evaluation", __name__, url_prefix="/evaluation")


@bp.get("/")
def index():
    return render_template("evaluation.html", report_content=report_content(g.backend, g.session))
