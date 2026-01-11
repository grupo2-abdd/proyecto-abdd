-- Ejecutar en MariaDB (Puerto 4000)
CREATE DATABASE IF NOT EXISTS gestion_administrativa;
USE gestion_administrativa;

-- Limpieza
DROP TABLE IF EXISTS profesionales;
DROP TABLE IF EXISTS pacientes;

-- Estructura
CREATE TABLE pacientes (
    paciente_id INT PRIMARY KEY, 
    nombre VARCHAR(100), 
    fecha_nacimiento DATE, 
    genero CHAR(1), 
    telefono VARCHAR(20)
);

CREATE TABLE profesionales (
    medico_id INT PRIMARY KEY, 
    nombre VARCHAR(100), 
    especialidad VARCHAR(50), 
    licencia VARCHAR(20)
);
