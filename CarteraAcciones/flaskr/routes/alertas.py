from flask import Blueprint, render_template, request, redirect, url_for, session

alertas_bp = Blueprint('alertas', __name__)

# POST de form de alerta con parametro type 1, 2 o 3
@alertas_bp.route('/create-alert', methods=['POST'])
def create_alert():
    user_id = session.get('user_id')
    type_ = request.args.get('type')
    if not user_id or not type_ or type_ not in ["1", "2", "3"]:
        print("No hay user logueado o type invalido")
        return redirect(url_for('index.index'))

    data = request.form

    match type_:
        case "1":
            print(data['element_id']) # ID del futuro
            print(data['type']) # Tiene como valor "min" o "max"
            print(data['price']) # Precio
        case "2":
            print(data['element']) # Tiene como valor "portfolio" o el ID de UsuarioAccion
            print(data['trigger']) # Tiene como valor "gain" o "loss"
            print(data['percentage']) # Porcentage [1% ; 100%]
        case "3":
            print(data['threshold']) # Umbral de variación [0.01 ; 0.99]
    
    # TODO: Registrar alerta

    # TODO: Obtener alertas que el usuario tiene configuradas
    
    alertas = []

    return render_template('htmx/alert-list.html', alertas=alertas)

@alertas_bp.route('/get-user-alerts', methods=['GET'])
def get_user_alerts():
    if 'user_id' not in session:
        return redirect(url_for('index.index'))
    
    user_id = session['user_id']
    from flaskr.models import Usuario
    user = Usuario.query.filter_by(id=user_id).first()

    # TODO: Obtener alertas que el usuario tiene configuradas
    
    alertas = []

    return render_template('htmx/alert-list.html', alertas=alertas)
