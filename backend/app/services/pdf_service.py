from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime
import os

class PDFService:
    
    @staticmethod
    def generar_factura_pdf(factura, output_path):
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#2c3e50'), spaceAfter=30, alignment=TA_CENTER)
        elements.append(Paragraph("CENTRO DIAGNÓSTICO", title_style))
        elements.append(Paragraph("FACTURA", title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Info factura
        info_data = [
            ["Factura:", factura.numero_factura, "Fecha:", factura.fecha_factura.strftime('%d/%m/%Y')],
            ["NCF:", factura.ncf or 'N/A', "Estado:", factura.estado.upper()]
        ]
        info_table = Table(info_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2*inch])
        info_table.setStyle(TableStyle([
            ('FONT', (0,0), (-1,-1), 'Helvetica-Bold', 10),
            ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Info paciente
        paciente = factura.paciente
        elements.append(Paragraph(f"<b>Paciente:</b> {paciente.nombre} {paciente.apellido}", styles['Normal']))
        elements.append(Paragraph(f"<b>Cédula:</b> {paciente.cedula or 'N/A'}", styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Detalles
        detalles_data = [["Descripción", "Cantidad", "Precio Unit.", "Total"]]
        for detalle in factura.detalles:
            detalles_data.append([
                detalle.descripcion,
                str(detalle.cantidad),
                f"RD$ {float(detalle.precio_unitario):,.2f}",
                f"RD$ {float(detalle.total):,.2f}"
            ])
        
        detalles_table = Table(detalles_data, colWidths=[3.5*inch, 1*inch, 1.5*inch, 1.5*inch])
        detalles_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
            ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 12),
            ('FONT', (0,1), (-1,-1), 'Helvetica', 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ]))
        elements.append(detalles_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Totales
        totales_data = [
            ["Subtotal:", f"RD$ {float(factura.subtotal):,.2f}"],
            ["Descuento:", f"RD$ {float(factura.descuento):,.2f}"],
            ["ITBIS:", f"RD$ {float(factura.itbis):,.2f}"],
            ["TOTAL:", f"RD$ {float(factura.total):,.2f}"]
        ]
        totales_table = Table(totales_data, colWidths=[5*inch, 2*inch])
        totales_table.setStyle(TableStyle([
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
            ('FONT', (0,-1), (-1,-1), 'Helvetica-Bold', 14),
            ('TEXTCOLOR', (0,-1), (-1,-1), colors.HexColor('#27ae60')),
            ('LINEABOVE', (0,-1), (-1,-1), 2, colors.black),
        ]))
        elements.append(totales_table)
        
        doc.build(elements)
        return output_path
