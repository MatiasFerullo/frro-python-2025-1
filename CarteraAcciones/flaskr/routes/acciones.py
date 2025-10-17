## ACA VAN LAS TODAS LAS RUTAS RELACIONADAS CON LAS ACCIONES
from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from flaskr.services.pyrofex_service import obtener_acciones_desde_api
from datetime import datetime

acciones_bp = Blueprint('acciones', __name__)

@acciones_bp.route('/cargar-acciones', methods=['GET'])
def cargar_acciones():
    try:
        instrumentos_api = obtener_acciones_desde_api()  
        
        from flaskr.models import Accion, db
        
        # Test simple de la BD
        count_antes = Accion.query.count()
        print(f"OK: BD conectada. Hay {count_antes} acciones")

        print("Procesando instrumentos...")
        instrumentos_nuevos = []
        instrumentos_existentes = []
        
        for instrumento_data in instrumentos_api:
            # Verificar si ya existe
            existe = Accion.query.filter_by(simbolo=instrumento_data['simbolo']).first()
            if not existe:
                nuevo_instrumento = Accion(
                    simbolo=instrumento_data['simbolo'], 
                    nombre=instrumento_data['nombre']
                )
                instrumentos_nuevos.append(nuevo_instrumento)
                print(f" Nuevo: {instrumento_data['simbolo']} - {instrumento_data['nombre']}")
            else:
                instrumentos_existentes.append(instrumento_data['simbolo'])
                print(f"⏭ Ya existe: {instrumento_data['simbolo']}")
        
        print(f"🔍 Paso 4: Guardando {len(instrumentos_nuevos)} nuevos...")
        if instrumentos_nuevos:
            db.session.bulk_save_objects(instrumentos_nuevos)
            db.session.commit()
            mensaje = f'Se agregaron {len(instrumentos_nuevos)} nuevos instrumentos. Ya existían: {len(instrumentos_existentes)}'
            print(f" {mensaje}")
            return jsonify({
                'mensaje': mensaje,
                'nuevos': len(instrumentos_nuevos),
                'existentes': len(instrumentos_existentes),
                'total_en_bd': count_antes + len(instrumentos_nuevos)
            })
        else:
            mensaje = f'No se encontraron instrumentos nuevos para agregar. Ya existen {len(instrumentos_existentes)} instrumentos en la base de datos.'
            print(f" {mensaje}")
            return jsonify({
                'mensaje': mensaje,
                'nuevos': 0,
                'existentes': len(instrumentos_existentes),
                'total_en_bd': count_antes
            })
            
    except Exception as e:
        print(f" ERROR: {str(e)}")
        import traceback
        print(f" Traceback completo:")
        print(traceback.format_exc())
        
        try:
            from flaskr import db
            db.session.rollback()
            print(" Rollback ejecutado")
        except Exception as rollback_error:
            print(f" Error en rollback: {rollback_error}")
            
        return jsonify({'error': str(e)}), 500
    

@acciones_bp.route('/acciones', methods=['GET'])
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
@acciones_bp.route('/new-portfolio-stock', methods=['POST'])
def add_stock_to_portfolio():
    if 'user_id' not in session:
        return redirect(url_for('index.index'))
    
    user_id = session['user_id']

    from flaskr.models import Accion, User, UsuarioAccion, db

    data = request.form
    fecha_hora = data.get('fecha_hora')
    accion_id = data['accion_id']
    cantidad = data['cantidad']
    precio_compra = data['precio_compra']
    comision = data['comision']
    moneda = data['moneda']

    accion = Accion.query.filter_by(id=accion_id).first()
    if not accion:
        return jsonify({'error': 'Acción no encontrada'}), 404

    nueva_usuario_accion = UsuarioAccion(
        user_id=user_id,
        accion_id=accion_id,
        fecha_hora=fecha_hora,
        cantidad=cantidad,
        precio_compra=precio_compra,
        comision=comision,
        moneda=moneda
    )

    try:
        db.session.add(nueva_usuario_accion)
        db.session.commit()
        user = User.query.filter_by(id=user_id).first()
        return render_template('htmx/stock-list.html', usuario_acciones=user.usuario_acciones, view='edit')
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': "Couldn't persist db"}), 500

@acciones_bp.route('/get-user-stocks', methods=['GET'])
def get_user_stocks():
    if 'user_id' not in session:
        return redirect(url_for('index.index'))
    
    user_id = session['user_id']
    from flaskr.models import User
    user = User.query.filter_by(id=user_id).first()
    view = request.args.get('view')
    if view == None or view == '' or view not in ['menu', 'edit']:
        view = 'menu'
    return render_template('htmx/stock-list.html', usuario_acciones=user.usuario_acciones, view=view)

@acciones_bp.route('/delete-user-stock/<int:usuario_accion_id>', methods=['DELETE'])
def delete_user_stock(usuario_accion_id):
    if 'user_id' not in session:
        return redirect(url_for('index.index'))
    
    user_id = session['user_id']
    from flaskr.models import UsuarioAccion, User, db

    usuario_accion = UsuarioAccion.query.filter_by(id=usuario_accion_id, user_id=user_id).first()
    if not usuario_accion:
        return jsonify({'error': 'Registro no encontrado'}), 404

    try:
        db.session.delete(usuario_accion)
        db.session.commit()
        user = User.query.filter_by(id=user_id).first()
        return render_template('htmx/stock-list.html', usuario_acciones=user.usuario_acciones, view='edit')
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': "Couldn't delete from db"}), 500

@acciones_bp.route('/get-available-stocks', methods=['GET'])
def get_available_stocks():
    try:
        from flaskr.models import Accion
        
        acciones = Accion.query.all()
        return render_template('htmx/available-stocks.html', acciones=acciones)
    except Exception as e:
        return jsonify({'error': "Couldn't get available stock"}), 500