#!/bin/bash
echo "--- CONFIGURANDO MARIADB: PUERTO 4000 ---"

# 1. Instalación
sudo dnf install -y mariadb-server

# 2. Cambio de Puerto (De 3306 a 4000)
# Usamos sed para insertar la directiva 'port=4000' bajo la sección [mysqld]
sudo sed -i '/\[mysqld\]/a port=4000' /etc/my.cnf.d/mariadb-server.cnf

# 3. Arrancar y habilitar el servicio
sudo systemctl enable --now mariadb

# 4. Creación del Usuario 'dba_proyecto'
# MySQL/MariaDB diferencia entre 'localhost' y '%' (remoto). Creamos '%' para tu PC Host.
sudo mysql -e "CREATE USER 'dba_proyecto'@'%' IDENTIFIED BY 'password_proyecto';"
sudo mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'dba_proyecto'@'%' WITH GRANT OPTION;"
sudo mysql -e "FLUSH PRIVILEGES;"

echo "--- MARIADB CONFIGURADO EN PUERTO 4000 ---"
