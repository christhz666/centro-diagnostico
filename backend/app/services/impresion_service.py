from reportlab.lib.pagesizes import mm
from reportlab.lib.units import mm as MM
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import qrcode
from datetime import datetime

class ImpresionService:
    
    @staticmethod
    def generar_factura_80mm(factura):
        """Generar factura para impresora térmica 80x80mm"""
        # Tamaño papel: 80mm ancho, largo variable
        ancho = 80 * MM
        alto = 200 * MM  # Ajustable según contenido
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=(ancho, alto))
        
        # Posición Y inicial
        y = alto - 10*MM
        
        # Header
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(ancho/2, y, "CENTRO DIAGNÓSTICO")
        y -= 5*MM
        
        c.setFont("Helvetica", 8)
        c.drawCentredString(ancho/2, y, "RNC: 123-45678-9")
        y -= 4*MM
        c.drawCentredString(ancho/2, y, "Tel: 809-555-1234")
        y -= 6*MM
        
        # Línea separadora
        c.line(5*MM, y, ancho-5*MM, y)
        y -= 5*MM
        
        # Info factura
        c.setFont("Helvetica-Bold", 9)
        c.drawString(5*MM, y, f"Factura: {factura.numero_factura}")
        y -= 4*MM
        c.setFont("Helvetica", 8)
        c.drawString(5*MM, y, f"NCF: {factura.ncf or 'N/A'}")
        y -= 4*MM
        c.drawString(5*MM, y, f"Fecha: {factura.fecha_factura.strftime('%d/%m/%Y %H:%M')}")
        y -= 6*MM
        
        # Info paciente
        c.setFont("Helvetica-Bold", 8)
        c.drawString(5*MM, y, "PACIENTE:")
        y -= 4*MM
        c.setFont("Helvetica", 8)
        paciente = factura.paciente
        c.drawString(5*MM, y, f"{paciente.nombre} {paciente.apellido}")
        y -= 3.5*MM
        c.drawString(5*MM, y, f"Cédula: {paciente.cedula or 'N/A'}")
        y -= 3.5*MM
        c.drawString(5*MM, y, f"Código: {paciente.codigo_paciente}")
        y -= 6*MM
        
        # Línea
        c.line(5*MM, y, ancho-5*MM, y)
        y -= 5*MM
        
        # Detalles
        c.setFont("Helvetica-Bold", 8)
        c.drawString(5*MM, y, "DESCRIPCIÓN")
        c.drawRightString(ancho-5*MM, y, "TOTAL")
        y -= 4*MM
        c.line(5*MM, y, ancho-5*MM, y)
        y -= 4*MM
        
        c.setFont("Helvetica", 7)
        for detalle in factura.detalles:
            c.drawString(5*MM, y, detalle.descripcion[:35])
            c.drawRightString(ancho-5*MM, y, f"RD$ {float(detalle.total):,.2f}")
            y -= 3.5*MM
        
        y -= 2*MM
        c.line(5*MM, y, ancho-5*MM, y)
        y -= 5*MM
        
        # Totales
        c.setFont("Helvetica-Bold", 9)
        c.drawString(5*MM, y, "TOTAL:")
        c.drawRightString(ancho-5*MM, y, f"RD$ {float(factura.total):,.2f}")
        y -= 6*MM
        
        # Código QR
        qr_data = f"http://192.9.135.84:3000/portal-paciente?factura={factura.id}"
        qr = qrcode.QRCode(version=1, box_size=2, border=1)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir QR a imagen para reportlab
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        # Dibujar QR centrado
        qr_size = 20*MM
        c.drawImage(ImageReader(qr_buffer), (ancho-qr_size)/2, y-qr_size, qr_size, qr_size)
        y -= qr_size + 3*MM
        
        # Texto QR
        c.setFont("Helvetica", 6)
        c.drawCentredString(ancho/2, y, "Escanea para ver tus resultados")
        y -= 4*MM
        
        # Credenciales portal
        if paciente.portal_usuario:
            c.drawCentredString(ancho/2, y, f"Usuario: {paciente.portal_usuario}")
            y -= 3*MM
            c.drawCentredString(ancho/2, y, "Contraseña: (enviada por SMS)")
        
        y -= 5*MM
        c.drawCentredString(ancho/2, y, "¡Gracias por su visita!")
        
        c.save()
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generar_etiqueta_muestra(paciente, orden, estudio_nombre):
        """Generar etiqueta para tubo de muestra"""
        # Tamaño típico: 50mm x 25mm
        ancho = 50 * MM
        alto = 25 * MM
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=(ancho, alto))
        
        # Código de barras (usando el código del paciente)
        from reportlab.graphics.barcode import code128
        barcode = code128.Code128(paciente.codigo_paciente, barHeight=8*MM, barWidth=0.3*MM)
        barcode.drawOn(c, 2*MM, alto-12*MM)
        
        # Info paciente
        c.setFont("Helvetica-Bold", 8)
        c.drawString(2*MM, alto-14*MM, f"{paciente.nombre} {paciente.apellido}")
        
        c.setFont("Helvetica", 6)
        c.drawString(2*MM, alto-17*MM, f"Código: {paciente.codigo_paciente}")
        c.drawString(2*MM, alto-20*MM, f"Orden: {orden.numero_orden}")
        c.drawString(2*MM, alto-23*MM, f"Estudio: {estudio_nombre[:20]}")
        
        # Fecha
        c.drawRightString(ancho-2*MM, alto-23*MM, datetime.now().strftime('%d/%m/%Y'))
        
        c.save()
        buffer.seek(0)
        return buffer
