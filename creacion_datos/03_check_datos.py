import mysql.connector
import pymssql
import oracledb
from tabulate import tabulate

# CREDENCIALES (Extraídas de tu configuración)
USER_DB = "dba_proyecto"
PASS_DB = "password_proyecto"
PASS_SQL = "Password_proyecto123"

def get_connections():
    """Establece y retorna las conexiones a los tres motores."""
    return {
        'MariaDB': mysql.connector.connect(
            host="127.0.0.1", port=4000, user=USER_DB, 
            password=PASS_DB, database="gestion_administrativa"
        ),
        'SQLServer': pymssql.connect(
            server="127.0.0.1", port=5000, user=USER_DB, 
            password=PASS_SQL, database="gestion_citas"
        ),
        'Oracle': oracledb.connect(
            user=USER_DB, password=PASS_DB, 
            dsn="127.0.0.1:3000/XEPDB1"
        )
    }

def run_full_audit():
    conns = {}
    try:
        conns = get_connections()
        print("\n" + "="*70)
        print("AUDITORÍA DE SISTEMAS DISTRIBUIDOS - REPORTE FINAL")
        print("="*70)

        # --- [1] REPORTE DE VOLUMETRÍA ---
        # (Motor, Tabla, Esperado)
        targets = [
            ('MariaDB', 'pacientes', 10000),
            ('MariaDB', 'profesionales', 200),
            ('SQLServer', 'dbo.citas', 80000),
            ('Oracle', 'historial_atenciones', 120000)
        ]
        
        volumetry_results = []
        for engine_name, table, expected in targets:
            cur = conns[engine_name].cursor()
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            actual = cur.fetchone()[0]
            status = "✅ OK" if actual == expected else f"❌ ERROR ({actual - expected})"
            volumetry_results.append([engine_name, table, expected, actual, status])
            cur.close()
        
        print("\n[PASO 1] ESTADO DE LA CARGA:")
        print(tabulate(volumetry_results, headers=["Motor", "Tabla", "Esperado", "Actual", "Status"], tablefmt="fancy_grid"))

        # --- [2] MUESTRAS ALEATORIAS POR MOTOR ---
        print("\n[PASO 2] VALIDACIÓN VISUAL DE REGISTROS (MUESTRA):")
        # Aquí es donde corregimos el desempaquetado de las 5 columnas
        for engine_name, table, expected, actual, status in volumetry_results:
            cur = conns[engine_name].cursor()
            
            # Sintaxis específica por motor
            if engine_name == 'MariaDB':
                query = f"SELECT * FROM {table} LIMIT 3"
            elif engine_name == 'SQLServer':
                query = f"SELECT TOP 3 * FROM {table}"
            else: # Oracle
                query = f"SELECT * FROM {table} FETCH FIRST 3 ROWS ONLY"
            
            try:
                cur.execute(query)
                rows = cur.fetchall()
                cols = [desc[0] for desc in cur.description]
                print(f"\n--- Muestra de: {engine_name} | Tabla: {table} ---")
                print(tabulate(rows, headers=cols, tablefmt="simple"))
            except Exception as e:
                print(f"⚠️ Error al obtener muestra de {table}: {e}")
            finally:
                cur.close()

        # --- [3] AUDITORÍA DE INTEGRIDAD REFERENCIAL (CROSS-DB) ---
        print("\n[PASO 3] VERIFICACIÓN DE CONSISTENCIA ENTRE MOTORES:")
        
        # Prueba: ¿Existen los pacientes citados en SQL Server dentro de MariaDB?
        s_cur = conns['SQLServer'].cursor()
        s_cur.execute("SELECT TOP 500 paciente_id FROM dbo.citas")
        sample_ids = [row[0] for row in s_cur.fetchall()]
        s_cur.close()
        
        if sample_ids:
            m_cur = conns['MariaDB'].cursor()
            # Creamos el string de placeholders (%s, %s...)
            placeholders = ', '.join(['%s'] * len(sample_ids))
            m_cur.execute(f"SELECT paciente_id FROM pacientes WHERE paciente_id IN ({placeholders})", tuple(sample_ids))
            found_ids = [row[0] for row in m_cur.fetchall()]
            m_cur.close()
            
            orphans = set(sample_ids) - set(found_ids)
            if not orphans:
                print("✅ INTEGRIDAD SQL Server -> MariaDB: Consistente (Sin huérfanos).")
            else:
                print(f"⚠️ CRÍTICO: Se detectaron {len(orphans)} citas en SQL Server apuntando a pacientes inexistentes.")

        # Prueba: ¿Existen los pacientes del historial en Oracle dentro de MariaDB?
        o_cur = conns['Oracle'].cursor()
        o_cur.execute("SELECT paciente_id FROM historial_atenciones WHERE ROWNUM <= 500")
        o_sample_ids = [row[0] for row in o_cur.fetchall()]
        o_cur.close()
        
        if o_sample_ids:
            m_cur = conns['MariaDB'].cursor()
            placeholders = ', '.join(['%s'] * len(o_sample_ids))
            m_cur.execute(f"SELECT paciente_id FROM pacientes WHERE paciente_id IN ({placeholders})", tuple(o_sample_ids))
            o_found_ids = [row[0] for row in m_cur.fetchall()]
            m_cur.close()
            
            o_orphans = set(o_sample_ids) - set(o_found_ids)
            if not o_orphans:
                print("✅ INTEGRIDAD Oracle -> MariaDB: Consistente (Historial clínico válido).")
            else:
                print(f"⚠️ CRÍTICO: Oracle tiene {len(o_orphans)} registros de atención sin paciente maestro.")

    except Exception as e:
        print(f"\n✘ FALLO CRÍTICO EN LA AUDITORÍA: {e}")
    finally:
        for name, conn in conns.items():
            conn.close()
        print("\n" + "="*70)
        print("CONEXIONES CERRADAS. PROCESO FINALIZADO.")
        print("="*70)

if __name__ == "__main__":
    run_full_audit()
