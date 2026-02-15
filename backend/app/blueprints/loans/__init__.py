from flask import Blueprint

loans_bp = Blueprint("loans", __name__)

from . import routes  # noqa: E402,F401
