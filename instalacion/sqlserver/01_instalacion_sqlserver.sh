#!/bin/bash
echo "--- INSTALANDO SQL SERVER 2022: PUERTO 5000 ---"

# 1. Configurar el repositorio de Microsoft
sudo curl -o /etc/yum.repos.d/mssql-server.repo https://packages.microsoft.com/config/rhel/8/mssql-server-2022.repo

# 2. Instalar el motor
sudo dnf install -y sqlcmd mssql-server

# 3. EL TRUCO DE LA MEMORIA: Engañar al instalador
# SQL Server fallará si ve menos de 2GB. Forzamos la configuración.
sudo /opt/mssql/bin/mssql-conf set control.multicatanywhere false
sudo /opt/mssql/bin/mssql-conf set network.tcpport 5000

# 4. Configuración inicial (Aceptación de licencia y Password)
# Nota: La contraseña DEBE ser compleja (Mayúscula, minúscula, número y símbolo)
# Usaremos: Password_proyecto123
echo "Ejecutando configuración inicial..."
sudo MSSQL_SA_PASSWORD='Password_proyecto123' \
     MSSQL_PID='Developer' \
     /opt/mssql/bin/mssql-conf -n setup accept-eula

# 5. Reiniciar para aplicar el puerto 5000
sudo systemctl restart mssql-server
