from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db
from app.models import Usuario
import bcrypt
from datetime import datetime

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
def login():
    datos = request.get_json()
    if not datos or 'username' not in datos or 'password' not in datos:
        return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
    usuario = Usuario.query.filter_by(username=datos['username']).first()
    if not usuario or not usuario.activo:
        return jsonify({'error': 'Credenciales inválidas'}), 401
    if bcrypt.checkpw(datos['password'].encode('utf-8'), usuario.password_hash.encode('utf-8')):
        usuario.ultimo_acceso = datetime.utcnow()
        db.session.commit()
        identity = str(usuario.id)
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        return jsonify({'access_token': access_token, 'refresh_token': refresh_token, 'usuario': usuario.to_dict()})
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
