from flask import Blueprint
bp = Blueprint(__name__, 'home')

@bp.route('/')
def home():
    return 'Hello World!'
