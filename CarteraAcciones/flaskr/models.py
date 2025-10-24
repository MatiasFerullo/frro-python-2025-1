from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()  

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128))

    usuario_acciones = db.relationship("UsuarioAccion", back_populates="user", lazy='select', cascade="all, delete-orphan")
    alertas = db.relationship("Alerta", back_populates="user", lazy='select', cascade="all, delete-orphan")
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
    user_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    accion_id = db.Column(db.Integer, db.ForeignKey("accion.id"))
    fecha_hora = db.Column(db.DateTime)
    cantidad = db.Column(db.Float, nullable=False)
    precio_compra = db.Column(db.Float, nullable=False)

    user = db.relationship("Usuario", back_populates="usuario_acciones")
    accion = db.relationship("Accion", back_populates="usuario_acciones")
    alertas_rendimiento = db.relationship("AlertaRendimiento", back_populates="usuario_accion", lazy='select', cascade="all, delete-orphan")

class Alerta(db.Model):
    __tablename__ = "alerta"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))

    user = db.relationship("Usuario", back_populates="alertas")
    alertas_precio = db.relationship("AlertaPrecio", back_populates="alerta", lazy='select', cascade="all, delete-orphan")
    alertas_portafolio = db.relationship("AlertaPortafolio", back_populates="alerta", lazy='select', cascade="all, delete-orphan")
    alertas_rendimiento = db.relationship("AlertaRendimiento", back_populates="alerta", lazy='select', cascade="all, delete-orphan")

class AlertaPrecio(db.Model):
    __tablename__ = "alerta_precio"
    alerta_id = db.Column(db.Integer, db.ForeignKey("alerta.id"), primary_key=True)
    accion_id = db.Column(db.Integer, db.ForeignKey("accion.id"), primary_key=True)
    tipo = db.Column(db.String(10), primary_key=True)
    precio = db.Column(db.Float, nullable=False)

    alerta = db.relationship("Alerta", back_populates="alertas_precio")
    accion = db.relationship("Accion")

class AlertaPortafolio(db.Model):
    __tablename__ = "alerta_portafolio"
    alerta_id = db.Column(db.Integer, db.ForeignKey("alerta.id"), primary_key=True)
    variacion = db.Column(db.Float, nullable=False)

    alerta = db.relationship("Alerta", back_populates="alertas_portafolio")

class AlertaRendimiento(db.Model):
    __tablename__ = "alerta_rendimiento"
    alerta_id = db.Column(db.Integer, db.ForeignKey("alerta.id"), primary_key=True)
    # Aplica lógica de negocio para que el usuario no cree mas de una alerta por acción del portafolio
    usuario_accion_id = db.Column(db.Integer, db.ForeignKey("usuario_accion.id"))
    is_portafolio = db.Column(db.Boolean, nullable=False)
    porcentaje = db.Column(db.Integer, nullable=False)
    disparador = db.Column(db.String(10), nullable=False)

    alerta = db.relationship("Alerta", back_populates="alertas_rendimiento")
    usuario_accion = db.relationship("UsuarioAccion", back_populates="alertas_rendimiento")