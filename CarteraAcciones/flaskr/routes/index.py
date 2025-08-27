from flask import Blueprint, redirect, render_template, url_for


index_bp = Blueprint('index', __name__)

@index_bp.route('/')
def index():
    loggedIn = True
    if (loggedIn):
        return render_template('dashboard.html')
    return render_template('index.html')

@index_bp.route('/alerts')
def alerts():
    loggedIn = True
    if (loggedIn):
        return render_template('alerts.html')
    return redirect(url_for('index.index'))

@index_bp.route('/portfolio')
def portfolio():
    loggedIn = True
    if (loggedIn):
        return render_template('portfolio.html')
    return redirect(url_for('index.index'))

@index_bp.route('/chart')
def chart():
    loggedIn = True
    if (loggedIn):
        return render_template('chart.html')
    return redirect(url_for('index.index'))

@index_bp.route('/stock-form')
def stockForm():
    loggedIn = True
    if (loggedIn):
        return render_template('stock-form.html')
    return redirect(url_for('index.index'))
