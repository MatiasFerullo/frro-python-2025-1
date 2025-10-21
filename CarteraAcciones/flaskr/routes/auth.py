from flaskr.services.message_service import render_message
from flask import Blueprint, redirect, render_template, request, jsonify, url_for, session
from flaskr.models import Usuario, db  # ← Importar db para usar la base de datos

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

    # Verificar si el usuario ya existe en la BASE DE DATOS
    existing_user = Usuario.query.filter_by(username=username).first()
    if existing_user:
        return render_message(
            "Error en el registro",
            "El nombre de usuario ya existe. Por favor, elige otro nombre de usuario.",
            "Volver",
            url_for('auth.registerPage'))

    # Verificar si el email ya existe en la BASE DE DATOS
    existing_email = Usuario.query.filter_by(email=email).first()
    if existing_email:
        return render_message(
            "Error en el registro",
            "El correo electrónico ya está registrado. Por favor, usa otro correo o inicia sesión.",
            "Volver",
            url_for('auth.registerPage'))

    # Crear nuevo usuario en la BASE DE DATOS
    new_user = Usuario(
        username=username,
        email=email,
        password=password  # En producción, esto debería estar encriptado
    )
    
    db.session.add(new_user)
    db.session.commit()

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
    
    # Buscar usuario en la BASE DE DATOS
    user = Usuario.query.filter_by(username=username, password=password).first()
    
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
    # Buscar usuario en la BASE DE DATOS
    user = Usuario.query.get(user_id)
    if user:
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email
        }), 200
    return jsonify({'message': 'Usuario no encontrado'}), 404

@auth_bp.route('/users', methods=['GET'])
def list_users():
    # Obtener todos los usuarios de la BASE DE DATOS
    users = Usuario.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'email': user.email
    } for user in users]), 200
