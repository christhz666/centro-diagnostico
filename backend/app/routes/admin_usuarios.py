from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Usuario
from app.utils.validators import sanitize_string, sanitize_dict, validate_email
import bcrypt
import secrets

bp = Blueprint('admin_usuarios', __name__)


def require_admin(f):
    """Decorador para requerir rol admin"""
    from functools import wraps
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user_id = int(get_jwt_identity())
        usuario = Usuario.query.get(user_id)
        if not usuario or usuario.rol != 'admin':
            return jsonify({'error': 'Acceso denegado. Se requiere rol de administrador'}), 403
        return f(*args, **kwargs)
    return decorated


@bp.route('/usuarios', methods=['GET'])
@require_admin
def listar_usuarios():
    """Listar todos los usuarios"""
    usuarios = Usuario.query.order_by(Usuario.created_at.desc()).all()
    return jsonify({
        'usuarios': [u.to_dict() for u in usuarios],
        'total': len(usuarios)
    })


@bp.route('/usuarios/<int:user_id>', methods=['GET'])
@require_admin
def obtener_usuario(user_id):
    """Obtener un usuario por ID"""
    usuario = Usuario.query.get_or_404(user_id)
    return jsonify(usuario.to_dict())


@bp.route('/usuarios', methods=['POST'])
@require_admin
def crear_usuario():
    """Crear nuevo usuario"""
    datos = request.get_json()
    if not datos:
        return jsonify({'error': 'Datos requeridos'}), 400

    datos = sanitize_dict(datos)

    # Validaciones
    required = ['username', 'nombre', 'apellido', 'rol']
    for field in required:
        if not datos.get(field):
            return jsonify({'error': f'{field} es requerido'}), 400

    roles_validos = ['admin', 'cajero', 'tecnico', 'medico', 'recepcion']
    if datos['rol'] not in roles_validos:
        return jsonify({'error': f'Rol inválido. Válidos: {", ".join(roles_validos)}'}), 400

    # Verificar username único
    if Usuario.query.filter_by(username=datos['username']).first():
        return jsonify({'error': 'El nombre de usuario ya existe'}), 409

    if datos.get('email') and not validate_email(datos['email']):
        return jsonify({'error': 'Email inválido'}), 400

    # Generar contraseña temporal
    password_temporal = secrets.token_urlsafe(12)
    password_hash = bcrypt.hashpw(
        password_temporal.encode('utf-8'),
        bcrypt.gensalt(rounds=12)
    ).decode('utf-8')

    usuario = Usuario()
    usuario.username = datos['username'].lower().strip()
    usuario.password_hash = password_hash
    usuario.nombre = datos['nombre']
    usuario.apellido = datos['apellido']
    usuario.email = datos.get('email')
    usuario.rol = datos['rol']
    usuario.especialidad = datos.get('especialidad')
    usuario.activo = True

    db.session.add(usuario)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Usuario creado',
        'usuario': usuario.to_dict(),
        'password_temporal': password_temporal,
        'aviso': 'Guarde la contraseña temporal. El usuario deberá cambiarla al iniciar sesión.'
    }), 201


@bp.route('/usuarios/<int:user_id>', methods=['PUT'])
@require_admin
def actualizar_usuario(user_id):
    """Actualizar usuario"""
    usuario = Usuario.query.get_or_404(user_id)
    datos = request.get_json()
    if not datos:
        return jsonify({'error': 'Datos requeridos'}), 400

    datos = sanitize_dict(datos)

    if 'nombre' in datos:
        usuario.nombre = datos['nombre']
    if 'apellido' in datos:
        usuario.apellido = datos['apellido']
    if 'email' in datos:
        if datos['email'] and not validate_email(datos['email']):
            return jsonify({'error': 'Email inválido'}), 400
        usuario.email = datos['email']
    if 'rol' in datos:
        roles_validos = ['admin', 'cajero', 'tecnico', 'medico', 'recepcion']
        if datos['rol'] not in roles_validos:
            return jsonify({'error': 'Rol inválido'}), 400
        usuario.rol = datos['rol']
    if 'especialidad' in datos:
        usuario.especialidad = datos['especialidad']

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Usuario actualizado',
        'usuario': usuario.to_dict()
    })


@bp.route('/usuarios/<int:user_id>/toggle', methods=['POST'])
@require_admin
def toggle_usuario(user_id):
    """Activar/desactivar usuario"""
    current_user_id = int(get_jwt_identity())
    if user_id == current_user_id:
        return jsonify({'error': 'No puedes desactivarte a ti mismo'}), 400

    usuario = Usuario.query.get_or_404(user_id)
    usuario.activo = not usuario.activo
    db.session.commit()

    estado = 'activado' if usuario.activo else 'desactivado'
    return jsonify({
        'success': True,
        'message': f'Usuario {estado}',
        'activo': usuario.activo
    })


@bp.route('/usuarios/<int:user_id>/reset-password', methods=['POST'])
@require_admin
def reset_password(user_id):
    """Resetear contraseña de usuario"""
    usuario = Usuario.query.get_or_404(user_id)

    password_temporal = secrets.token_urlsafe(12)
    password_hash = bcrypt.hashpw(
        password_temporal.encode('utf-8'),
        bcrypt.gensalt(rounds=12)
    ).decode('utf-8')

    usuario.password_hash = password_hash
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Contraseña reseteada',
        'password_temporal': password_temporal,
        'aviso': 'El usuario deberá cambiar esta contraseña al iniciar sesión.'
    })


@bp.route('/roles', methods=['GET'])
@require_admin
def listar_roles():
    """Listar roles disponibles"""
    return jsonify({
        'roles': [
            {'id': 'admin', 'nombre': 'Administrador', 'descripcion': 'Acceso total al sistema'},
            {'id': 'cajero', 'nombre': 'Cajero', 'descripcion': 'Facturación y pagos'},
            {'id': 'tecnico', 'nombre': 'Técnico', 'descripcion': 'Resultados y equipos'},
            {'id': 'medico', 'nombre': 'Médico', 'descripcion': 'Historial y resultados de pacientes'},
            {'id': 'recepcion', 'nombre': 'Recepción', 'descripcion': 'Registro de pacientes y órdenes'},
        ]
    })
