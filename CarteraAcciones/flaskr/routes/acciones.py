## ACA VAN LAS TODAS LAS RUTAS RELACIONADAS CON LAS ACCIONES
from collections import defaultdict
from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from datetime import datetime, timedelta
from flask import Blueprint, jsonify
from sqlalchemy import func
from flaskr.models import Accion, Precio_accion
from flaskr import db
from flaskr.services.htmx_service import htmx_redirect, htmx_show_error_trigger
from flaskr.services.pyrofex_service import get_active_futures 
from datetime import date



futuros_bp = Blueprint('futuros', __name__)

@futuros_bp.route('/cargar-futuros', methods=['POST'])
def cargar_futuros():
    try:
        print(" Paso 1: Obteniendo futuros de PyRofex...")
        futuros_api = get_active_futures()
        print(f"✅ Paso 1 OK: {len(futuros_api)} futuros obtenidos")

        print(" Paso 2: Verificando conexión a BD...")
        count_antes = Accion.query.count()
        print(f"✅ Paso 2 OK: BD conectada. Hay {count_antes} acciones")

        print(" Paso 3: Procesando futuros...")
        futuros_nuevos = []
        precios_nuevos = []

        for fut_data in futuros_api:
            symbol = fut_data['symbol']
            price = fut_data['price']

            # Verificar si el futuro ya existe
            accion_existente = Accion.query.filter_by(simbolo=symbol).first()

            if not accion_existente:
                # Crear nueva acción (en tu BD los futuros también van en tabla Accion)
                nueva_accion = Accion(
                    simbolo=symbol,
                    nombre=symbol  # Podés cambiar si querés un nombre más descriptivo
                )
                db.session.add(nueva_accion)
                db.session.flush()  # Para obtener el ID
                futuros_nuevos.append(nueva_accion)
                print(f" Nuevo futuro: {symbol} (ID: {nueva_accion.id})")
                accion_para_precio = nueva_accion
            else:
                accion_para_precio = accion_existente
                print(f" Futuro existente: {symbol} (ID: {accion_existente.id})")

            # Crear registro de precio
            if price is not None:
                nuevo_precio = Precio_accion(
                    accion_id=accion_para_precio.id,
                    precio=float(price),
                    fecha_hora=datetime.utcnow()
                )
                db.session.add(nuevo_precio)
                precios_nuevos.append(nuevo_precio)
                print(f"💰 Precio AGREGADO para {symbol}: ${price}")

        print(f"🔍 Paso 4: Guardando {len(futuros_nuevos)} futuros y {len(precios_nuevos)} precios...")
        db.session.commit()
        print("✅ Commit ejecutado")

        count_precios_despues = Precio_accion.query.count()
        mensaje = f'Se agregaron {len(futuros_nuevos)} nuevos futuros y {len(precios_nuevos)} precios'

        return jsonify({
            'mensaje': mensaje,
            'nuevos_futuros': len(futuros_nuevos),
            'nuevos_precios': len(precios_nuevos),
            'total_acciones': Accion.query.count(),
            'total_precios': count_precios_despues
        })

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        print(traceback.format_exc())
        db.session.rollback()
        print("✅ Rollback ejecutado")
        return jsonify({'error': str(e)}), 500
    

@futuros_bp.route('/acciones', methods=['GET'])
def listar_acciones():
    try:
        from flaskr.models import Accion
        
        acciones = Accion.query.all()
        resultado = []
        
        for accion in acciones:
            resultado.append({
                'id': accion.id,
                'simbolo': accion.simbolo,
                'nombre': accion.nombre,
                'precios_count': len(accion.precios) if hasattr(accion, 'precios') else 0
            })
        
        return jsonify({
            'total': len(resultado),
            'acciones': resultado
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_first_price(usuario_accion):
    from flaskr.models import Precio_accion

    return Precio_accion.query.filter(
        Precio_accion.accion_id == usuario_accion.accion_id,
        func.date(Precio_accion.fecha_hora) <= usuario_accion.fecha
    ).order_by(Precio_accion.fecha_hora.desc()).first()

def get_latest_price(usuario_accion):
    from flaskr.models import Precio_accion

    return Precio_accion.query.filter_by(accion_id=usuario_accion.accion_id).order_by(Precio_accion.fecha_hora.desc()).first()

def get_first_prices(user):
    first_prices = {}

    for usuario_accion in user.usuario_acciones:

        first_price_record = get_first_price(usuario_accion)

        if first_price_record:
            first_prices[usuario_accion.id] = first_price_record.precio
        else:
            first_prices[usuario_accion.id] = 0.0
    return first_prices

def get_latest_prices(user):
    latest_prices = {}

    for usuario_accion in user.usuario_acciones:
        latest_price_record = get_latest_price(usuario_accion)
        if latest_price_record:
            latest_prices[usuario_accion.id] = latest_price_record.precio
        else:
            latest_prices[usuario_accion.id] = 0.0
    return latest_prices

# Agregar una accion al portafolio del usuario (form de "Añadir accion" en /portfolio)
@futuros_bp.route('/new-portfolio-stock', methods=['POST'])
def add_stock_to_portfolio():
    if 'user_id' not in session:
        return htmx_redirect(url_for('index.index'))
    
    user_id = session['user_id']

    from flaskr.models import Accion, Usuario, UsuarioAccion, Precio_accion, db

    data = request.form
    fecha = data.get('fecha')
    accion_id = data['accion_id']
    cantidad = data['cantidad']

    if (UsuarioAccion.query.filter_by(accion_id=int(accion_id), user_id=int(user_id), fecha=fecha).first()):
        return htmx_show_error_trigger("Ya posee este futuro en la fecha seleccionada. Puede editarlo desde el portafolio.")

    first_ever_price = Precio_accion.query.filter_by(accion_id=int(accion_id)).order_by(func.date(Precio_accion.fecha_hora).asc()).first()
    if (first_ever_price.fecha_hora.date() > date.fromisoformat(fecha)):
        return htmx_show_error_trigger(f"No existen registros de precios anteriores al {first_ever_price.fecha_hora.date().strftime('%d/%m/%Y')} para este futuro.")

    accion = Accion.query.filter_by(id=accion_id).first()
    if not accion:
        return jsonify({'error': 'Acción no encontrada'}), 404

    nueva_usuario_accion = UsuarioAccion(
        user_id=user_id,
        accion_id=accion_id,
        fecha=fecha,
        cantidad=cantidad
    )

    try:
        db.session.add(nueva_usuario_accion)
        db.session.commit()
        user = Usuario.query.filter_by(id=user_id).first()

        first_prices = get_first_prices(user)
                
        return render_template('htmx/stock-list.html', usuario_acciones=user.usuario_acciones, first_prices=first_prices, view='edit')
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': "Couldn't persist db"}), 500

@futuros_bp.route('/get-user-stocks', methods=['GET'])
def get_user_stocks():
    if 'user_id' not in session:
        return htmx_redirect(url_for('index.index'))
    
    user_id = session['user_id']
    from flaskr.models import Usuario, Precio_accion
    user = Usuario.query.filter_by(id=user_id).first()
    view = request.args.get('view')
    if view == None or view == '' or view not in ['menu', 'edit']:
        view = 'menu'
    
    latest_prices = get_latest_prices(user)
    first_prices = get_first_prices(user)

    return render_template('htmx/stock-list.html', usuario_acciones=user.usuario_acciones, view=view, latest_prices=latest_prices, first_prices=first_prices)

@futuros_bp.route('/delete-user-stock/<int:usuario_accion_id>', methods=['DELETE'])
def delete_user_stock(usuario_accion_id):
    if 'user_id' not in session:
        return htmx_redirect(url_for('index.index'))
    
    user_id = session['user_id']
    from flaskr.models import UsuarioAccion, Usuario, db

    usuario_accion = UsuarioAccion.query.filter_by(id=usuario_accion_id, user_id=user_id).first()
    if not usuario_accion:
        return jsonify({'error': 'Registro no encontrado'}), 404

    try:
        for alerta_rendimiento in usuario_accion.alertas_rendimiento:
            db.session.delete(alerta_rendimiento.alerta)
        db.session.delete(usuario_accion)
        db.session.commit()
        user = Usuario.query.filter_by(id=user_id).first()

        first_prices = get_first_prices(user)

        return render_template('htmx/stock-list.html', usuario_acciones=user.usuario_acciones, view='edit', first_prices=first_prices)
    except Exception as e:
        print(str(e))
        db.session.rollback()
        return jsonify({'error': "Couldn't delete from db"}), 500

@futuros_bp.route('/get-available-stocks', methods=['GET'])
def get_available_stocks():
    try:
        from flaskr.models import Accion
        
        acciones = Accion.query.all()
        return render_template('htmx/available-stocks.html', acciones=acciones)
    except Exception as e:
        return jsonify({'error': "Couldn't get available stock"}), 500

@futuros_bp.route('/edit-portfolio-stock', methods=['PATCH'])
def edit_user_stock():
    if 'user_id' not in session:
        return htmx_redirect(url_for('index.index'))
    
    user_id = session['user_id']

    from flaskr.models import UsuarioAccion, Usuario, UsuarioAccion, Precio_accion, db

    data = request.form
    usuario_accion_id = data['usuario_accion_id']
    fecha = data.get('fecha')
    cantidad = data['cantidad']

    usuario_accion = UsuarioAccion.query.filter_by(id=usuario_accion_id).first()
    if not usuario_accion:
        return jsonify({'error': 'Acción del usuario no encontrada'}), 404

    conflict = UsuarioAccion.query.filter(
        UsuarioAccion.id != usuario_accion.id,
        UsuarioAccion.accion_id == usuario_accion.accion_id,
        UsuarioAccion.user_id == user_id,
        UsuarioAccion.fecha == fecha
    ).first()

    if conflict:
        return htmx_show_error_trigger("Ya posee un futuro del mismo tipo en la fecha seleccionada.")

    first_ever_price = Precio_accion.query.filter_by(accion_id=int(usuario_accion.accion_id)).order_by(func.date(Precio_accion.fecha_hora).asc()).first()
    if (first_ever_price.fecha_hora.date() > date.fromisoformat(fecha)):
        return htmx_show_error_trigger(f"No existen registros de precios anteriores al {first_ever_price.fecha_hora.date().strftime('%d/%m/%Y')} para este futuro.")

    usuario_accion.fecha = fecha
    usuario_accion.cantidad = cantidad

    try:
        db.session.commit()
        user = Usuario.query.filter_by(id=user_id).first()

        first_prices = get_first_prices(user)

        return render_template('htmx/stock-list.html', usuario_acciones=user.usuario_acciones, view='edit', first_prices=first_prices)
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': "Couldn't persist db"}), 500

@futuros_bp.route('/get-portfolio-summary', methods=['GET'])
def get_portfolio_summary():
    if 'user_id' not in session:
        return htmx_redirect(url_for('index.index'))
    
    user_id = session['user_id']
    from flaskr.models import Usuario, Precio_accion
    user = Usuario.query.filter_by(id=user_id).first()

    gain_sum = 0.0
    initial_investment = 0.0
    for usuario_accion in user.usuario_acciones:
        accion_id = usuario_accion.accion_id
        latest_price_record = Precio_accion.query.filter_by(accion_id=accion_id).order_by(Precio_accion.fecha_hora.desc()).first()
        if latest_price_record:
            latest_price = latest_price_record.precio
            gain_sum += (usuario_accion.cantidad * latest_price)
        first_price_record = Precio_accion.query.filter(
            Precio_accion.accion_id == usuario_accion.accion_id,
            func.date(Precio_accion.fecha_hora) <= usuario_accion.fecha
        ).order_by(Precio_accion.fecha_hora.desc()).first()
        if first_price_record:
            initial_investment += (usuario_accion.cantidad * first_price_record.precio)

    difference = gain_sum - initial_investment
    differencePercentage = 0.0
    if initial_investment != 0:
        differencePercentage = round((difference / initial_investment) * 100, 2)

    return render_template('htmx/portfolio-summary.html', gain_sum=gain_sum, difference=difference, differencePercentage=differencePercentage)

@futuros_bp.route('/portfolio-chart-data', methods=['GET'])
def portfolio_chart_data():
    if 'user_id' not in session:
        return redirect(url_for('index.index'))
    user_id = session['user_id']

    days = request.args.get('d')
    if not days or days not in ["7", "14", "21", "30", "60", "90", "180"]:
        days = "7"

    date_limit = date.today() - timedelta(days=int(days))

    from flaskr.models import Usuario, Precio_accion

    user = Usuario.query.filter_by(id=user_id).first()
    usuario_acciones = user.usuario_acciones
    sum_ = defaultdict(float)
    for usuario_accion in usuario_acciones:
        precios = Precio_accion.query.filter_by(accion_id=usuario_accion.accion_id).order_by(func.date(Precio_accion.fecha_hora).desc())
        for precio in precios:
            if precio.fecha_hora.date() >= date_limit:
                if precio.fecha_hora.date() >= usuario_accion.fecha:
                    fecha = precio.fecha_hora.date()
                    sum_[fecha] += round(precio.precio * usuario_accion.cantidad, 2)

    fechas_ordenadas = sorted(sum_.keys())

    data = {
        "labels": [fecha.strftime("%-d/%-m") for fecha in fechas_ordenadas],
        "values": [sum_[fecha] for fecha in fechas_ordenadas]
    }

    if len(data["labels"]) == 1:
        data["labels"].append(data["labels"][0])
        data["values"].append(data["values"][0])
    print(data)
    return jsonify(data)

@futuros_bp.route('/portfolio-composition-chart-data', methods=['GET'])
def portfolio_composition_chart_data():
    if 'user_id' not in session:
        return redirect(url_for('index.index'))

    user_id = session['user_id']
    from flaskr.models import Usuario, Precio_accion
    user = Usuario.query.filter_by(id=user_id).first()

    labels = []
    values = []
    for usuario_accion in user.usuario_acciones:
        labels.append(usuario_accion.accion.simbolo)
        latest_price_record = get_latest_price(usuario_accion)
        if latest_price_record:
            values.append(usuario_accion.cantidad * latest_price_record.precio)
        else:
            values.append(0.0)
    data = {
        "labels": labels,
        "values": values
    }
    return jsonify(data)

@futuros_bp.route('/get-available-user-stocks', methods=['GET'])
def get_available_user_stocks():
    if 'user_id' not in session:
        return htmx_redirect(url_for('index.index'))

    user_id = session['user_id']
    from flaskr.models import Usuario
    user = Usuario.query.filte
    user = Usuario.query.filter_by(id=user_id).first()

    return render_template("htmx/available-user-stocks.html", user_stocks=user.usuario_acciones)

@futuros_bp.route('/portfolio-gains-chart-data', methods=['GET'])
def portfolio_gains_chart_data():
    if 'user_id' not in session:
        return redirect(url_for('index.index'))
    user_id = session['user_id']

    days = request.args.get('d')
    if not days or days not in ["7", "14", "21", "30", "60", "90", "180"]:
        days = "7"

    date_limit = date.today() - timedelta(days=int(days))

    from flaskr.models import Usuario, Precio_accion

    user = Usuario.query.filter_by(id=user_id).first()
    usuario_acciones = user.usuario_acciones
    sum_ = defaultdict(float)
    for usuario_accion in usuario_acciones:
        precios = Precio_accion.query.filter_by(accion_id=usuario_accion.accion_id).order_by(func.date(Precio_accion.fecha_hora).desc())
        precio_compra = get_first_price(usuario_accion).precio
        for precio in precios:
            if precio.fecha_hora.date() >= date_limit:
                if precio.fecha_hora.date() >= usuario_accion.fecha:
                    fecha = precio.fecha_hora.date()
                    sum_[fecha] += round((precio.precio - precio_compra) * usuario_accion.cantidad, 2)

    fechas_ordenadas = sorted(sum_.keys())

    data = {
        "labels": [fecha.strftime("%-d/%-m") for fecha in fechas_ordenadas],
        "values": [sum_[fecha] for fecha in fechas_ordenadas]
    }

    if len(data["labels"]) == 1:
        data["labels"].append(data["labels"][0])
        data["values"].append(data["values"][0])
    print(data)
    return jsonify(data)

@futuros_bp.route('/stock/<int:usuario_accion_id>', methods=['GET'])
def stock_details(usuario_accion_id):
    if 'user_id' not in session:
        return redirect(url_for('index.index'))

    from flaskr.models import UsuarioAccion

    usuario_accion = UsuarioAccion.query.filter_by(id=usuario_accion_id).first()
    if not usuario_accion:
        return jsonify({'error': 'Acción no encontrada'}), 404
    if usuario_accion.user_id != session['user_id']:
        return jsonify({'error': 'No autorizado'}), 403

    purchase_price = get_first_price(usuario_accion).precio
    current_price = get_latest_price(usuario_accion).precio

    return render_template('user-stock.html', usuario_accion=usuario_accion, purchase_price=purchase_price, current_price=current_price)

@futuros_bp.route('/user-stock-gains-chart-data/<int:usuario_accion_id>', methods=['GET'])
def user_stock_gains_chart_data(usuario_accion_id):
    if 'user_id' not in session:
        return redirect(url_for('index.index'))
    user_id = session['user_id']

    days = request.args.get('d')
    if not days or days not in ["7", "14", "21", "30", "60", "90", "180"]:
        days = "7"

    date_limit = date.today() - timedelta(days=int(days))

    from flaskr.models import Precio_accion, UsuarioAccion

    usuario_accion = UsuarioAccion.query.filter_by(id=usuario_accion_id).first()
    if not usuario_accion:
        return jsonify({'error': 'Acción no encontrada'}), 404
    if usuario_accion.user_id != user_id:
        return jsonify({'error': 'No autorizado'}), 403

    sum_ = defaultdict(float)
    precios = Precio_accion.query.filter_by(accion_id=usuario_accion.accion_id).order_by(func.date(Precio_accion.fecha_hora).desc())
    precio_compra = get_latest_price(usuario_accion).precio
    for precio in precios:
        if precio.fecha_hora.date() >= date_limit:
            if precio.fecha_hora.date() >= usuario_accion.fecha:
                fecha = precio.fecha_hora.date()
                sum_[fecha] += round((precio.precio - precio_compra) * usuario_accion.cantidad, 2)

    fechas_ordenadas = sorted(sum_.keys())

    data = {
        "labels": [fecha.strftime("%-d/%-m") for fecha in fechas_ordenadas],
        "values": [sum_[fecha] for fecha in fechas_ordenadas]
    }

    if len(data["labels"]) == 1:
        data["labels"].append(data["labels"][0])
        data["values"].append(data["values"][0])
    return jsonify(data)

@futuros_bp.route('/stock-chart-data/<int:accion_id>', methods=['GET'])
def stock_chart_data(accion_id):
    if 'user_id' not in session:
        return redirect(url_for('index.index'))

    days = request.args.get('d')
    if not days or days not in ["7", "14", "21", "30", "60", "90", "180"]:
        days = "7"

    date_limit = date.today() - timedelta(days=int(days))

    from flaskr.models import Precio_accion

    sum_ = defaultdict(float)

    precios = Precio_accion.query.filter_by(accion_id=accion_id).order_by(func.date(Precio_accion.fecha_hora).desc())
    for precio in precios:
        if precio.fecha_hora.date() >= date_limit:
            sum_[precio.fecha_hora.date()] += round(precio.precio, 2)

    fechas_ordenadas = sorted(sum_.keys())

    data = {
        "labels": [fecha.strftime("%-d/%-m") for fecha in fechas_ordenadas],
        "values": [sum_[fecha] for fecha in fechas_ordenadas]
    }

    if len(data["labels"]) == 1:
        data["labels"].append(data["labels"][0])
        data["values"].append(data["values"][0])
    return jsonify(data)