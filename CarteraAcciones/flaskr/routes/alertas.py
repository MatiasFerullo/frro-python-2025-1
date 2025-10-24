from flask import Blueprint, render_template, request, redirect, url_for, session
from flaskr import db
from flaskr.services.htmx_service import htmx_redirect, htmx_show_error_trigger

alertas_bp = Blueprint('alertas', __name__)

# POST de form de alerta con parametro type 1, 2 o 3
@alertas_bp.route('/create-alert', methods=['POST'])
def create_alert():
    user_id = session.get('user_id')
    type_ = request.args.get('type')
    if not user_id or not type_ or type_ not in ["1", "2", "3"]:
        print("No hay user logueado o type invalido")
        return htmx_redirect(url_for('index.index'))
    
    from flaskr.models import Usuario
    user = Usuario.query.filter_by(id=user_id).first()
    if not user:
        return htmx_redirect(url_for('index.index'))
    
    data = request.form
    alertas = user.alertas

    match type_:
        case "1":
            # print(data['element_id']) # ID del futuro
            # print(data['type']) # Tiene como valor "min" o "max"
            # print(data['price']) # Precio
            from flaskr.models import Alerta, AlertaPrecio, Accion

            element_id_f1 = int(data['element_id'])
            type_f1 = data['type']
            price_f1 = data['price']
            
            accion = Accion.query.filter_by(id=data['element_id']).first()
            if not accion:
                return htmx_show_error_trigger("Acción no encontrada.")
            
            for alerta in alertas:
                if alerta.alertas_precio and alerta.alertas_precio[0].accion_id == element_id_f1 and alerta.alertas_precio[0].tipo == type_f1:
                    return htmx_show_error_trigger("Ya tienes una alerta de este tipo para la acción seleccionada.")

            alerta = Alerta(user_id=user_id)
            alerta_precio = AlertaPrecio(
                alerta=alerta,
                accion_id=element_id_f1,
                tipo=type_f1,
                precio=price_f1
            )
            db.session.add(alerta)
            db.session.add(alerta_precio)
            db.session.commit()
        case "2":
            # print(data['element']) # Tiene como valor "portfolio" o el ID de UsuarioAccion
            # print(data['trigger']) # Tiene como valor "gain" o "loss"
            # print(data['percentage']) # Porcentage [1% ; 100%]

            from flaskr.models import Alerta, AlertaRendimiento

            is_portafolio = data['element'] == 'portfolio'
            usuario_accion_id = None if is_portafolio else int(data['element'])
            porcentaje = int(data['percentage'])
            disparador = data['trigger']

            for alerta in alertas:
                if alerta.alertas_rendimiento:
                    if is_portafolio and alerta.alertas_rendimiento[0].is_portafolio:
                        return htmx_show_error_trigger("Ya tienes una alerta de portafolio configurada.")
                    elif alerta.alertas_rendimiento[0].usuario_accion_id == usuario_accion_id and alerta.alertas_rendimiento[0].disparador == disparador:
                        return htmx_show_error_trigger("Ya tienes una alerta de rendimiento para esta acción en tu portafolio.")
            alerta = Alerta(user_id=user_id)
            
            alerta_rendimiento = AlertaRendimiento(
                alerta=alerta,
                usuario_accion_id=usuario_accion_id,
                is_portafolio=is_portafolio,
                porcentaje=porcentaje,
                disparador=disparador
            )
            db.session.add(alerta)
            db.session.add(alerta_rendimiento)
            db.session.commit()
        case "3":
            # print(data['threshold']) # Umbral de variación [0.01 ; 0.99]

            from flaskr.models import Alerta, AlertaPortafolio


            for alerta in alertas:
                if alerta.alertas_portafolio:
                    return htmx_show_error_trigger("Ya tienes una alerta de portafolio configurada.")

            alerta = Alerta(user_id=user_id)
            alerta_portafolio = AlertaPortafolio(
                alerta=alerta,
                variacion=data['threshold']
            )
            db.session.add(alerta)
            db.session.add(alerta_portafolio)
            db.session.commit()
    
    alertas = user.alertas

    return render_template('htmx/alert-list.html', alertas=alertas)

@alertas_bp.route('/get-user-alerts', methods=['GET'])
def get_user_alerts():
    if 'user_id' not in session:
        return htmx_redirect(url_for('index.index'))
    
    user_id = session['user_id']
    from flaskr.models import Usuario
    user = Usuario.query.filter_by(id=user_id).first()

    return render_template('htmx/alert-list.html', alertas=user.alertas)

@alertas_bp.route('/delete-alert/<int:alerta_id>', methods=['DELETE'])
def delete_alert(alerta_id):
    if 'user_id' not in session:
        return htmx_redirect(url_for('index.index'))
    
    user_id = session['user_id']
    from flaskr.models import Alerta
    alerta = Alerta.query.filter_by(id=alerta_id, user_id=user_id).first()
    if not alerta:
        return htmx_show_error_trigger("Alerta no encontrada o no tienes permiso para eliminarla.")
    
    db.session.delete(alerta)
    db.session.commit()
    from flaskr.models import Usuario
    user = Usuario.query.filter_by(id=user_id).first()
    return render_template('htmx/alert-list.html', alertas=user.alertas)