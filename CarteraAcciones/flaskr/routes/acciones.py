## ACA VAN LAS TODAS LAS RUTAS RELACIONADAS CON LAS ACCIONES
from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from datetime import datetime
from flask import Blueprint, jsonify
from flaskr.models import Accion, Precio_accion
from datetime import datetime
from flaskr import db
from flaskr.services.pyrofex_service import get_active_futures 




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

# Agregar una accion al portafolio del usuario (form de "Añadir accion" en /portfolio)
@futuros_bp.route('/new-portfolio-stock', methods=['POST'])
def add_stock_to_portfolio():
    if 'user_id' not in session:
        return redirect(url_for('index.index'))
    
    user_id = session['user_id']

    from flaskr.models import Accion, Usuario, UsuarioAccion, db

    data = request.form
    fecha_hora = data.get('fecha_hora')
    accion_id = data['accion_id']
    cantidad = data['cantidad']
    precio_compra = data['precio_compra']

    accion = Accion.query.filter_by(id=accion_id).first()
    if not accion:
        return jsonify({'error': 'Acción no encontrada'}), 404

    nueva_usuario_accion = UsuarioAccion(
        user_id=user_id,
        accion_id=accion_id,
        fecha_hora=fecha_hora,
        cantidad=cantidad,
        precio_compra=precio_compra
    )

    try:
        db.session.add(nueva_usuario_accion)
        db.session.commit()
        user = Usuario.query.filter_by(id=user_id).first()
        return render_template('htmx/stock-list.html', usuario_acciones=user.usuario_acciones, view='edit')
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': "Couldn't persist db"}), 500

@futuros_bp.route('/get-user-stocks', methods=['GET'])
def get_user_stocks():
    if 'user_id' not in session:
        return redirect(url_for('index.index'))
    
    user_id = session['user_id']
    from flaskr.models import Usuario, Precio_accion
    user = Usuario.query.filter_by(id=user_id).first()
    view = request.args.get('view')
    if view == None or view == '' or view not in ['menu', 'edit']:
        view = 'menu'
    
    latest_prices = {}
    first_prices = {}

    for usuario_accion in user.usuario_acciones:
        latest_price_record = Precio_accion.query.filter_by(accion_id=usuario_accion.accion_id).order_by(Precio_accion.fecha_hora.desc()).first()
        if latest_price_record:
            latest_prices[usuario_accion.id] = latest_price_record.precio
        else:
            latest_prices[usuario_accion.id] = 0.0

        first_price_record = Precio_accion.query.filter(
            Precio_accion.accion_id == usuario_accion.accion_id,
            Precio_accion.fecha_hora <= usuario_accion.fecha_hora
        ).order_by(Precio_accion.fecha_hora.desc()).first()

        if first_price_record:
            first_prices[usuario_accion.id] = first_price_record.precio
        else:
            first_prices[usuario_accion.id] = 0.0

    return render_template('htmx/stock-list.html', usuario_acciones=user.usuario_acciones, view=view, latest_prices=latest_prices, first_prices=first_prices)

@futuros_bp.route('/delete-user-stock/<int:usuario_accion_id>', methods=['DELETE'])
def delete_user_stock(usuario_accion_id):
    if 'user_id' not in session:
        return redirect(url_for('index.index'))
    
    user_id = session['user_id']
    from flaskr.models import UsuarioAccion, Usuario, db

    usuario_accion = UsuarioAccion.query.filter_by(id=usuario_accion_id, user_id=user_id).first()
    if not usuario_accion:
        return jsonify({'error': 'Registro no encontrado'}), 404

    try:
        db.session.delete(usuario_accion)
        db.session.commit()
        user = Usuario.query.filter_by(id=user_id).first()
        return render_template('htmx/stock-list.html', usuario_acciones=user.usuario_acciones, view='edit')
    except Exception as e:
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
        return redirect(url_for('index.index'))
    
    user_id = session['user_id']

    from flaskr.models import UsuarioAccion, Usuario, UsuarioAccion, db

    data = request.form
    usuario_accion_id = data['usuario_accion_id']
    fecha_hora = data.get('fecha_hora')
    cantidad = data['cantidad']
    precio_compra = data['precio_compra']

    usuario_accion = UsuarioAccion.query.filter_by(id=usuario_accion_id).first()
    if not usuario_accion:
        return jsonify({'error': 'Acción del usuario no encontrada'}), 404

    usuario_accion.fecha_hora = fecha_hora
    usuario_accion.cantidad = cantidad
    usuario_accion.precio_compra = precio_compra

    try:
        db.session.commit()
        user = Usuario.query.filter_by(id=user_id).first()
        return render_template('htmx/stock-list.html', usuario_acciones=user.usuario_acciones, view='edit')
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': "Couldn't persist db"}), 500

@futuros_bp.route('/get-portfolio-summary', methods=['GET'])
def get_portfolio_summary():
    if 'user_id' not in session:
        return redirect(url_for('index.index'))
    
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
            Precio_accion.fecha_hora <= usuario_accion.fecha_hora
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
    # TODO: Agregar el histórico del portafolio del usuario
    # Este endpoint controla la gráfica que aparece arriba de todo en la página principal
    # Labels tiene los valores del eje x
    # Values tiene los valores del eje y correspondientes a cáda valor del eje x
    # Por esta razón ambas listas deben tener la misma cantidad de elementos
    data = {
        "labels": ["10/8", "11/8", "12/8", "13/8", "14/8", "15/8", "16/8", "17/8", "18/8", "19/8", "20/8"],
        "values": [120, 118, 121, 123, 125, 127, 130, 128, 132, 135, 100]
    }
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
        latest_price_record = Precio_accion.query.filter_by(accion_id=usuario_accion.accion_id).order_by(Precio_accion.fecha_hora.desc()).first()
        if latest_price_record:
            values.append(usuario_accion.cantidad * latest_price_record.precio)
        else:
            values.append(0.0)
    data = {
        "labels": labels,
        "values": values
    }
    return jsonify(data)