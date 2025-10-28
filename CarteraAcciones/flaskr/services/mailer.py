#!/venv/bin/python3
# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask_mail import Mail, Message
import pymysql
import datetime
import logging
from logging.handlers import RotatingFileHandler
import traceback
from dotenv import load_dotenv

load_dotenv()



app = Flask(__name__) #Usa el mail service de flask

# Configuración de Gmail SMTP
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('SMTP_MAIL')  
app.config['MAIL_PASSWORD'] =  os.environ.get('SMTP_TOKEN') 
app.config['MAIL_DEFAULT_SENDER'] = ('Cartera de futuros', os.environ.get('SMTP_MAIL'))

mail = Mail(app)

# Configuración de la conexión
conexion = pymysql.connect(
    host= "localhost",   
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
            


            cursor.execute("SELECT * FROM usuario;")
            print("Usuarios:", cursor.fetchall())
            cursor.execute("SELECT * from alerta")
            print("Alertas:", cursor.fetchall())

            cursor.execute("SELECT * FROM precio_accion WHERE DATE(fecha_hora) = \"2025-10-27\";")
            print("Precios acción 3:", cursor.fetchall())

            logger.info(f"Alertas de precio: {len(alertas_precios)} encontradas")

            #Checkear una por una si se deberia activar
            for alerta in alertas_precios:
                check_alerta_precio(alerta)
            
            cursor.execute("SELECT * from alerta_portafolio;")
            
            alertas_portafolios = cursor.fetchall()

            logger.info(f"Alertas de portafolio: {len(alertas_portafolios)} encontradas")

            for alerta in alertas_portafolios:
                check_alerta_portafolio(alerta)

            

    finally:
        conexion.close()
        logger.info("Conexión cerrada.")
        logger.info("==== Fin de ejecución del mailer ====")



def get_precio_accion(id_accion, fecha_hora):
    with conexion.cursor() as cursor:
        cursor.execute(f"SELECT precio FROM precio_accion WHERE accion_id = {id_accion} AND fecha_hora <= '{fecha_hora}' ORDER BY fecha_hora DESC LIMIT 1;")
        
        return cursor.fetchone()[0]

def get_precio_actual_futuro(id_accion):
    with conexion.cursor() as cursor:
        cursor.execute(f"SELECT precio FROM precio_accion WHERE accion_id = {id_accion} ORDER BY fecha_hora DESC LIMIT 1;")
        
        return cursor.fetchone()[0]

def check_alerta_precio(alerta):
    #Precio actual del futuro
    precio_actual = get_precio_actual_futuro(alerta[1])

    if (alerta[2] == "min"):
        #Si el precio actual es menor o igual al precio de la alerta
        if precio_actual <= alerta[3]:
            subject = "Alerta de precio mínimo alcanzada"
            mensaje = f"El precio actual del futuro ha caído a {precio_actual}, que es menor o igual al umbral de {alerta[3]}."
            handle_alerta(alerta, subject, mensaje)

    else: #max
        #Si el precio actual es mayor o igual al precio de la alerta
        if precio_actual >= alerta[3]:
            subject = "Alerta de precio máximo alcanzada"
            mensaje = f"El precio actual del futuro ha subido a {precio_actual}, que es mayor o igual al umbral de {alerta[3]}."
            handle_alerta(alerta, subject, mensaje)


def check_alerta_portafolio(alerta):
    #Obtener todos los futuros del portafolio del usuario
    with conexion.cursor() as cursor:
        cursor.execute(f"SELECT * FROM usuario_accion RIGHT JOIN alerta ON alerta.user_id = usuario_accion.user_id WHERE alerta.id = {alerta[0]};")
        futuros_portafolio = cursor.fetchall()

    #Suma de todos los precios actuales de las acciones del usuario
    valor_actual = 0
    for futuro in futuros_portafolio:
        valor_actual += get_precio_actual_futuro(futuro[2]) * futuro[4]

    #Suma de todos los precios de compra de las acciones del usuario
    valor_compra = 0
    for futuro in futuros_portafolio:
        valor_compra += get_precio_accion(futuro[2], futuro[3]) * futuro[4]
    print("Valor compra:", valor_compra)

    if (valor_compra == 0):
        return
    
    if ((valor_actual - valor_compra) / valor_compra) >= alerta[3]: #Si la variacion es mayor o igual al umbral
        subject = "Rendimiento del portafolio superó el umbral"
        mensaje = f"El rendimiento actual de su portafolio es {(valor_actual - valor_compra) / valor_compra * 100:.2f}% que supera el umbral de {alerta[3] * 100:.2f}%."
        handle_alerta(alerta, subject, mensaje)



def handle_alerta(alerta, subject, mensaje):
    
    with conexion.cursor() as cursor:

        #Obtener el mail del usuario
        cursor.execute(f"SELECT email FROM usuario RIGHT JOIN alerta ON alerta.id = {alerta[0]} WHERE usuario.id = alerta.user_id;")
        mail_usuario = cursor.fetchone()
        print("Mail del usuario:", mail_usuario[0])


    with app.app_context():
        try:
            msg = Message(
                subject="Alerta de Cartera de Futuros - " + subject, 
                recipients=["matias.ferullo1@gmail.com"], #Cambiar por el mail del usuario
                body="Este es un correo enviado por Cartera de Futuros.\n\n" + mensaje
            )
            #mail.send(msg)
            logger.info(f"Correo enviado correctamente a {mail_usuario}")
        except Exception as e:
            logger.error(f"Error al enviar correo a {mail_usuario}: {e}\n{traceback.format_exc()}")



if __name__ == "__main__": 
    logging.basicConfig(filename="app.log", level=logging.INFO)

    logger = logging.getLogger("alertas_logger")



    logger.info("==== Iniciando ejecución del mailer ====")

    main()