import os
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy 
from flaskr.models import db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    # Cargar variables de entorno
    load_dotenv()
    
    db_user = os.environ.get('DB_USER', 'admin')
    db_password = os.environ.get('DB_PASSWORD', 'admin')
    db_name = os.environ.get('DB_NAME', 'acciones')
    
    # Configuración de la base de datos 
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@localhost/{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    @app.template_filter('format_price')
    def format_price(value):
        try:
            value = float(value)
            if value.is_integer():
                formatted = f"{int(value):,}"
            else:
                formatted = f"{value:,.2f}"
            formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
            return formatted
        except (ValueError, TypeError):
            return value
   
    with app.app_context():
        from flaskr import models 
    
    
    from flaskr.routes.auth import auth_bp
    from flaskr.routes.index import index_bp
    from flaskr.routes.acciones import futuros_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(futuros_bp)
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app