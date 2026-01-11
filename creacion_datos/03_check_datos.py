import mysql.connector
import pymssql
import oracledb
from tabulate import tabulate # Opcional: pip install tabulate para ver tablas lindas

# CREDENCIALES (Extraídas de tu script de carga)
USER_DB = "dba_proyecto"
PASS_DB = "password_proyecto"
PASS_SQL = "Password_proyecto123"

def verify_deployment():
    conns = {}
    try:
        print("--- INICIANDO AUDITORÍA TÉCNICA DE REGISTROS ---")
        
        # 1. Conexiones
        conns['MariaDB'] = mysql.connector.connect(host="127.0.0.1", port=4000, user=USER_DB, password=PASS_DB, database="gestion_administrativa")
        conns['SQLServer'] = pymssql.connect(server="127.0.0.1", port=5000, user=USER_DB, password=PASS_SQL, database="gestion_citas")
        conns['Oracle'] = oracledb.connect(user=USER_DB, password=PASS_DB, dsn="127.0.0.1:3000/XEPDB1")

        # 2. Mapa de verificación: (DB_Key, Tabla, Conteo_Esperado, Query_Muestra)
        checks = [
            ('MariaDB', 'profesionales', 200, "SELECT * FROM profesionales LIMIT 5"),
            ('MariaDB', 'pacientes', 10000, "SELECT * FROM pacientes LIMIT 5"),
            ('SQLServer', 'dbo.citas', 80000, "SELECT TOP 5 * FROM dbo.citas"),
            ('Oracle', 'historial_atenciones', 120000, "SELECT * FROM historial_atenciones FETCH FIRST 5 ROWS ONLY")
        ]

        summary = []
        for db_key, table, expected, sample_query in checks:
            cursor = conns[db_key].cursor()
            
            # Conteo
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            actual = cursor.fetchone()[0]
            status = "✅ OK" if actual == expected else "❌ DIFERENCIA"
            
            summary.append([db_key, table, expected, actual, status])
            
            # Muestra de datos
            print(f"\n>>> MUESTRA DE DATOS: {db_key} - TABLA: {table}")
            cursor.execute(sample_query)
            rows = cursor.fetchall()
            
            # Obtener nombres de columnas
            cols = [desc[0] for desc in cursor.description]
            print(tabulate(rows, headers=cols, tablefmt="grid"))
            cursor.close()

        # 3. Reporte Final
        print("\n" + "="*60)
        print("RESUMEN DE INTEGRIDAD DE CARGA")
        print("="*60)
        print(tabulate(summary, headers=["Motor", "Tabla", "Esperado", "Actual", "Estado"], tablefmt="fancy_grid"))

    except Exception as e:
        print(f"\n✘ ERROR DURANTE LA VERIFICACIÓN: {e}")
    finally:
        for c in conns.values(): c.close()
        print("\nAuditoría finalizada. Conexiones cerradas.")

if __name__ == "__main__":
    verify_deployment()
