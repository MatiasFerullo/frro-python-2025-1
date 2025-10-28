#!/var/www/frro-python-2025-1/CarteraAcciones/venv/bin/python
# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask_mail import Mail, Message
import pymysql
import datetime
import logging
from logging.handlers import RotatingFileHandler
import traceback


## FALTA INTEGRAR CON LA BASE DE DATOS DE SQLALCHEMY

LOG_FILE = "mailer_log.txt"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logger = logging.getLogger("alertas_logger")
logger.setLevel(logging.INFO)



logger.info("==== Iniciando ejecución del mailer ====")

app = Flask(__name__) #Usa el mail service de flask

# Configuración de Gmail SMTP
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('SMTP_MAIL')  
app.config['MAIL_PASSWORD'] = os.environ.get('SMTP_TOKEN') 
app.config['MAIL_DEFAULT_SENDER'] = ('Cartera de futuros', os.environ.get('SMTP_MAIL'))

mail = Mail(app)

# Configuración de la conexión
conexion = pymysql.connect(
    host="200.58.107.248",        
    user= os.environ.get('DB_USER'),
    password= os.environ.get('DB_PASSWORD'),
    database="acciones",
    port=3306                # Puerto por defecto de MySQL
)

def main():
    try:
        with conexion.cursor() as cursor:
            #Sacar todas las alertas
            cursor.execute("SELECT * from alerta_precio;")
            alertas_precios = cursor.fetchall()
            
            logger.info(f"Alertas de precio: {len(alertas_precios)} encontradas")

            #Checkear una por una si se deberia activar
            for alerta in alertas_precios:
                check_alerta_precio(alerta)

            cursor.execute("SELECT * from alerta_rendimiento;")
            alertas_rendimientos = cursor.fetchall()

            logger.info(f"Alertas de rendimiento: {len(alertas_rendimientos)} encontradas")

            for alerta in alertas_rendimientos:
                check_alerta_rendimiento(alerta)
            
            cursor.execute("SELECT * from alerta_portafolio;")
            alertas_portafolios = cursor.fetchall()

            logger.info(f"Alertas de portafolio: {len(alertas_portafolios)} encontradas")

            for alerta in alertas_portafolios:
                check_alerta_portafolio(alerta)

    finally:
        conexion.close()
        logger.info("Conexión cerrada.")
        logger.info("==== Fin de ejecución del mailer ====")


#En los 3, comparar los valores actuales y los valores de las fechas de compra con las condiciones de las alertas

def check_alerta_rendimiento(alerta):
    #Suma de todos los precios de compra de las acciones del usuario
    precio_compra = 0
    #suma de todos los precios actuales de las acciones del usuario
    precio_actual = 0

    if precio_compra == 0:
        return
    
    if (alerta[4] == "loss"):
        #Si la perdida es mayor o igual al umbral
        if ((precio_compra - precio_actual) / precio_compra) >= alerta[3]:
            subject = "Rendimiento negativo del portafolio superó el umbral"
            mensaje = f"La pérdida actual de su portafolio es {(precio_compra - precio_actual) / precio_compra * 100:.2f}% que supera el umbral de {alerta[3] * 100:.2f}%."
            handle_alerta(alerta, subject, mensaje)
    else: #gain
        #Si la ganancia es mayor o igual al umbral
        if ((precio_actual - precio_compra) / precio_compra) >= alerta[3]:
            subject = "Rendimiento positivo del portafolio superó el umbral"
            mensaje = f"La ganancia actual de su portafolio es {(precio_actual - precio_compra) / precio_compra * 100:.2f}% que supera el umbral de {alerta[3] * 100:.2f}%."
            handle_alerta(alerta, subject, mensaje)

    

def check_alerta_precio(alerta):
    #Precio actual del futuro
    precio_actual = 0

    if (alerta[3] == "min"):
        #Si el precio actual es menor o igual al precio de la alerta
        if precio_actual <= alerta[3]:
            subject = "Alerta de precio mínimo alcanzada"
            mensaje = f"El precio actual del futuro ha caído a {precio_actual}, que es menor o igual al umbral de {alerta[4]}."
            handle_alerta(alerta, subject, mensaje)

    else: #max
        #Si el precio actual es mayor o igual al precio de la alerta
        if precio_actual >= alerta[3]:
            subject = "Alerta de precio máximo alcanzada"
            mensaje = f"El precio actual del futuro ha subido a {precio_actual}, que es mayor o igual al umbral de {alerta[4]}."
            handle_alerta(alerta, subject, mensaje)


def check_alerta_portafolio(alerta):
    #Suma de todos los precios actuales de las acciones del usuario
    valor_actual = 0
    #Suma de todos los precios de compra de las acciones del usuario
    valor_compra = 0

    if (valor_compra == 0):
        return
    
    if ((valor_actual - valor_compra) / valor_compra) >= alerta[3]: #Si la variacion es mayor o igual al umbral
        subject = "Rendimiento del portafolio superó el umbral"
        mensaje = f"El rendimiento actual de su portafolio es {(valor_actual - valor_compra) / valor_compra * 100:.2f}% que supera el umbral de {alerta[3] * 100:.2f}%."
        handle_alerta(alerta, subject, mensaje)



def handle_alerta(alerta, subject, mensaje):
    
    with conexion.cursor() as cursor:

        #Obtener el mail del usuario
        cursor.execute(f"SELECT email FROM usuario WHERE id = {alerta[1]};")
        mail_usuario = cursor.fetchone()
        print("Mail del usuario:", mail_usuario[0][0]) #Lista en una lista


    with app.app_context():
        try:
            msg = Message(
                subject="Alerta de Cartera de Futuros - " + subject, 
                recipients=["matias.ferullo1@gmail.com"], #Cambiar por el mail del usuario
                body="Este es un correo enviado por Cartera de Futuros.\n\n" + mensaje
            )
            mail.send(msg)
            logger.info(f"Correo enviado correctamente a {mail_usuario}")
        except Exception as e:
            logger.error(f"Error al enviar correo a {mail_usuario}: {e}\n{traceback.format_exc()}")



if __name__ == "__main__": 
    
    main()