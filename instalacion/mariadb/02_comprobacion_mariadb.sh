#!/bin/bash
echo "PUERTO"
sudo ss -tulpn | grep 4000
echo "USUARIO ADB"
mysql -u dba_proyecto -p'password_proyecto' -P 4000 -h 127.0.0.1 -e "SELECT user, host FROM mysql.user WHERE user='dba_proyecto'; SHOW GRANTS FOR 'dba_proyecto'@'%';"O

