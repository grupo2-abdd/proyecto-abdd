import mysql.connector
import pymssql
import oracledb
from faker import Faker
import random

fake = Faker()
BATCH_SIZE = 1000  # Insertamos de 1000 en 1000 para no ahogar la RAM

# Credenciales
PASS_DB = "password_proyecto"
PASS_SQL = "Password_proyecto123"

def populate():
    try:
        # 1. CONEXIONES
        m_conn = mysql.connector.connect(host="127.0.0.1", port=4000, user="dba_proyecto", password=PASS_DB, database="gestion_administrativa")
        s_conn = pymssql.connect(server="localhost", port=5000, user="dba_proyecto", password=PASS_SQL, database="gestion_citas", autocommit=True)
        o_conn = oracledb.connect(user="dba_proyecto", password=PASS_DB, dsn="localhost:3000/XEPDB1")

        m_cur = m_conn.cursor()
        s_cur = s_conn.cursor()
        o_cur = o_conn.cursor()

        print("--- Fase 1: MariaDB (10,000 Pacientes y 200 Médicos) ---")
        # Médicos
        medicos_ids = list(range(1, 201))
        medicos_data = [(i, fake.name(), fake.job()[:50], f"LIC-{i:05d}") for i in medicos_ids]
        m_cur.executemany("INSERT INTO profesionales VALUES (%s, %s, %s, %s)", medicos_data)
        
        # Pacientes (en lotes para ahorrar RAM)
        pacientes_ids = list(range(1, 10001))
        for i in range(0, 10000, BATCH_SIZE):
            lote = [(j, fake.name(), fake.date_of_birth(minimum_age=0, maximum_age=90), random.choice(['M', 'F']), fake.phone_number()[:20]) 
                    for j in range(i+1, i+BATCH_SIZE+1)]
            m_cur.executemany("INSERT INTO pacientes VALUES (%s, %s, %s, %s, %s)", lote)
        m_conn.commit()
        print("✔ MariaDB poblada.")

        print("--- Fase 2: SQL Server (80,000 Citas) ---")
        # Generamos citas usando los IDs que ya existen en MariaDB
        for i in range(0, 80000, BATCH_SIZE):
            lote_citas = [(j, random.choice(pacientes_ids), random.choice(medicos_ids), fake.date_time_this_year(), random.choice(['Programada', 'Completada', 'Cancelada'])) 
                          for j in range(i+1, i+BATCH_SIZE+1)]
            s_cur.executemany("INSERT INTO citas (cita_id, paciente_id, medico_id, fecha_cita, estado) VALUES (%d, %d, %d, %s, %s)", lote_citas)
        print("✔ SQL Server poblado.")

        print("--- Fase 3: Oracle (120,000 Atenciones) ---")
        # Solo generamos atenciones para citas que están 'Completada' o al azar
        for i in range(0, 120000, BATCH_SIZE):
            lote_atenciones = [(j, random.randint(1, 80000), random.choice(pacientes_ids), fake.date_time_this_year(), fake.sentence(nb_words=6), fake.sentence(nb_words=10)) 
                               for j in range(i+1, i+BATCH_SIZE+1)]
            o_cur.executemany("INSERT INTO historial_atenciones VALUES (:1, :2, :3, :4, :5, :6)", lote_atenciones)
        o_conn.commit()
        print("✔ Oracle poblado.")

    except Exception as e:
        print(f"✘ ERROR CRÍTICO: {e}")
    finally:
        for c in [m_conn, s_conn, o_conn]: c.close()

if __name__ == "__main__":
    populate()
