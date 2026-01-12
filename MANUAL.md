# MANUAL DE DESPLIEGUE
## HOSPITAL CORE MIDDLEWARE - BASE DE DATOS HETEROGENEA

Este documento describe el proceso completo de **despliegue, configuración y operación** del sistema de interconexión de bases de datos hospitalarias sobre **Oracle Linux 8**, diseñado para operar bajo **restricciones severas de recursos**.

---

## 1. ESPECIFICACIONES DE LA INFRAESTRUCTURA

El sistema se ejecuta al límite de la capacidad del hardware para maximizar el aprovechamiento de recursos.

- **Imagen ISO:** Oracle Linux R8 U10 x86_64  
- **Memoria RAM:** 3.5 GB  
  - Umbral mínimo operativo para Oracle Database
- **Almacenamiento:** 70 GB  
  - Partición dinámica
- **CPU:** 1 Core
- **Acceso remoto:** SSH (Puerto 22)
- **Credenciales de la VM:**
  - Usuario: `oracle`
  - Password: `oracle`

---

## 2. ESTRUCTURA DEL PROYECTO

Organización lógica del proyecto por capas funcionales:

```plaintext
├── base_de_datos/         # Esquemas SQL (Tablas, Constraints, Índices)
├── creacion_datos/        # Scripts de automatización de datos (Python)
├── documentos/            # Diagramas de clases y manuales adicionales
├── instalacion/           # Binarios y automatización de motores (Bash)
│   ├── mariadb/           # Configuración – Puerto 4000
│   ├── oracle/            # Configuración – Puerto 3000
│   └── sqlserver/         # Configuración – Puerto 5000
├── interconexion/         # Middleware UI (Streamlit)
└── README.md              # Documentación rápida
```
---

## 3. FASE DE INSTALACIÓN (ORDEN CRÍTICO)

**No alterar el orden de ejecución.**  
El consumo de memoria está orquestado para evitar bloqueos del kernel.

### 3.1 Reparación y Pre-configuración del Sistema

```bash
cd creacion_datos && bash 00_pre_config.sh
cd ../instalacion && bash 00_preparacion_sistema.sh
```

### 3.2 Instalación de Motores de Base de Datos

Acceder a cada subdirectorio y ejecutar los scripts **en orden estricto**.

#### MariaDB
1. `01_instalacion_mariadb.sh`
2. `02_comprobacion_mariadb.sh`

#### SQL Server
- Ejecutar los scripts `01` al `04` en secuencia

#### Oracle Database
- Ejecutar los scripts `01` al `03`
- Verificar que el **SID** configurado sea el correcto

### 3.3 Finalización de la Instalación

```bash
cd instalacion && bash 01_post_instalacion.sh
```

---

## 🗄️ 4. CONFIGURACIÓN DE LA CAPA DE DATOS

Conectarse desde **VSCode** usando la extensión **Database Client / SQLTools** con los siguientes parámetros:

| Parámetro | MariaDB | SQL Server | Oracle DB |
|----------|---------|------------|-----------|
| Host | 127.0.0.1 / IP | 127.0.0.1 / IP | 127.0.0.1 / IP |
| Puerto | 4000 | 5000 | 3000 |
| Usuario | dba_proyecto | dba_proyecto | dba_proyecto |
| Password | password_proyecto | Password_proyecto123 | password_proyecto |
| DB / Service | gestion_administrativa | gestion_citas | XEPDB1 |

### Acción requerida

Ejecutar los archivos `.sql` ubicados en `base_de_datos/` **en cada motor**, creando las tablas:

- `pacientes`
- `profesionales`
- `citas`
- `historial_atenciones`

---

## 5. POBLADO Y VALIDACIÓN DE DATOS

Ejecución de scripts de carga inicial y verificación de interconexión:

```bash
cd creacion_datos
python3 01_check_dependencias.py
python3 02_poblar_datos.py
python3 03_check_datos.py
```

---

## 6. LANZAMIENTO DEL MIDDLEWARE

Inicio de la aplicación de interconexión unificada:

```bash
cd interconexion
streamlit run app.py
```

---

## FUNCIONALIDADES DEL MIDDLEWARE

### Consulta
- Join virtual entre:
  - Historial de citas (SQL Server)
  - Evoluciones clínicas (Oracle)
- Visualización completa del historial del paciente

### Registro
- Alta integral de pacientes
- Validación previa en MariaDB para evitar duplicados
- Control de integridad referencial

### Panel Lateral
- Estado en tiempo real de cada motor
- Conteo de registros por tabla
- Monitorización básica del sistema

---

## NOTAS TÉCNICAS Y RIESGOS

- **Memoria:**  
  Fallos de conexión a Oracle suelen indicar problemas de asignación del SGA.  
  Revisar `alert.log`.

- **Seguridad:**  
  El puerto 5000 (SQL Server) requiere reglas de firewall activas para accesos externos.

- **Consistencia:**  
  El sistema no implementa transacciones distribuidas (XA).  
  Un fallo parcial puede generar datos huérfanos.  
  Se recomienda auditoría periódica.

---

## FIN DEL DOCUMENTO

