import pyRofex
import os 
from dotenv import load_dotenv

load_dotenv()

def get_active_futures():
    
    pyRofex.initialize(
        user=os.environ.get('PYROFEX_USER'),
        password=os.environ.get('PYROFEX_PASSWORD'), 
        account=os.environ.get('PYROFEX_ACCOUNT'),
        environment=pyRofex.Environment.REMARKET
    )
    
    instruments = pyRofex.get_all_instruments()["instruments"]
    print(f" Total instrumentos obtenidos: {len(instruments)}")

    futures = []
    for inst in instruments:
        cficode = inst.get("cficode", "")
        symbol = inst["instrumentId"]["symbol"]

        # Filtrar solo los futuros (CFI code que empieza con 'F')
        if cficode.startswith("F"):
            try:
                # Obtener el último precio
                market_data = pyRofex.get_market_data(ticker=symbol)
                last_price = market_data.get("marketData", {}).get("LA", {}).get("price")

                # Solo incluir si hay precio disponible
                if last_price is not None:
                    futures.append({
                        "symbol": symbol,
                        "price": last_price
                    })
                    print(f"✅ {symbol}: ${last_price}")
                else:
                    print(f"⚠️ {symbol}: Sin datos de precio")
            except Exception as e:
                print(f"❌ Error al obtener precio de {symbol}: {e}")

    print(f"\nFuturos con precio: {len(futures)} de {len(instruments)} totales.")
    return futures