from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Estudio, CategoriaEstudio, Usuario
from app.utils.validators import sanitize_string, sanitize_dict
from sqlalchemy import or_

bp = Blueprint('estudios', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def listar_estudios():
    categoria_id = request.args.get('categoria_id', type=int)
    buscar = sanitize_string(request.args.get('buscar', ''), max_length=100)
    solo_activos = request.args.get('activos', 'true') == 'true'

    query = Estudio.query
    if solo_activos:
        query = query.filter_by(activo=True)
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)
    if buscar and len(buscar) >= 2:
        search = f'%{buscar}%'
        query = query.filter(
            or_(
                Estudio.nombre.ilike(search),
                Estudio.codigo.ilike(search),
                Estudio.descripcion.ilike(search)
            )
        )

    estudios = query.order_by(Estudio.nombre).all()

    return jsonify({
        'estudios': [{
            'id': e.id,
            'codigo': e.codigo,
            'nombre': e.nombre,
            'categoria': e.categoria.nombre if e.categoria else None,
            'categoria_id': e.categoria_id,
            'precio': float(e.precio),
            'descripcion': e.descripcion,
            'tipo_resultado': e.tipo_resultado,
            'tiempo_estimado': e.tiempo_estimado,
            'requiere_preparacion': e.requiere_preparacion,
            'instrucciones_preparacion': e.instrucciones_preparacion,
            'activo': e.activo
        } for e in estudios],
        'total': len(estudios)
    })


@bp.route('/<int:estudio_id>', methods=['GET'])
@jwt_required()
def obtener_estudio(estudio_id):
    estudio = Estudio.query.get_or_404(estudio_id)
    return jsonify({
        'id': estudio.id,
        'codigo': estudio.codigo,
        'nombre': estudio.nombre,
        'categoria': estudio.categoria.nombre if estudio.categoria else None,
        'categoria_id': estudio.categoria_id,
        'precio': float(estudio.precio),
        'costo': float(estudio.costo) if estudio.costo else None,
        'descripcion': estudio.descripcion,
        'tipo_resultado': estudio.tipo_resultado,
        'tiempo_estimado': estudio.tiempo_estimado,
        'requiere_preparacion': estudio.requiere_preparacion,
        'instrucciones_preparacion': estudio.instrucciones_preparacion,
        'activo': estudio.activo
    })


@bp.route('/', methods=['POST'])
@jwt_required()
def crear_estudio():
    datos = request.get_json()
    if not datos:
        return jsonify({'error': 'Datos requeridos'}), 400

    datos = sanitize_dict(datos)

    required = ['codigo', 'nombre', 'precio']
    for f in required:
        if not datos.get(f):
            return jsonify({'error': f'{f} es requerido'}), 400

    if Estudio.query.filter_by(codigo=datos['codigo'].upper()).first():
        return jsonify({'error': 'Ya existe un estudio con este código'}), 409

    try:
        precio = float(datos['precio'])
        if precio <= 0:
            return jsonify({'error': 'Precio debe ser mayor a 0'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Precio inválido'}), 400

    estudio = Estudio()
    estudio.codigo = datos['codigo'].upper().strip()
    estudio.nombre = datos['nombre']
    estudio.categoria_id = datos.get('categoria_id')
    estudio.descripcion = datos.get('descripcion')
    estudio.precio = precio
    estudio.costo = float(datos['costo']) if datos.get('costo') else None
    estudio.tipo_resultado = datos.get('tipo_resultado', 'pdf')
    estudio.tiempo_estimado = datos.get('tiempo_estimado')
    estudio.requiere_preparacion = datos.get('requiere_preparacion', False)
    estudio.instrucciones_preparacion = datos.get('instrucciones_preparacion')
    estudio.activo = True

    db.session.add(estudio)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Estudio creado', 'estudio': estudio.to_dict()}), 201


@bp.route('/<int:estudio_id>', methods=['PUT'])
@jwt_required()
def actualizar_estudio(estudio_id):
    estudio = Estudio.query.get_or_404(estudio_id)
    datos = request.get_json()
    if not datos:
        return jsonify({'error': 'Datos requeridos'}), 400

    datos = sanitize_dict(datos)

    if 'nombre' in datos:
        estudio.nombre = datos['nombre']
    if 'precio' in datos:
        try:
            estudio.precio = float(datos['precio'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Precio inválido'}), 400
    if 'categoria_id' in datos:
        estudio.categoria_id = datos['categoria_id']
    if 'descripcion' in datos:
        estudio.descripcion = datos['descripcion']
    if 'tipo_resultado' in datos:
        estudio.tipo_resultado = datos['tipo_resultado']
    if 'tiempo_estimado' in datos:
        estudio.tiempo_estimado = datos['tiempo_estimado']
    if 'requiere_preparacion' in datos:
        estudio.requiere_preparacion = datos['requiere_preparacion']
    if 'instrucciones_preparacion' in datos:
        estudio.instrucciones_preparacion = datos['instrucciones_preparacion']
    if 'activo' in datos:
        estudio.activo = datos['activo']
    if 'costo' in datos:
        estudio.costo = float(datos['costo']) if datos['costo'] else None

    db.session.commit()
    return jsonify({'success': True, 'message': 'Estudio actualizado', 'estudio': estudio.to_dict()})


@bp.route('/categorias', methods=['GET'])
@jwt_required()
def listar_categorias():
    categorias = CategoriaEstudio.query.filter_by(activo=True).order_by(CategoriaEstudio.nombre).all()
    return jsonify({
        'categorias': [{
            'id': c.id,
            'nombre': c.nombre,
            'descripcion': c.descripcion,
            'color': c.color,
            'cantidad_estudios': c.estudios.filter_by(activo=True).count()
        } for c in categorias]
    })


@bp.route('/precios', methods=['GET'])
@jwt_required()
def lista_precios():
    """Lista de precios agrupada por categoría"""
    categorias = CategoriaEstudio.query.filter_by(activo=True).order_by(CategoriaEstudio.nombre).all()

    resultado = []
    for cat in categorias:
        estudios = Estudio.query.filter_by(
            categoria_id=cat.id, activo=True
        ).order_by(Estudio.nombre).all()

        if estudios:
            resultado.append({
                'categoria': cat.nombre,
                'color': cat.color,
                'estudios': [{
                    'codigo': e.codigo,
                    'nombre': e.nombre,
                    'precio': float(e.precio),
                    'requiere_preparacion': e.requiere_preparacion
                } for e in estudios]
            })

    return jsonify({'lista_precios': resultado})
