from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class User:
    id: int
    username: str
    email: str
    password: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password': self.password  #Nota : es una prueba, no se muestra la contraseña en producción
        }

@dataclass
class Precio:
    id: int
    accion_id: int
    precio: float
    fecha_hora: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'accion_id': self.accion_id,
            'precio': float(self.precio),
            'fecha_hora': self.fecha_hora.isoformat()
        }
    

@dataclass
class Accion:
    id: int
    simbolo: str
    nombre: str
    descripcion: Optional[str] = None
    precios: Optional[List[Precio]] = None

    def to_dict(self, include_prices: bool = False) -> Dict[str, Any]:
        result = {
            'id': self.id,
            'simbolo': self.simbolo,
            'nombre': self.nombre,
            'descripcion': self.descripcion
        }
        if include_prices and self.precios:
            result['precios'] = [precio.to_dict() for precio in self.precios]
        return result
    
    def agregar_precio(self, precio: float, fecha_hora: Optional[datetime] = None):
        if self.precios is None:
            self.precios = []
        
        nuevo_precio = Precio(
            id=0, # El ID debería ser asignado por la base de datos
            accion_id=self.id,
            precio=precio,
            fecha_hora=fecha_hora or datetime.now()
        )
        self.precios.append(nuevo_precio)
        return nuevo_precio
    
    def obtener_ultimo_precio(self) -> Optional[Precio]:
        if self.precios:
            return max(self.precios, key=lambda p: p.fecha_hora)
        return None
