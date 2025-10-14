from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()  

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128))

    def __repr__(self):
        return f"User('{self.email}')"

class Accion(db.Model):
    __tablename__ = 'accion'  # ← Tabla se llama 'accion'
    id = db.Column(db.Integer, primary_key=True)
    simbolo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    
    # Relación COMENTADA por ahora
    # precios = db.relationship('Precio', backref='accion', lazy=True)

    def __repr__(self):
        return f"Accion('{self.simbolo}')"

class Precio(db.Model):
    __tablename__ = 'precios'  
    id = db.Column(db.Integer, primary_key=True)
    accion_id = db.Column(db.Integer, db.ForeignKey('accion.id'), nullable=False)  # ← 'accion.id' NO 'acciones.id'
    precio = db.Column(db.Float, nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Precio('{self.precio}', '{self.fecha_hora}')"
