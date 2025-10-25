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
                return htmx_show_error_trigger("El futuro seleccionado no fue encontrado.")
            
            for alerta in alertas:
                if alerta.alertas_precio and alerta.alertas_precio[0].accion_id == element_id_f1 and alerta.alertas_precio[0].tipo == type_f1:
                    return htmx_show_error_trigger("Ya posee una alerta de este tipo para el futuro seleccionado.")

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
                    if is_portafolio and alerta.alertas_rendimiento[0].is_portafolio and alerta.alertas_rendimiento[0].disparador == disparador:
                        return htmx_show_error_trigger("Ya posee una alerta de este tipo para el portafolio completo.")
                    elif alerta.alertas_rendimiento[0].usuario_accion_id == usuario_accion_id and alerta.alertas_rendimiento[0].disparador == disparador:
                        return htmx_show_error_trigger("Ya posee una alerta de rendimiento de este tipo y futuro en su portafolio.")
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
                    return htmx_show_error_trigger("Ya posee una alerta de cambios súbitos configurada.")

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
        return htmx_show_error_trigger("La alerta no fue encontrada o no posee permisos para eliminarla.")
    
    db.session.delete(alerta)
    db.session.commit()
    from flaskr.models import Usuario
    user = Usuario.query.filter_by(id=user_id).first()
    return render_template('htmx/alert-list.html', alertas=user.alertas)

@alertas_bp.route('/edit-alert', methods=['PATCH'])
def edit_alert():
    user_id = session.get('user_id')
    if not user_id:
        print("No hay user logueado")
        return htmx_redirect(url_for('index.index'))
    
    from flaskr.models import Usuario, Alerta
    user = Usuario.query.filter_by(id=user_id).first()
    if not user:
        return htmx_redirect(url_for('index.index'))
    
    data = request.form
    alerta_id = int(data.get('usuario_accion_id'))
    
    alerta = Alerta.query.filter_by(id=alerta_id, user_id=user_id).first()
    if not alerta:
        return htmx_show_error_trigger("La alerta no fue encontrada o no posee permisos para editarla.")
    
    if alerta.alertas_precio:
        from flaskr.models import AlertaPrecio, Accion
        
        alerta_precio = alerta.alertas_precio[0]
        type_f1 = data['type']
        price_f1 = data['price']
        
        accion = Accion.query.filter_by(id=alerta_precio.accion_id).first()
        if not accion:
            return htmx_show_error_trigger("El futuro seleccionado no fue encontrado.")
        
        for alert in user.alertas:
            if alert.id != alerta_id and alert.alertas_precio:
                if (alert.alertas_precio[0].accion_id == alerta_precio.accion_id and 
                    alert.alertas_precio[0].tipo == type_f1):
                    return htmx_show_error_trigger("Ya posee una alerta de este tipo para el futuro seleccionado.")
        
        alerta_precio.tipo = type_f1
        alerta_precio.precio = price_f1
        db.session.commit()
        
    elif alerta.alertas_rendimiento:
        from flaskr.models import AlertaRendimiento
        
        alerta_rendimiento = alerta.alertas_rendimiento[0]
        porcentaje = int(data['percentage'])
        disparador = data['trigger']
        
        for alert in user.alertas:
            if alert.id != alerta_id and alert.alertas_rendimiento:
                if (alerta_rendimiento.is_portafolio and alert.alertas_rendimiento[0].is_portafolio and
                    alert.alertas_rendimiento[0].disparador == disparador):
                    return htmx_show_error_trigger("Ya posee una alerta con este disparador para el portafolio.")
                elif (alert.alertas_rendimiento[0].usuario_accion_id == alerta_rendimiento.usuario_accion_id and 
                      alert.alertas_rendimiento[0].disparador == disparador):
                    return htmx_show_error_trigger("Ya posee una alerta con este disparador para este futuro.")
        
        alerta_rendimiento.porcentaje = porcentaje
        alerta_rendimiento.disparador = disparador
        db.session.commit()
        
    elif alerta.alertas_portafolio:
        from flaskr.models import AlertaPortafolio
        
        alerta_portafolio = alerta.alertas_portafolio[0]
        
        for alert in user.alertas:
            if alert.id != alerta_id and alert.alertas_portafolio:
                return htmx_show_error_trigger("Ya posee una alerta de variación de portafolio configurada.")
        
        alerta_portafolio.variacion = data['threshold']
        db.session.commit()
    
    else:
        return htmx_show_error_trigger("El tipo de alerta no es reconocido.")
    
    alertas = user.alertas
    return render_template('htmx/alert-list.html', alertas=alertas)