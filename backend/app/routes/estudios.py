from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Estudio, CategoriaEstudio

bp = Blueprint('estudios', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def listar_estudios():
    categoria_id = request.args.get('categoria_id', type=int)
    query = Estudio.query.filter_by(activo=True)
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)
    estudios = query.order_by(Estudio.nombre).all()
    return jsonify({'estudios': [e.to_dict() for e in estudios], 'total': len(estudios)})

@bp.route('/<int:estudio_id>', methods=['GET'])
@jwt_required()
def obtener_estudio(estudio_id):
    estudio = Estudio.query.get_or_404(estudio_id)
    return jsonify(estudio.to_dict())

@bp.route('/categorias', methods=['GET'])
@jwt_required()
def listar_categorias():
    categorias = CategoriaEstudio.query.filter_by(activo=True).all()
    return jsonify({'categorias': [{'id': c.id, 'nombre': c.nombre, 'descripcion': c.descripcion} for c in categorias]})
