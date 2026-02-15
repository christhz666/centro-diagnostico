from flask import Flask
from flask_cors import CORS
from config import config
import os

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    from app import db, migrate, jwt
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    os.makedirs(app.config.get('UPLOAD_FOLDER', './uploads'), exist_ok=True)
    
    # Importar solo módulos que SABEMOS que existen
    try:
        from app.routes.auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
    except: pass
    
    try:
        from app.routes.pacientes import bp as pacientes_bp
        app.register_blueprint(pacientes_bp, url_prefix='/api/pacientes')
    except: pass
    
    try:
        from app.routes.estudios import bp as estudios_bp
        app.register_blueprint(estudios_bp, url_prefix='/api/estudios')
    except: pass
    
    try:
        from app.routes.ordenes import bp as ordenes_bp
        app.register_blueprint(ordenes_bp, url_prefix='/api/ordenes')
    except: pass
    
    try:
        from app.routes.facturas import bp as facturas_bp
        app.register_blueprint(facturas_bp, url_prefix='/api/facturas')
    except: pass
    
    try:
        from app.routes.reportes import bp as reportes_bp
        app.register_blueprint(reportes_bp, url_prefix='/api/reportes')
    except: pass
    
    try:
        from app.routes.busqueda import bp as busqueda_bp
        app.register_blueprint(busqueda_bp, url_prefix='/api/busqueda')
    except: pass
    
    try:
        from app.routes.impresion import bp as impresion_bp
        app.register_blueprint(impresion_bp, url_prefix='/api/impresion')
    except: pass
    
    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'message': 'Sistema operativo'}
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Recurso no encontrado'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Error interno del servidor'}, 500
    
    return app

if __name__ == '__main__':
    application = create_app(os.getenv('FLASK_ENV', 'development'))
    application.run(host='0.0.0.0', port=5000, debug=True)
