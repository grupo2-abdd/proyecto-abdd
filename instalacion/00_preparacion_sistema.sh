#!/bin/bash
echo "--- INICIANDO PRE-CONFIGURACIÓN ESTRATÉGICA ---"

# 1. SWAP de 4GB: Tu seguro de vida para la RAM
# Sin esto, el instalador de Oracle fallará por "Out of Memory"
echo "[1/4] Creando archivo Swap de 4GB..."
sudo dd if=/dev/zero of=/swapfile bs=1024 count=4194304
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile swap swap defaults 0 0' | sudo tee -a /etc/fstab

# 2. Expansión de Disco
# Aseguramos que el sistema vea los 70GB físicos
echo "[2/4] Expandiendo almacenamiento..."
sudo lvextend -l +100%FREE /dev/mapper/ol-root
sudo xfs_growfs /

# 3. Preinstalador Oficial de Oracle 21c
# Este comando es MAGIA: configura límites del kernel, crea grupos y usuarios
echo "[3/4] Instalando el preinstalador de Oracle 21c..."
sudo dnf install -y oracle-database-preinstall-21c

# 4. Utilidades Extra y SELinux
# Desactivamos SELinux para evitar bloqueos en los puertos 3000, 4000 y 5000
echo "[4/4] Ajustando seguridad y utilidades..."
sudo dnf install -y wget
sudo setenforce 0
sudo sed -i 's/^SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config

echo "--------------------------------------------------"
echo "SISTEMA PREPARADO PARA RECIBIR LOS MOTORES"
echo "RAM + Swap: $(free -h | grep -E 'Mem|Swap' | awk '{print $2}' | xargs echo 'Total')"
echo "Espacio en /: $(df -h / | awk 'NR==2 {print $4}') libres"
echo "--------------------------------------------------"
