## ACA VAN LAS TODAS LAS RUTAS RELACIONADAS CON LAS ACCIONES
from flask import Blueprint, jsonify
from flaskr.services.pyrofex_service import obtener_acciones_desde_api

acciones_bp = Blueprint('acciones', __name__)

@acciones_bp.route('/cargar-acciones', methods=['POST'])
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