#!/bin/bash
# Script para resolver el error 208 (Objeto no encontrado)
SQL_CMD="/opt/mssql-tools/bin/sqlcmd"
SA_PASS="Password_proyecto123"

echo "--- [USUARIO DBA SQL SERVER] ---"

$SQL_CMD -S 127.0.0.1,5000 -U sa -P "$SA_PASS" -Q "
-- 1. Asegurar que la base de datos existe y usarla
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'gestion_citas') 
    CREATE DATABASE gestion_citas;
GO

USE gestion_citas;
GO

-- 2. Asegurar que el Login dba_proyecto tiene acceso a esta DB
IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'dba_proyecto')
    CREATE USER dba_proyecto FOR LOGIN dba_proyecto;

-- 3. Darle permisos de propietario para que vea todo
ALTER ROLE db_owner ADD MEMBER dba_proyecto;
GO

-- 4. Crear la tabla explícitamente en el esquema dbo
IF OBJECT_ID('dbo.citas', 'U') IS NOT NULL DROP TABLE dbo.citas;

CREATE TABLE dbo.citas (
    cita_id INT PRIMARY KEY, 
    paciente_id INT NOT NULL, 
    medico_id INT NOT NULL, 
    fecha_cita DATETIME, 
    estado VARCHAR(20)
);
GO
"

echo "--- [VERIFICACIÓN DE ESQUEMA] ---"
$SQL_CMD -S 127.0.0.1,5000 -U dba_proyecto -P "Password_proyecto123" -d "gestion_citas" -Q "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'citas';"
