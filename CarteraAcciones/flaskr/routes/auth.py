from flask import Blueprint, redirect, render_template, request, jsonify, url_for
from flaskr.models import User
from flaskr.services.fake_db import users

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register')
def registerPage():
    return render_template('register.html')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.form
    # if data['password_repeat'] == data['password']:
    new_user = User(
        id=0,
        username=data['username'],
        email=data['email'],
        password=data['password']
    )
    users.append(new_user)
    return redirect(url_for('index.index'))

@auth_bp.route('/login')
def loginPage():
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.form
    username = data['username']
    password = data['password']
    
    user = next((u for u in users if u.username == username and u.password == password), None)
    
    if user:
        return redirect(url_for('index.index'))
    return 'Credenciales inválidas'

@auth_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u.id == user_id), None)
    if user:
        return jsonify(user.to_dict()), 200
    return jsonify({'message': 'Usuario no encontrado'}), 404

@auth_bp.route('/users', methods=['GET'])
def list_users():
    return jsonify([user.to_dict() for user in users]), 200
