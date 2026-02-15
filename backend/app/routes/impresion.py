from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from app import db
from app.models import Factura, Paciente, Orden
from app.services.impresion_service import ImpresionService
from app.services.qr_service import QRService

bp = Blueprint('impresion', __name__)

@bp.route('/factura/<int:factura_id>', methods=['GET'])
@jwt_required()
def imprimir_factura(factura_id):
    """Generar PDF de factura para impresora 80mm"""
    factura = Factura.query.get_or_404(factura_id)
    
    # Generar QR si no existe
    qr_existe = db.session.execute(
        "SELECT codigo_qr FROM facturas_qr WHERE factura_id = :fid",
        {'fid': factura_id}
    ).first()
    
    if not qr_existe:
        QRService.registrar_qr_factura(factura_id)
    
    # Generar PDF
    pdf_buffer = ImpresionService.generar_factura_80mm(factura)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'factura_{factura.numero_factura}_80mm.pdf'
    )

@bp.route('/etiqueta/<int:orden_id>/<int:detalle_id>', methods=['GET'])
@jwt_required()
def imprimir_etiqueta(orden_id, detalle_id):
    """Generar etiqueta para muestra"""
    from app.models import OrdenDetalle
    
    orden = Orden.query.get_or_404(orden_id)
    detalle = OrdenDetalle.query.get_or_404(detalle_id)
    paciente = orden.paciente
    
    estudio_nombre = detalle.estudio.nombre if detalle.estudio else 'Estudio'
    
    pdf_buffer = ImpresionService.generar_etiqueta_muestra(paciente, orden, estudio_nombre)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'etiqueta_{paciente.codigo_paciente}.pdf'
    )
