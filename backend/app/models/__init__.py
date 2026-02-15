from datetime import datetime
from app import db
import uuid

class Paciente(db.Model):
    __tablename__ = 'pacientes'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    cedula = db.Column(db.String(20), unique=True)
    pasaporte = db.Column(db.String(30))
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date)
    sexo = db.Column(db.String(1))
    telefono = db.Column(db.String(20))
    celular = db.Column(db.String(20))
    email = db.Column(db.String(100))
    direccion = db.Column(db.Text)
    ciudad = db.Column(db.String(100))
    seguro_medico = db.Column(db.String(100))
    numero_poliza = db.Column(db.String(50))
    tipo_sangre = db.Column(db.String(5))
    alergias = db.Column(db.Text)
    notas_medicas = db.Column(db.Text)
    estado = db.Column(db.String(20), default='activo')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    ordenes = db.relationship('Orden', back_populates='paciente', lazy='dynamic')
    facturas = db.relationship('Factura', back_populates='paciente', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'cedula': self.cedula,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'nombre_completo': f"{self.nombre} {self.apellido}",
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'sexo': self.sexo,
            'telefono': self.telefono,
            'celular': self.celular,
            'email': self.email,
            'direccion': self.direccion,
            'seguro_medico': self.seguro_medico,
            'estado': self.estado
        }


class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    rol = db.Column(db.String(20), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    ultimo_acceso = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'email': self.email,
            'rol': self.rol,
            'activo': self.activo
        }


class CategoriaEstudio(db.Model):
    __tablename__ = 'categorias_estudios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    color = db.Column(db.String(7))
    icono = db.Column(db.String(50))
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    estudios = db.relationship('Estudio', back_populates='categoria', lazy='dynamic')


class Estudio(db.Model):
    __tablename__ = 'estudios'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias_estudios.id'))
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    costo = db.Column(db.Numeric(10, 2))
    tiempo_estimado = db.Column(db.Integer)
    requiere_preparacion = db.Column(db.Boolean, default=False)
    instrucciones_preparacion = db.Column(db.Text)
    tipo_resultado = db.Column(db.String(20))
    equipo_asignado = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    categoria = db.relationship('CategoriaEstudio', back_populates='estudios')
    
    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'categoria': self.categoria.nombre if self.categoria else None,
            'precio': float(self.precio),
            'tipo_resultado': self.tipo_resultado,
            'activo': self.activo
        }


class Orden(db.Model):
    __tablename__ = 'ordenes'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    numero_orden = db.Column(db.String(20), unique=True, nullable=False)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    medico_referente = db.Column(db.String(100))
    fecha_orden = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_cita = db.Column(db.DateTime)
    estado = db.Column(db.String(20), default='pendiente')
    prioridad = db.Column(db.String(20), default='normal')
    observaciones = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    paciente = db.relationship('Paciente', back_populates='ordenes')
    detalles = db.relationship('OrdenDetalle', back_populates='orden', lazy='dynamic', cascade='all, delete-orphan')
    factura = db.relationship('Factura', back_populates='orden', uselist=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero_orden': self.numero_orden,
            'paciente': self.paciente.to_dict() if self.paciente else None,
            'fecha_orden': self.fecha_orden.isoformat(),
            'estado': self.estado,
            'total_estudios': self.detalles.count()
        }


class OrdenDetalle(db.Model):
    __tablename__ = 'orden_detalles'
    
    id = db.Column(db.Integer, primary_key=True)
    orden_id = db.Column(db.Integer, db.ForeignKey('ordenes.id'), nullable=False)
    estudio_id = db.Column(db.Integer, db.ForeignKey('estudios.id'), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    descuento = db.Column(db.Numeric(10, 2), default=0)
    precio_final = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(db.String(20), default='pendiente')
    resultado_disponible = db.Column(db.Boolean, default=False)
    fecha_resultado = db.Column(db.DateTime)
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    orden = db.relationship('Orden', back_populates='detalles')
    estudio = db.relationship('Estudio')
    resultados = db.relationship('Resultado', back_populates='orden_detalle', lazy='dynamic')


class NCFSecuencia(db.Model):
    __tablename__ = 'ncf_secuencias'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_comprobante = db.Column(db.String(20), nullable=False)
    serie = db.Column(db.String(3), nullable=False)
    secuencia_inicio = db.Column(db.BigInteger, nullable=False)
    secuencia_fin = db.Column(db.BigInteger, nullable=False)
    secuencia_actual = db.Column(db.BigInteger, nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Factura(db.Model):
    __tablename__ = 'facturas'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    numero_factura = db.Column(db.String(30), unique=True, nullable=False)
    ncf = db.Column(db.String(19))
    tipo_comprobante = db.Column(db.String(3))
    orden_id = db.Column(db.Integer, db.ForeignKey('ordenes.id'))
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    fecha_factura = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_vencimiento = db.Column(db.Date)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    descuento = db.Column(db.Numeric(10, 2), default=0)
    itbis = db.Column(db.Numeric(10, 2), default=0)
    otros_impuestos = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(db.String(20), default='pendiente')
    forma_pago = db.Column(db.String(30))
    notas = db.Column(db.Text)
    usuario_emision_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    paciente = db.relationship('Paciente', back_populates='facturas')
    orden = db.relationship('Orden', back_populates='factura')
    detalles = db.relationship('FacturaDetalle', back_populates='factura', lazy='dynamic', cascade='all, delete-orphan')
    pagos = db.relationship('Pago', back_populates='factura', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'numero_factura': self.numero_factura,
            'ncf': self.ncf,
            'fecha_factura': self.fecha_factura.isoformat(),
            'paciente': self.paciente.to_dict() if self.paciente else None,
            'subtotal': float(self.subtotal),
            'descuento': float(self.descuento),
            'itbis': float(self.itbis),
            'total': float(self.total),
            'estado': self.estado,
            'forma_pago': self.forma_pago
        }


class FacturaDetalle(db.Model):
    __tablename__ = 'factura_detalles'
    
    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas.id'), nullable=False)
    orden_detalle_id = db.Column(db.Integer, db.ForeignKey('orden_detalles.id'))
    descripcion = db.Column(db.String(255), nullable=False)
    cantidad = db.Column(db.Integer, default=1)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    descuento = db.Column(db.Numeric(10, 2), default=0)
    itbis = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    factura = db.relationship('Factura', back_populates='detalles')


class Pago(db.Model):
    __tablename__ = 'pagos'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas.id'))
    fecha_pago = db.Column(db.DateTime, default=datetime.utcnow)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    metodo_pago = db.Column(db.String(30), nullable=False)
    referencia = db.Column(db.String(100))
    banco = db.Column(db.String(100))
    notas = db.Column(db.Text)
    usuario_recibe_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    factura = db.relationship('Factura', back_populates='pagos')


class Resultado(db.Model):
    __tablename__ = 'resultados'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    orden_detalle_id = db.Column(db.Integer, db.ForeignKey('orden_detalles.id'))
    tipo_archivo = db.Column(db.String(10))
    ruta_archivo = db.Column(db.String(500))
    ruta_nube = db.Column(db.String(500))
    nombre_archivo = db.Column(db.String(255))
    tamano_bytes = db.Column(db.BigInteger)
    hash_archivo = db.Column(db.String(64))
    estado_validacion = db.Column(db.String(20), default='pendiente')
    fecha_importacion = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    orden_detalle = db.relationship('OrdenDetalle', back_populates='resultados')


class Configuracion(db.Model):
    __tablename__ = 'configuracion'
    
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(100), unique=True, nullable=False)
    valor = db.Column(db.Text)
    tipo = db.Column(db.String(20))
    descripcion = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
