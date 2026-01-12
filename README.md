# Proyecto Integrador - Creación, población y despliegue de una base de datos heterogénea

**Carrera:** Ingeniería en Ciberseguridad  
**Institución:** Universidad de las Américas (UDLA)  
**Materia:** Administración de Bases de Datos  

---

## Integrantes
* Cisneros Edgar
* Freire Anderson
* Toscano Jhon
* Velasquez Alex

---

## Descripción del Proyecto
Este proyecto aborda la complejidad de gestionar un entorno de **Base de Datos Heterogénea y Federada**. El enfoque principal no es la temática operativa (Hospital), sino el desafío técnico de la **administración multi-motor**. 

Se ha diseñado un ecosistema donde tres motores distintos (MariaDB, SQL Server y Oracle) operan de forma independiente pero coordinada. El flujo de trabajo abarca:
1.  **Creación:** Despliegue automatizado de esquemas mediante scripts Bash y SQL en puertos no estándar para endurecer la seguridad.
2.  **Población:** Implementación de lógica de inserción masiva mediante Python, gestionando la integridad referencial a nivel de aplicación (Foreign Keys lógicas).
3.  **Interconexión:** Desarrollo de una capa de middleware que unifica los motores para permitir consultas transversales y transacciones distribuidas.

---

## Acceso a la Máquina Virtual (VM)
La infraestructura completa configurada en Oracle Linux 8 se encuentra disponible para su despliegue:
* **Enlace de descarga:** [Máquina virtual configurada](https://drive.google.com/file/d/1dl4nUn5MffcKvJ3jk29QvVmR-uKywaW1/view?usp=sharing)

---

## Arquitectura de Base de Datos 
Aunque los motores están separados, los datos están unidos por una lógica de negocio que Python administrará.

| Base de Datos | Motor | Puerto | Entidad | Rol Estratégico |
| :--- | :--- | :--- | :--- | :--- |
| **Administrativa** | MariaDB | 4000 | Pacientes, Profesionales | **Fuente de Verdad.** Datos maestros que identifican a las personas. |
| **Citas** | SQL Server | 5000 | Citas | **Transaccional.** Controla el flujo de tiempo y estados de atención. |
| **Clínica** | Oracle XE | 3000 | Historial_Atenciones | **Carga Crítica.** Almacena el volumen masivo de datos médicos. |


---

## Estructura de Tablas (Esquema Lógico)

### 1. MariaDB (Gestión Administrativa)
* **pacientes:** `paciente_id (PK)`, `nombre`, `fecha_nacimiento`, `genero`, `telefono`.
* **profesionales:** `medico_id (PK)`, `nombre`, `especialidad`, `licencia`.

### 2. SQL Server (Gestión de Citas)
* **citas:** `cita_id (PK)`, `paciente_id (FK Lógica)`, `medico_id (FK Lógica)`, `fecha_cita`, `estado`.

### 3. Oracle XE (Gestión Clínica)
* **historial_atenciones:** `atencion_id (PK)`, `cita_id (FK Lógica)`, `paciente_id (FK Lógica)`, `fecha_atencion`, `diagnostico`, `tratamiento`.

---

## Diagrama de Clases
![Diagrama de clases](https://raw.githubusercontent.com/grupo2-abdd/proyecto-abdd/refs/heads/main/documentos/diagrama_clases.png)
---

## Estructura del Proyecto
```text
├── base_de_datos
│   ├── mariadb_hospital.sql
│   ├── oracle_historial.sql
│   └── sqlserver_citas.sql
├── creacion_datos
│   ├── 00_pre_config.sh
│   ├── 01_check_dependencias.py
│   ├── 02_poblar_datos.py
│   └── 03_check_datos.py
├── documentos
│   ├── diagrama_clases.png
│   ├── diagrama_clases.txt
│   └── MANUAL.md  // MANUAL DE CONFIGURACIÓN Y DESPLIEGUE DEL SISTEMA
├── instalacion
│   ├── 00_preparacion_sistema.sh
│   ├── 01_post_instalacion.sh
│   ├── mariadb
│   │   ├── 01_instalacion_mariadb.sh
│   │   └── 02_comprobacion_mariadb.sh
│   ├── oracle
│   │   ├── 01_instalacion_oracle.sh
│   │   ├── 02_instalacion_oracle.sh
│   │   └── 03_comprobacion_oracle.sh
│   └── sqlserver
│       ├── 01_instalacion_sqlserver.sh
│       ├── 02_configuracion_sqlserver.sh
│       ├── 03_configuracion_sqlserver.sh
│       └── 04_comprobracion_sqlserver.sh
├── interconexion
│   └── app.py
└── README.md
