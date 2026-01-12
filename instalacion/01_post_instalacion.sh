#!/bin/bash
echo "--- ABRIENDO PUERTOS PARA EL TRIDENTE DE BASES DE DATOS ---"

# Abrir puertos de forma permanente
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-port=4000/tcp
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --permanent --add-port=8501/tcp

# Recargar para aplicar cambios
sudo firewall-cmd --reload

# Verificación inmediata
echo "Puertos abiertos actualmente:"
sudo firewall-cmd --list-ports
