from dataclasses import dataclass
from typing import Optional, List, Dict, Any


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

