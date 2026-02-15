from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Resultado, OrdenDetalle

bp = Blueprint('resultados', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def listar_resultados():
    orden_id = request.args.get('orden_id', type=int)
    query = Resultado.query
    if orden_id:
        query = query.join(OrdenDetalle).filter(OrdenDetalle.orden_id == orden_id)
    resultados = query.order_by(Resultado.fecha_importacion.desc()).limit(50).all()
    return jsonify({'resultados': [{'id': r.id, 'tipo_archivo': r.tipo_archivo, 'nombre_archivo': r.nombre_archivo, 'fecha': r.fecha_importacion.isoformat()} for r in resultados]})
