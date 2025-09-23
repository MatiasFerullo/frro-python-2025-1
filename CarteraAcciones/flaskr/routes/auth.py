from flaskr.services.message_service import render_message
from flask import Blueprint, redirect, render_template, request, jsonify, url_for, session
from flaskr.models import User
from flaskr.services.fake_db import users

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register')
def registerPage():
    if (session.get('user_id')):
        return redirect(url_for('index.index'))
    return render_template('register.html')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.form
    username = data['username']
    email = data['email']
    password = data['password']
    password_repeat = data['password_repeat']

    if any(u.username == username for u in users):
        return render_message(
            "Error en el registro",
            "El nombre de usuario ya existe. Por favor, elige otro nombre de usuario.",
            "Volver",
            url_for('auth.registerPage'))

    if any(u.email == email for u in users):
        return render_message(
            "Error en el registro",
            "El correo electrónico ya está registrado. Por favor, usa otro correo o inicia sesión.",
            "Volver",
            url_for('auth.registerPage'))

    new_user = User(
        id=0,
        username=username,
        email=email,
        password=password
    )
    users.append(new_user)

    session['user_id'] = new_user.id
    return redirect(url_for('index.index'))

@auth_bp.route('/login')
def loginPage():
    if (session.get('user_id')):
        return redirect(url_for('index.index'))
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.form
    username = data['username']
    password = data['password']
    
    user = next((u for u in users if u.username == username and u.password == password), None)
    
    if user:
        session['user_id'] = user.id
        return redirect(url_for('index.index'))
    return render_message(
        "Credenciales inválidas",
        "El usuario o contraseña son incorrectos.",
        "Volver",
        url_for('auth.loginPage'))

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index.index'))

@auth_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u.id == user_id), None)
    if user:
        return jsonify(user.to_dict()), 200
    return jsonify({'message': 'Usuario no encontrado'}), 404

@auth_bp.route('/users', methods=['GET'])
def list_users():
    return jsonify([user.to_dict() for user in users]), 200
