#!/bin/bash

echo "--- INICIANDO MODERNIZACIÓN DE ENTORNO PYTHON ---"

# 1. Instalación de Python 3.9 y herramientas de desarrollo
echo "[1/4] Instalando Python 3.9 y dependencias de sistema..."
sudo dnf install -y python39 python39-devel gcc

# 2. Actualización de PIP para la versión 3.9
echo "[2/4] Preparando gestor de paquetes (pip)..."
python3.9 -m pip install --user --upgrade pip

# 3. Instalación de dependencias del proyecto
echo "[3/4] Instalando librerías (Faker, Oracle, SQL Server, MariaDB, Pandas)..."
python3.9 -m pip install --user Faker oracledb mysql-connector-python pymssql pandas sqlalchemy pyodbc tabulate

# 4. Configuración del ALIAS
# Usaremos .bashrc para que el alias persista tras reiniciar la sesión
echo "[4/4] Configurando alias 'python' para apuntar a 3.9..."
if ! grep -q "alias python='python3.9'" ~/.bashrc; then
    echo "alias python='python3.9'" >> ~/.bashrc
    echo "✔ Alias creado con éxito."
else
    echo "⚠ El alias ya existía."
fi

echo "--- PROCESO COMPLETADO ---"
echo "IMPORTANTE: Ejecuta 'source ~/.bashrc' para activar el alias ahora mismo."
