from flask import Blueprint, redirect, render_template, url_for, session


index_bp = Blueprint('index', __name__)

@index_bp.route('/')
def index():
    loggedIn = session.get('user_id') is not None
    if (loggedIn):
        return render_template('dashboard.html')
    return render_template('index.html')

@index_bp.route('/alerts')
def alerts():
    loggedIn = session.get('user_id') is not None
    if (loggedIn):
        return render_template('alerts.html')
    return redirect(url_for('index.index'))

@index_bp.route('/portfolio')
def portfolio():
    loggedIn = session.get('user_id') is not None
    if (loggedIn):
        return render_template('portfolio.html')
    return redirect(url_for('index.index'))

@index_bp.route('/chart')
def chart():
    loggedIn = session.get('user_id') is not None
    if (loggedIn):
        return render_template('chart.html')
    return redirect(url_for('index.index'))

@index_bp.route('/stock-form')
def stockForm():
    loggedIn = session.get('user_id') is not None
    if (loggedIn):
        return render_template('stock-form.html')
    return redirect(url_for('index.index'))
