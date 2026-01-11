-- Ejecutar en SQL Server (Puerto 5000)
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'gestion_citas')
    CREATE DATABASE gestion_citas;
GO

USE gestion_citas;
GO

-- Limpieza
IF OBJECT_ID('citas', 'U') IS NOT NULL 
    DROP TABLE citas;
GO

-- Estructura
CREATE TABLE citas (
    cita_id INT PRIMARY KEY, 
    paciente_id INT NOT NULL, -- Relación lógica con MariaDB
    medico_id INT NOT NULL,   -- Relación lógica con MariaDB
    fecha_cita DATETIME, 
    estado VARCHAR(20)        -- Programada, Completada, Cancelada
);
