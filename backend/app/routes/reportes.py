from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Factura, Orden, Paciente, Estudio
from sqlalchemy import func, extract
from datetime import datetime, timedelta

bp = Blueprint('reportes', __name__)

@bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    hoy = datetime.now().date()
    inicio_mes = hoy.replace(day=1)
    
    # Facturas del mes
    facturas_mes = Factura.query.filter(
        extract('year', Factura.fecha_factura) == hoy.year,
        extract('month', Factura.fecha_factura) == hoy.month,
        Factura.estado != 'anulada'
    ).all()
    
    total_mes = sum(float(f.total) for f in facturas_mes)
    facturas_pendientes = len([f for f in facturas_mes if f.estado in ['pendiente', 'parcial']])
    
    # Órdenes pendientes
    ordenes_pendientes = Orden.query.filter(Orden.estado.in_(['pendiente', 'en_proceso'])).count()
    
    # Pacientes registrados
    total_pacientes = Paciente.query.filter_by(estado='activo').count()
    
    return jsonify({
        'ventas_mes': total_mes,
        'facturas_mes': len(facturas_mes),
        'facturas_pendientes': facturas_pendientes,
        'ordenes_pendientes': ordenes_pendientes,
        'total_pacientes': total_pacientes
    })

@bp.route('/ventas', methods=['GET'])
@jwt_required()
def reporte_ventas():
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    if not fecha_inicio or not fecha_fin:
        return jsonify({'error': 'Se requieren fecha_inicio y fecha_fin'}), 400
    
    fecha_inicio = datetime.fromisoformat(fecha_inicio)
    fecha_fin = datetime.fromisoformat(fecha_fin)
    
    facturas = Factura.query.filter(
        Factura.fecha_factura >= fecha_inicio,
        Factura.fecha_factura <= fecha_fin,
        Factura.estado != 'anulada'
    ).all()
    
    total_ventas = sum(float(f.total) for f in facturas)
    total_itbis = sum(float(f.itbis) for f in facturas)
    
    return jsonify({
        'fecha_inicio': fecha_inicio.isoformat(),
        'fecha_fin': fecha_fin.isoformat(),
        'total_ventas': total_ventas,
        'total_itbis': total_itbis,
        'cantidad_facturas': len(facturas)
    })
