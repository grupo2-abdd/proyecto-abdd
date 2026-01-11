#!/bin/bash

echo "--- USUARIO DBA_PROYECTO EN SQL SERVER ---"

# Definir variables para fácil mantenimiento
SQL_SA_PASS="Password_proyecto123"
SQL_NEW_PASS="Password_proyecto123"
SQL_CMD="/opt/mssql-tools/bin/sqlcmd"

# 1. Comprobar si el servicio está activo en el puerto 5000
echo "[1/3] Verificando conectividad en puerto 5000..."
if ! nc -z localhost 5000; then
    echo "✘ ERROR: SQL Server no responde en el puerto 5000."
    echo "Ejecuta: sudo systemctl restart mssql-server"
    exit 1
fi

# 2. Ejecutar la reconfiguración del login
echo "[2/3] Ejecutando comandos T-SQL..."
$SQL_CMD -S localhost,5000 -U sa -P "$SQL_SA_PASS" -Q "
IF EXISTS (SELECT * FROM sys.server_principals WHERE name = 'dba_proyecto')
    DROP LOGIN dba_proyecto;
CREATE LOGIN dba_proyecto WITH PASSWORD = '$SQL_NEW_PASS', CHECK_POLICY = OFF;
ALTER SERVER ROLE sysadmin ADD MEMBER dba_proyecto;
"

# 3. Verificación final de acceso
echo "[3/3] Verificando acceso con el nuevo usuario..."
if $SQL_CMD -S localhost,5000 -U dba_proyecto -P "$SQL_NEW_PASS" -Q "SELECT '✔ ACCESO CONCEDIDO' AS Status" | grep -q 'ACCESO CONCEDIDO'; then
    echo "--- PROCESO COMPLETADO CON ÉXITO ---"
else
    echo "✘ ERROR: El login falló incluso después de la reparación."
    exit 1
fi
