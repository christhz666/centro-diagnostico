# 🏥 Centro Diagnóstico - Sistema de Gestión Integral

Sistema híbrido (local + nube) para gestión completa de centros diagnósticos con integración automática de equipos médicos y facturación con NCF para República Dominicana.

![Status](https://img.shields.io/badge/Status-En%20Desarrollo-yellow)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue)
![License](https://img.shields.io/badge/License-Propietario-red)

---

## ✨ Características Principales

### ✅ Implementado (Fase 1)
- 💰 **Sistema de Facturación Completo**
  - Generación automática de NCF (Números de Comprobante Fiscal)
  - Cálculo automático de ITBIS (18%)
  - Múltiples métodos de pago (efectivo, tarjeta, transferencia, seguro)
  - Control de pagos parciales
  - Anulación de facturas con motivo
  - Reportes de ventas y cuentas por cobrar

- 🔐 **Seguridad y Autenticación**
  - JWT (JSON Web Tokens) para autenticación
  - Roles de usuario (admin, cajero, técnico, médico, recepción)
  - Auditoría completa de acciones

- 🗄️ **Base de Datos Robusta**
  - PostgreSQL con schema completo
  - Triggers y funciones automatizadas
  - Índices optimizados para búsquedas rápidas
  - Integridad referencial completa

### 🔄 En Desarrollo (Fase 2)
- 👥 Gestión completa de pacientes
- 📋 Órdenes de servicio y seguimiento
- 🔬 Catálogo de estudios
- 📁 Monitor de archivos de equipos

### 📅 Planificado (Fases 3-4)
- 🧬 Parser HL7 para resultados de laboratorio
- 🖼️ Visor DICOM para imágenes médicas
- ☁️ Sincronización automática con nube (AWS/Azure)
- 📊 Dashboard con reportes avanzados
- 📱 Aplicación móvil

---

## 🚀 Inicio Rápido

### Requisitos Previos

```bash
✓ Ubuntu 20.04+ / Windows 10+ / macOS 10.15+
✓ Python 3.9+
✓ PostgreSQL 13+
✓ Redis 6+ (opcional, para tareas asíncronas)
✓ Node.js 16+ (para frontend en próxima fase)
```

### Instalación Automática

```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd centro-diagnostico

# Ejecutar script de instalación
chmod +x setup.sh
./setup.sh
```

El script automáticamente:
1. Verifica dependencias
2. Crea entorno virtual Python
3. Instala dependencias
4. Configura variables de entorno
5. Crea base de datos PostgreSQL
6. Ejecuta el schema SQL

### Instalación Manual

Si prefieres instalar manualmente, consulta la [documentación completa](docs/README.md).

### Ejecutar el Sistema

```bash
cd backend
source venv/bin/activate  # En Windows: venv\Scripts\activate
python app.py
```

El servidor estará disponible en: **http://localhost:5000**

---

## 📚 Documentación

- **[Documentación Completa](docs/README.md)** - Guía técnica completa
- **[API Reference](docs/API.md)** - Documentación de endpoints (próximamente)
- **[Manual de Usuario](docs/USER_MANUAL.md)** - Guía de uso (próximamente)

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                  FRONTEND (React)                        │
│         [Facturación] [Pacientes] [Órdenes]             │
└─────────────────────────────────────────────────────────┘
                         ↕ REST API
┌─────────────────────────────────────────────────────────┐
│                 BACKEND (Flask/Python)                   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  API Endpoints & Servicios de Negocio           │   │
│  │  - Facturación (✅)                              │   │
│  │  - Integración Equipos (🔄)                     │   │
│  │  - Sincronización Nube (📅)                     │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────────┐
│              BASE DE DATOS (PostgreSQL)                  │
│  Pacientes | Órdenes | Facturas | Resultados           │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Estructura del Proyecto

```
centro-diagnostico/
├── backend/              # API Backend (Python/Flask)
│   ├── app/
│   │   ├── models/       # Modelos de base de datos
│   │   ├── routes/       # Endpoints API
│   │   ├── services/     # Lógica de negocio
│   │   └── utils/        # Utilidades
│   ├── app.py           # Aplicación principal
│   ├── config.py        # Configuraciones
│   └── requirements.txt # Dependencias
├── database/            # Schema y migraciones
│   └── schema.sql       # Schema completo
├── frontend/            # Frontend React (próxima fase)
├── docs/                # Documentación
│   └── README.md        # Documentación técnica
├── setup.sh            # Script de instalación
└── README.md           # Este archivo
```

---

## 🔌 API Endpoints

### Autenticación
```
POST /api/auth/login          - Iniciar sesión
POST /api/auth/refresh        - Renovar token
GET  /api/auth/me             - Usuario actual
```

### Facturas
```
GET    /api/facturas/                        - Listar facturas
GET    /api/facturas/<id>                    - Detalles de factura
POST   /api/facturas/crear-desde-orden/<id> - Crear desde orden
POST   /api/facturas/<id>/pagar              - Registrar pago
POST   /api/facturas/<id>/anular             - Anular factura
GET    /api/facturas/estado-cuenta/<id>     - Estado cuenta paciente
GET    /api/facturas/reporte-ventas         - Reporte de ventas
```

Consulta la [documentación completa](docs/README.md) para más detalles.

---

## 💡 Ejemplo de Uso

### 1. Autenticación

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Respuesta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "usuario": {
    "id": 1,
    "username": "admin",
    "rol": "admin"
  }
}
```

### 2. Crear Factura desde Orden

```bash
curl -X POST http://localhost:5000/api/facturas/crear-desde-orden/123 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_comprobante": "B02",
    "forma_pago": "tarjeta",
    "incluir_itbis": false
  }'
```

### 3. Registrar Pago

```bash
curl -X POST http://localhost:5000/api/facturas/1/pagar \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "monto": 2500.00,
    "metodo_pago": "efectivo"
  }'
```

---

## 🧪 Testing

```bash
# Ejecutar tests
cd backend
source venv/bin/activate
pytest

# Con coverage
pytest --cov=app
```

---

## 🛠️ Tecnologías

### Backend
- **Flask** - Framework web
- **SQLAlchemy** - ORM
- **PostgreSQL** - Base de datos
- **JWT** - Autenticación
- **Celery** - Tareas asíncronas
- **Redis** - Caché y cola

### Integraciones Médicas
- **pydicom** - Archivos DICOM
- **hl7apy** - Mensajes HL7
- **PyPDF2** - Documentos PDF
- **Watchdog** - Monitor de archivos

### DevOps (Próximamente)
- **Docker** - Containerización
- **Nginx** - Proxy reverso
- **GitHub Actions** - CI/CD

---

## 📈 Roadmap

### ✅ Fase 1 - Completada
- [x] Base de datos PostgreSQL
- [x] Sistema de facturación con NCF
- [x] Autenticación JWT
- [x] API REST básica

### 🔄 Fase 2 - En Desarrollo (Semanas 3-4)
- [ ] CRUD de pacientes
- [ ] CRUD de órdenes
- [ ] Monitor de archivos
- [ ] Frontend React básico

### 📅 Fase 3 - Planificada (Semanas 5-7)
- [ ] Parser HL7 automático
- [ ] Visor DICOM
- [ ] Asociación automática de resultados
- [ ] Dashboard de reportes

### 📅 Fase 4 - Futura (Semanas 8+)
- [ ] Sincronización con nube
- [ ] Aplicación móvil
- [ ] Portal para pacientes
- [ ] Integración con seguros

---

## 🤝 Contribuir

Este es un proyecto propietario. El acceso al código está restringido.

---

## 📞 Soporte

Para soporte técnico o consultas:
- **Email:** soporte@centrodiagnostico.com
- **Teléfono:** +1 (809) 000-0000

---

## 📄 Licencia

Copyright © 2025 Centro Diagnóstico. Todos los derechos reservados.

Este software es propietario y confidencial. El uso no autorizado está prohibido.

---

## 🙏 Agradecimientos

Sistema desarrollado específicamente para centros diagnósticos en República Dominicana, cumpliendo con todas las regulaciones de la DGII para facturación electrónica.

---

**¿Listo para comenzar?** Ejecuta `./setup.sh` y en minutos tendrás el sistema funcionando. 🚀
