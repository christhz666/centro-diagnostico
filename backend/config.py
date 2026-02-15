import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuración base"""
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY or SECRET_KEY.startswith('CAMBIAR') or SECRET_KEY == 'dev-secret-key-change-in-production':
        raise RuntimeError("??  SECRET_KEY no configurada. Edita el archivo .env")

    # Base de datos
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError("??  DATABASE_URL no configurada. Edita el archivo .env")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }

    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY or JWT_SECRET_KEY.startswith('CAMBIAR'):
        raise RuntimeError("??  JWT_SECRET_KEY no configurada. Edita el archivo .env")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'

    # Archivos
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')
    RESULTADOS_FOLDER = os.path.join(UPLOAD_FOLDER, 'resultados')
    TEMP_FOLDER = os.path.join(UPLOAD_FOLDER, 'temp')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'pdf', 'dcm', 'jpg', 'jpeg', 'png', 'hl7', 'txt'}

    # Monitoreo
    EQUIPOS_EXPORT_PATH = os.getenv('EQUIPOS_EXPORT_PATH', './uploads/equipos')

    # Nube
    CLOUD_SYNC_ENABLED = os.getenv('CLOUD_SYNC_ENABLED', 'false').lower() == 'true'
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET', 'centro-diagnostico-resultados')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

    # Email
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

    # NCF / ITBIS
    NCF_VALIDATION_ENABLED = True
    ITBIS_RATE = 0.18

    # Sesión
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class ProductionConfig(Config):
    """Producción"""
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Desarrollo - NO usar en producción"""
    DEBUG = True
    TESTING = False
    # Permitir keys genéricas solo en dev
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-key-not-for-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-key-not-for-production')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/centro_diagnostico'
    )


class TestingConfig(DevelopmentConfig):
    """Testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/centro_diagnostico_test'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': ProductionConfig  # CAMBIADO: default es producción
}

# Parche UTF-8
class ConfigUtf8(Config):
    JSON_AS_ASCII = False
    RESTFUL_JSON = {'ensure_ascii': False}

# Aplicar parche a las configuraciones existentes
DevelopmentConfig.JSON_AS_ASCII = False
ProductionConfig.JSON_AS_ASCII = False

# Parche forzado de codificación
class ConfigUtf8Fix(Config):
    JSON_AS_ASCII = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'client_encoding': 'utf8',
        'connect_args': {'client_encoding': 'utf8'}
    }

# Aplicar a Production
ProductionConfig.SQLALCHEMY_ENGINE_OPTIONS = ConfigUtf8Fix.SQLALCHEMY_ENGINE_OPTIONS
ProductionConfig.JSON_AS_ASCII = False
