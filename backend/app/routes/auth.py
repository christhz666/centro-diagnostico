from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from app import db
from app.models import Usuario
from app.utils.validators import sanitize_string
import bcrypt
from datetime import datetime
import logging

bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)


@bp.route('/login', methods=['POST'])
def login():
    datos = request.get_json()
    if not datos:
        return jsonify({'error': 'Datos requeridos'}), 400

    username = sanitize_string(datos.get('username', ''), max_length=50)
    password = datos.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Usuario y contraseña requeridos'}), 400

    if len(password) > 128:
        return jsonify({'error': 'Contraseña demasiado larga'}), 400

    # Buscar usuario
    usuario = Usuario.query.filter_by(username=username).first()

    # Siempre verificar hash incluso si no existe usuario (timing attack prevention)
    if not usuario or not usuario.activo:
        # Realizar hash dummy para evitar timing attacks
        bcrypt.checkpw(b'dummy', bcrypt.hashpw(b'dummy', bcrypt.gensalt()))
        logger.warning(f'Login fallido para usuario: {username} desde IP: {request.headers.get("X-Real-IP", request.remote_addr)}')
        return jsonify({'error': 'Credenciales inválidas'}), 401

    if bcrypt.checkpw(password.encode('utf-8'), usuario.password_hash.encode('utf-8')):
        usuario.ultimo_acceso = datetime.utcnow()
        db.session.commit()

        identity = str(usuario.id)
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)

        logger.info(f'Login exitoso: {username}')

        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'usuario': usuario.to_dict()
        })

    logger.warning(f'Password incorrecto para: {username} desde IP: {request.headers.get("X-Real-IP", request.remote_addr)}')
    return jsonify({'error': 'Credenciales inválidas'}), 401


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    return jsonify({'access_token': access_token})


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    usuario = Usuario.query.get(int(current_user_id))
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify(usuario.to_dict())


@bp.route('/cambiar-password', methods=['POST'])
@jwt_required()
def cambiar_password():
    current_user_id = get_jwt_identity()
    datos = request.get_json()

    if not datos:
        return jsonify({'error': 'Datos requeridos'}), 400

    password_actual = datos.get('password_actual', '')
    password_nuevo = datos.get('password_nuevo', '')

    if not password_actual or not password_nuevo:
        return jsonify({'error': 'Contraseña actual y nueva son requeridas'}), 400

    if len(password_nuevo) < 8:
        return jsonify({'error': 'La nueva contraseña debe tener al menos 8 caracteres'}), 400

    if len(password_nuevo) > 128:
        return jsonify({'error': 'Contraseña demasiado larga'}), 400

    usuario = Usuario.query.get(int(current_user_id))
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    if not bcrypt.checkpw(password_actual.encode('utf-8'), usuario.password_hash.encode('utf-8')):
        return jsonify({'error': 'Contraseña actual incorrecta'}), 401

    # Generar nuevo hash
    nuevo_hash = bcrypt.hashpw(
        password_nuevo.encode('utf-8'),
        bcrypt.gensalt(rounds=12)
    ).decode('utf-8')

    usuario.password_hash = nuevo_hash
    db.session.commit()

    logger.info(f'Contraseña cambiada para usuario: {usuario.username}')

    return jsonify({'success': True, 'message': 'Contraseña actualizada correctamente'})
