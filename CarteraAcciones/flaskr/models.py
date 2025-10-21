from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()  

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128))

    usuario_acciones = db.relationship("UsuarioAccion", back_populates="user", lazy='select')
    def __repr__(self):
        return f"User('{self.email}')"

class Accion(db.Model):
    __tablename__ = 'accion' 
    id = db.Column(db.Integer, primary_key=True)
    simbolo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    
    # Relación COMENTADA por ahora
    # precios = db.relationship('Precio', backref='accion', lazy=True)
    usuario_acciones = db.relationship("UsuarioAccion", back_populates="accion", lazy='select')

    def __repr__(self):
        return f"Accion('{self.simbolo}')"

class Precio_accion(db.Model):
    __tablename__ = 'precio_accion'
    id = db.Column(db.Integer, primary_key=True)
    accion_id = db.Column(db.Integer, db.ForeignKey('accion.id'), nullable=False)
    precio = db.Column(db.Float, nullable=False)  
    fecha_hora = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):

        return f"Precio('{self.precio}', '{self.fecha_hora}')"

class UsuarioAccion(db.Model):
    __tablename__ = "usuario_accion"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    accion_id = db.Column(db.Integer, db.ForeignKey("accion.id"))
    fecha_hora = db.Column(db.DateTime)
    cantidad = db.Column(db.Float, nullable=False)
    precio_compra = db.Column(db.Float, nullable=False)

    user = db.relationship("User", back_populates="usuario_acciones")
    accion = db.relationship("Accion", back_populates="usuario_acciones")

    

