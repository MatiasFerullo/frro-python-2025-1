from flask import Blueprint, render_template


index_bp = Blueprint('index', __name__)

@index_bp.route('/')
def index():
    loggedIn = True
    if (loggedIn):
        return render_template('dashboard.html')
    return render_template('index.html')