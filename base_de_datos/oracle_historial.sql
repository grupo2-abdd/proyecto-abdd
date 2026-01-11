-- Ejecutar en Oracle (Usuario dba_proyecto en XEPDB1)

-- Limpieza (ignoramos error si no existe)
BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE historial_atenciones';
EXCEPTION
   WHEN OTHERS THEN
      IF SQLCODE != -942 THEN
         RAISE;
      END IF;
END;
/

-- Estructura
CREATE TABLE historial_atenciones (
    atencion_id NUMBER PRIMARY KEY, 
    cita_id NUMBER NOT NULL,      -- Relación lógica con SQL Server
    paciente_id NUMBER NOT NULL,  -- Relación lógica con MariaDB
    fecha_atencion TIMESTAMP, 
    diagnostico VARCHAR2(200), 
    tratamiento VARCHAR2(200)
);
