import pyRofex
import os 
from dotenv import load_dotenv

load_dotenv()

def obtener_acciones_desde_api():
    """Obtener instrumentos relacionados con acciones (futuros, índices, etc.)"""
    # Obtener credenciales desde variables de entorno
    pyRofex.initialize(
        user=os.environ.get('PYROFEX_USER'),
        password=os.environ.get('PYROFEX_PASSWORD'), 
        account=os.environ.get('PYROFEX_ACCOUNT'),
        environment=pyRofex.Environment.REMARKET  # O usar variable si necesitas cambiar
    )
    
    instruments = pyRofex.get_all_instruments()
    instrumentos_acciones = []
    
    # Mapear nombres más legibles
    nombres_legibles = {
        'GGAL': 'Grupo Financiero Galicia',
        'YPFD': 'YPF Sociedad Anónima', 
        'PAMP': 'Pampa Energía',
        'TXAR': 'Ternium Argentina',
        'CEPU': 'Central Puerto',
        'BMA': 'Banco Macro',
        'CRES': 'Cresud',
        'MIRG': 'Mirgor',
        'MERV': 'Índice MERVAL'
    }
    
    for instrument in instruments['instruments']:
        symbol = instrument['instrumentId']['symbol']
        
        # Incluir cualquier instrumento relacionado con acciones argentinas
        if any(accion in symbol for accion in ['GGAL', 'YPFD', 'PAMP', 'TXAR', 'CEPU', 'BMA', 'CRES', 'MIRG']):
            # Generar nombre legible
            nombre_base = next((nombres_legibles[accion] for accion in nombres_legibles if accion in symbol), symbol)
            
            # Mejorar el nombre según el tipo de instrumento
            if '/' in symbol:
                nombre = f"Futuro {nombre_base} {symbol.split('/')[1]}"
            elif 'MERV' in symbol:
                nombre = f"Derivado {nombre_base}"
            else:
                nombre = nombre_base
                
            instrumentos_acciones.append({
                'simbolo': symbol, 
                'nombre': nombre
            })
    
    return instrumentos_acciones