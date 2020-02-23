from flask import Blueprint

bp = Blueprint('parse', __name__)

from app.parse import jobs
