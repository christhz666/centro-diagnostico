from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Paciente
from datetime import datetime

bp = Blueprint('pacientes', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def listar_pacientes():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    buscar = request.args.get('buscar', '')
    query = Paciente.query
    if buscar:
        query = query.filter((Paciente.nombre.ilike(f'%{buscar}%')) | (Paciente.apellido.ilike(f'%{buscar}%')) | (Paciente.cedula.ilike(f'%{buscar}%')))
    query = query.order_by(Paciente.created_at.desc())
    pacientes = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({'pacientes': [p.to_dict() for p in pacientes.items], 'total': pacientes.total, 'pages': pacientes.pages, 'current_page': page})

@bp.route('/<int:paciente_id>', methods=['GET'])
@jwt_required()
def obtener_paciente(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    return jsonify(paciente.to_dict())

@bp.route('/', methods=['POST'])
@jwt_required()
def crear_paciente():
    try:
        datos = request.get_json()
        if not datos.get('nombre') or not datos.get('apellido'):
            return jsonify({'error': 'Nombre y apellido requeridos'}), 400
        if datos.get('cedula'):
            existe = Paciente.query.filter_by(cedula=datos['cedula']).first()
            if existe:
                return jsonify({'error': 'Ya existe un paciente con esta cédula'}), 400
        paciente = Paciente()
        paciente.cedula = datos.get('cedula')
        paciente.pasaporte = datos.get('pasaporte')
        paciente.nombre = datos['nombre']
        paciente.apellido = datos['apellido']
        paciente.fecha_nacimiento = datetime.fromisoformat(datos['fecha_nacimiento']) if datos.get('fecha_nacimiento') else None
        paciente.sexo = datos.get('sexo')
        paciente.telefono = datos.get('telefono')
        paciente.celular = datos.get('celular')
        paciente.email = datos.get('email')
        paciente.direccion = datos.get('direccion')
        paciente.ciudad = datos.get('ciudad')
        paciente.seguro_medico = datos.get('seguro_medico')
        paciente.numero_poliza = datos.get('numero_poliza')
        paciente.tipo_sangre = datos.get('tipo_sangre')
        paciente.alergias = datos.get('alergias')
        db.session.add(paciente)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Paciente creado', 'paciente': paciente.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:paciente_id>', methods=['PUT'])
@jwt_required()
def actualizar_paciente(paciente_id):
    try:
        paciente = Paciente.query.get_or_404(paciente_id)
        datos = request.get_json()
        if 'nombre' in datos: paciente.nombre = datos['nombre']
        if 'apellido' in datos: paciente.apellido = datos['apellido']
        if 'telefono' in datos: paciente.telefono = datos['telefono']
        if 'celular' in datos: paciente.celular = datos['celular']
        if 'email' in datos: paciente.email = datos['email']
        if 'direccion' in datos: paciente.direccion = datos['direccion']
        db.session.commit()
        return jsonify({'success': True, 'message': 'Paciente actualizado', 'paciente': paciente.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

import random
import string
import bcrypt

@bp.route('/<int:paciente_id>/generar-credenciales', methods=['POST'])
@jwt_required()
def generar_credenciales(paciente_id):
    """Generar credenciales de portal para paciente"""
    try:
        paciente = Paciente.query.get_or_404(paciente_id)
        
        # Generar usuario (nombre.apellido + número random)
        base_usuario = f"{paciente.nombre.lower()}.{paciente.apellido.lower()}"
        base_usuario = base_usuario.replace(' ', '')
        numero_random = ''.join(random.choices(string.digits, k=3))
        usuario = f"{base_usuario}{numero_random}"
        
        # Generar contraseña aleatoria
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        # Hash de la contraseña
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Actualizar paciente
        paciente.portal_usuario = usuario
        paciente.portal_password = password_hash
        db.session.commit()
        
        return jsonify({
            'success': True,
            'credenciales': {
                'usuario': usuario,
                'password': password,  # Solo se muestra una vez
                'mensaje': 'Guarde esta contraseña, no se mostrará nuevamente'
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
