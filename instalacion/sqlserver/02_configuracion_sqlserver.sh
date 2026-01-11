# Instalar herramientas de línea de comandos
sudo curl -o /etc/yum.repos.d/msprod.repo https://packages.microsoft.com/config/rhel/8/prod.repo
sudo dnf install -y mssql-tools unixODBC-devel
echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile
source ~/.bash_profile

# Crear el login y el usuario
sqlcmd -S localhost,5000 -U sa -P 'Password_proyecto123' -Q "CREATE LOGIN dba_proyecto WITH PASSWORD = 'Password_proyecto123'; ALTER SERVER ROLE sysadmin ADD MEMBER dba_proyecto;"
