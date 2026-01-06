#!/bin/bash
echo "--- INICIANDO PASO 01: DESCARGA E INSTALACIÓN BLINDADA ---"

# 1. Validación de SWAP (Seguro de vida para 1.5GB RAM)
SWAP_TOTAL=$(free -m | grep Swap | awk '{print $2}')
if [ "$SWAP_TOTAL" -lt 3500 ]; then
    echo "ERROR: El Swap es insuficiente ($SWAP_TOTAL MB). Ejecuta el Paso 00 (preconfigs) primero."
    exit 1
fi

# 2. Instalación de dependencias y Preinstalador
echo "Instalando pre-requisitos y wget..."
sudo dnf install -y oracle-database-preinstall-21c wget

# 3. Descarga Directa del Motor (2.1 GB)
URL="https://download.oracle.com/otn-pub/otn_software/db-express/oracle-database-xe-21c-1.0-1.ol8.x86_64.rpm"
ARCHIVO="oracle-database-xe-21c-1.0-1.ol8.x86_64.rpm"

if [ ! -f "$ARCHIVO" ]; then
    echo "Descargando Oracle Database 21c XE directamente... (Paciencia)"
    wget "$URL" -O "$ARCHIVO"
else
    echo "El instalador ya existe. Saltando descarga."
fi

# 4. Instalación de los Binarios
echo "Instalando binarios de Oracle (RPM)..."
sudo dnf localinstall -y "$ARCHIVO"

# 5. CONFIGURACIÓN DE FIREWALL (Vital para conexión desde Host)
echo "Abriendo puertos 3000 (Oracle), 4000 (MariaDB) y 5000 (PostgreSQL)..."
if systemctl is-active --quiet firewalld; then
    sudo firewall-cmd --permanent --add-port=3000/tcp
    sudo firewall-cmd --permanent --add-port=4000/tcp
    sudo firewall-cmd --permanent --add-port=5000/tcp
    sudo firewall-cmd --reload
    echo "Reglas de firewall aplicadas exitosamente."
else
    echo "FirewallD no está corriendo, no se requieren ajustes de red internos."
fi

# 6. INYECCIÓN AGRESIVA DEL PUERTO 3000
CONF_FILE="/etc/sysconfig/oracle-xe-21c.conf"
echo "Configurando puerto 3000 en $CONF_FILE..."
sudo sed -i '/LISTENER_PORT/d' "$CONF_FILE"
echo "LISTENER_PORT=3000" | sudo tee -a "$CONF_FILE"

# 7. VERIFICACIÓN CRÍTICA
RESULTADO=$(grep "LISTENER_PORT=3000" "$CONF_FILE")
if [ -z "$RESULTADO" ]; then
    echo "ERROR CRÍTICO: No se pudo establecer el puerto 3000 en el archivo de configuración."
    exit 1
else
    echo "VERIFICACIÓN EXITOSA: $RESULTADO"
fi

echo "------------------------------------------------------------"
echo "PASO 01 FINALIZADO CORRECTAMENTE"
echo "------------------------------------------------------------"
echo "SIGUIENTE PASO (EJECUCIÓN MANUAL):"
echo "sudo /etc/init.d/oracle-xe-21c configure"
echo "------------------------------------------------------------"
