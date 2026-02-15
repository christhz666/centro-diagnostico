from flask import Flask, request, jsonify
from flask_cors import CORS
from config import config
import os
import logging
from logging.handlers import RotatingFileHandler


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'production')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    from app import db, migrate, jwt

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # =====================
    # CORS SEGURO
    # =====================
    allowed_origins = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://192.9.135.84',
        'http://192.9.135.84:3000',
    ]
    CORS(app, origins=allowed_origins, supports_credentials=True)

    # =====================
    # HEADERS DE SEGURIDAD
    # =====================
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers.pop('Server', None)
        response.headers.pop('X-Powered-By', None)
        return response

    # =====================
    # RATE LIMITING BÁSICO
    # =====================
    login_attempts = {}

    @app.before_request
    def rate_limit_login():
        if request.path == '/api/auth/login' and request.method == 'POST':
            ip = request.headers.get('X-Real-IP', request.remote_addr)
            import time
            now = time.time()

            if ip in login_attempts:
                attempts = [t for t in login_attempts[ip] if now - t < 300]
                login_attempts[ip] = attempts

                if len(attempts) >= 10:
                    return jsonify({
                        'error': 'Demasiados intentos. Espere 5 minutos.'
                    }), 429

                login_attempts[ip].append(now)
            else:
                login_attempts[ip] = [now]

    # =====================
    # LOGGING
    # =====================
    if not app.debug:
        os.makedirs('logs', exist_ok=True)
        file_handler = RotatingFileHandler(
            'logs/centro_diagnostico.log',
            maxBytes=10_000_000,
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [%(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Centro Diagnóstico iniciado')

    # =====================
    # CREAR DIRECTORIOS
    # =====================
    os.makedirs(app.config.get('UPLOAD_FOLDER', './uploads'), exist_ok=True)
    os.makedirs(app.config.get('RESULTADOS_FOLDER', './uploads/resultados'), exist_ok=True)
    os.makedirs(app.config.get('TEMP_FOLDER', './uploads/temp'), exist_ok=True)

    # =====================
    # REGISTRAR BLUEPRINTS
    # =====================
    blueprints = {
        'app.routes.auth': ('auth', '/api/auth'),
        'app.routes.pacientes': ('pacientes', '/api/pacientes'),
        'app.routes.estudios': ('estudios', '/api/estudios'),
        'app.routes.ordenes': ('ordenes', '/api/ordenes'),
        'app.routes.facturas': ('facturas', '/api/facturas'),
        'app.routes.reportes': ('reportes', '/api/reportes'),
        'app.routes.impresion': ('impresion', '/api/impresion'),
        'app.routes.resultados': ('resultados', '/api/resultados'),
        'app.routes.integraciones': ('integraciones', '/api/integraciones'),
        'app.routes.portal_paciente': ('portal_paciente', '/api/portal'),
        'app.routes.portal_medico': ('portal_medico', '/api/medico'),
        'app.routes.whatsapp': ('whatsapp', '/api/whatsapp'),
        'app.routes.busqueda': ('busqueda', '/api/busqueda'),
        'app.routes.configuracion': ('configuracion', '/api/config'),
        'app.routes.admin_usuarios': ('admin_usuarios', '/api/admin'),
    }

    for module_path, (bp_name, url_prefix) in blueprints.items():
        try:
            import importlib
            module = importlib.import_module(module_path)
            bp = getattr(module, 'bp')
            app.register_blueprint(bp, url_prefix=url_prefix)
            app.logger.debug(f'Blueprint registrado: {bp_name}')
        except Exception as e:
            app.logger.warning(f'No se pudo cargar {module_path}: {e}')

    # =====================
    # RUTAS BASE
    # =====================
    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'message': 'Sistema operativo', 'env': config_name}

    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Recurso no encontrado'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Error 500: {error}')
        return {'error': 'Error interno del servidor'}, 500

    @app.errorhandler(405)
    def method_not_allowed(error):
        return {'error': 'Método no permitido'}, 405

    return app


# =====================
# PUNTO DE ENTRADA
# =====================
if __name__ == '__main__':
    env = os.getenv('FLASK_ENV', 'production')
    application = create_app(env)

    if env == 'production':
        # En producción usar Gunicorn (ver más abajo)
        print("??  En producción use: gunicorn run:application")
        print("   Iniciando en modo desarrollo para testing...")
        application.run(host='127.0.0.1', port=5000, debug=False)
    else:
        application.run(host='0.0.0.0', port=5000, debug=True)

# Para Gunicorn
application = create_app(os.getenv('FLASK_ENV', 'production'))
