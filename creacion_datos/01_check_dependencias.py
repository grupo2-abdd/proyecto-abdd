import importlib

libs = [
    "faker",           # Generador de datos
    "oracledb",        # Driver Oracle
    "mysql.connector", # Driver MariaDB
    "pymssql",         # Driver SQL Server
    "pandas"           # Para el futuro ETL
]

print("--- VERIFICACIÓN DE LIBRERÍAS ---")
for lib in libs:
    try:
        importlib.import_module(lib)
        print(f"✔ {lib}: INSTALADA")
    except ImportError:
        print(f"✘ {lib}: NO ENCONTRADA")
