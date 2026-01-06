# Ejecutar en la terminal de Linux
lsnrctl status | grep -E "PORT=3000|Instance \"XE\""


# Ejecutar en la terminal (usando la conexión de red para validar doblemente)
sqlplus dba_proyecto/password_proyecto@//localhost:3000/XEPDB1 <<EOF
SELECT USERNAME, ACCOUNT_STATUS FROM USER_USERS;
SELECT * FROM SESSION_PRIVS WHERE PRIVILEGE = 'CREATE TABLE';
EXIT;
EOF

3. Comprobación de la PDB Abierta (Disponibilidad)
Un error común es que la base de datos esté creada pero cerrada. Esto certifica que está lista para recibir datos.

SQL

-- Ejecutar dentro de sqlplus / as sysdba
COLUMN name FORMAT A15;
SELECT name, open_mode FROM v$pdbs WHERE name = 'XEPDB1';
