echo 'puerto de escucha'
sudo ss -tulpn | grep 5000
echo 'Usuario dba'
sqlcmd -S localhost,5000 -U dba_proyecto -P 'Password_proyecto123' -Q "SELECT @@VERSION; SELECT name FROM sys.databases;"
