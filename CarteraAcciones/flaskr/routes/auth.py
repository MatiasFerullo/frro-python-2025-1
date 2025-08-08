from flask import Blueprint, request, jsonify
from flaskr.models import User
from flaskr.services.fake_db import users

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    new_user = User(
        id=data.get('id'),
        username=data.get('username'),
        email=data.get('email'),
        password=data.get('password')
    )
    users.append(new_user)
    return jsonify({'message': 'Usuario registrado exitosamente'}), 201
    


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = next((u for u in users if u.username == username and u.password == password), None)
    
    if user:
        return jsonify({'message': 'Login exitoso', 'user_id': user.id}), 200
    return jsonify({'message': 'Credenciales inválidas'}), 401

@auth_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u.id == user_id), None)
    if user:
        return jsonify(user.to_dict()), 200
    return jsonify({'message': 'Usuario no encontrado'}), 404

@auth_bp.route('/users', methods=['GET'])
def list_users():
    return jsonify([user.to_dict() for user in users]), 200
