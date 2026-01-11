cat <<EOF >> ~/.bash_profile

# --- CONFIGURACION AUTOMATICA ORACLE ---
export ORACLE_SID=XE
export ORAENV_ASK=NO
. /usr/local/bin/oraenv
export PATH=\$PATH:\$ORACLE_HOME/bin
# ---------------------------------------
EOF

# Aplicar los cambios ahora mismo
source ~/.bash_profile
