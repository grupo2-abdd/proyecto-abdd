import streamlit as st
import mysql.connector
import pymssql
import oracledb
import pandas as pd
import time
from logging import getLogger, INFO, FileHandler, Formatter

# --- CONFIGURACIÓN DE LOGGER ---
def setup_logger(name, log_file, level=INFO):
    handler = FileHandler(log_file)
    handler.setFormatter(Formatter('%(asctime)s - %(message)s'))
    
    logger = getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger

sql_logger = setup_logger('sql_logger', 'sql_queries.log')

class VerboseLogger:
    def log_sql(self, engine, query, params=None):
        # Log to file (full detail for debugging history)
        log_entry_file = f"MOTOR={engine} | QUERY={query}"
        if params:
            log_entry_file += f" | PARAMS={params}"
        sql_logger.info(log_entry_file)
        
        # Display in sidebar (new format based on user's clarification)
        st.sidebar.text(f"Motor: {engine}") # Engine as a text label
        st.sidebar.code(query, language='sql') # Pure SQL query in a code box
        # --- CAMBIO SOLICITADO: Se elimina la visualización de parámetros en el sidebar ---
        st.sidebar.markdown("---") # Separator for better legibility

log = VerboseLogger()

# --- CONFIGURACIÓN DE ENTORNO Y CONEXIONES ---
st.set_page_config(page_title="Hospital Core - Middleware", layout="wide")

USER_DB, PASS_DB, PASS_SQL = "dba_proyecto", "password_proyecto", "Password_proyecto123"
DB_CONFIG = {
    "mariadb": {"host": "127.0.0.1", "port": 4000, "user": USER_DB, "password": PASS_DB},
    "sqlserver": {"server": "127.0.0.1", "port": 5000, "user": USER_DB, "password": PASS_SQL},
    "oracle": {"user": USER_DB, "password": PASS_DB, "dsn": "127.0.0.1:3000/XEPDB1"}
}

# --- SIDEBAR ---
with st.sidebar:
    st.title("🚥 Estatus de Motores")

    def check_status(name, config):
        try:
            if name == "MariaDB":
                c = mysql.connector.connect(**config, connect_timeout=2)
            elif name == "SQL Server":
                c = pymssql.connect(**config, timeout=2)
            else:
                c = oracledb.connect(**config)
            c.close()
            return "ONLINE ✅"
        except Exception:
            return "OFFLINE ❌"

    st.write(f"**MariaDB:** {check_status('MariaDB', DB_CONFIG['mariadb'])}")
    st.write(f"**SQL Server:** {check_status('SQL Server', DB_CONFIG['sqlserver'])}")
    st.write(f"**Oracle:** {check_status('Oracle', DB_CONFIG['oracle'])}")
    st.markdown("---")

    st.subheader("📊 Volumetría de Datos")

    def get_table_counts():
        counts = {"Pacientes": "N/A", "Médicos": "N/A", "Citas": "N/A", "Atenciones": "N/A"}
        try:
            conn = mysql.connector.connect(**DB_CONFIG['mariadb'], database="gestion_administrativa", connect_timeout=2)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM pacientes"); counts["Pacientes"] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM profesionales"); counts["Médicos"] = cursor.fetchone()[0]
            conn.close()
        except Exception: pass
        try:
            conn = pymssql.connect(**DB_CONFIG['sqlserver'], database="gestion_citas", timeout=2)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM dbo.citas"); counts["Citas"] = cursor.fetchone()[0]
            conn.close()
        except Exception: pass
        try:
            conn = oracledb.connect(**DB_CONFIG['oracle'])
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM historial_atenciones"); counts["Atenciones"] = cursor.fetchone()[0]
            conn.close()
        except Exception: pass
        return counts

    if st.button("Actualizar Conteos"):
        st.session_state.table_counts = get_table_counts()
    
    if 'table_counts' not in st.session_state:
        st.session_state.table_counts = get_table_counts()

    for table, count in st.session_state.table_counts.items():
        st.write(f"**{table}:** {count}")
    
    st.markdown("---")
    st.info("Logs Verbose activos en el panel inferior.")

# --- TÍTULO PRINCIPAL ---
st.title("🏥 Capa de Interconexión: Middleware Python")

# --- SECCIÓN 1: BÚSQUEDA GLOBAL (VIRTUAL JOIN) ---
st.header("🔎 1. Consulta Unificada de Paciente")
search_id = st.number_input("Ingrese ID del Paciente para búsqueda multi-motor", min_value=1, step=1)

if st.button("Buscar en toda la Red"):
    with st.status("Realizando Join Virtual entre motores...", expanded=True) as status:
        try:
            status.update(label="Buscando identidad en MariaDB...")
            conn = mysql.connector.connect(**DB_CONFIG['mariadb'], database="gestion_administrativa")
            query = "SELECT nombre, fecha_nacimiento, genero, telefono FROM pacientes WHERE paciente_id = %s"
            log.log_sql("MariaDB", query, (search_id,))
            df_paciente = pd.read_sql(query, conn, params=[search_id])
            conn.close()
            st.subheader("👤 Datos del Paciente (MariaDB)")
            if not df_paciente.empty:
                st.dataframe(df_paciente, use_container_width=True)
            else:
                st.warning("Paciente no encontrado en la base de datos principal (MariaDB).")
        except Exception as e:
            st.error(f"Error en MariaDB: {e}")
        try:
            status.update(label="Consultando citas en SQL Server...")
            conn = pymssql.connect(**DB_CONFIG['sqlserver'], database="gestion_citas")
            query = "SELECT cita_id, medico_id, fecha_cita, estado FROM dbo.citas WHERE paciente_id = %s ORDER BY fecha_cita DESC"
            log.log_sql("SQL Server", query, (search_id,))
            citas_df = pd.read_sql(query, conn, params=(search_id,))
            conn.close()
            st.subheader("🗓️ Historial de Citas (SQL Server)")
            if not citas_df.empty:
                st.dataframe(citas_df, use_container_width=True)
            else:
                st.info("El paciente no tiene citas registradas en SQL Server.")
        except Exception as e:
            st.error(f"Error en SQL Server: {e}")
        try:
            status.update(label="Recuperando historial de Oracle...")
            conn = oracledb.connect(**DB_CONFIG['oracle'])
            query = "SELECT atencion_id, cita_id, fecha_atencion, diagnostico, tratamiento FROM historial_atenciones WHERE paciente_id = :1 ORDER BY fecha_atencion DESC"
            log.log_sql("Oracle", query, (search_id,))
            historial_df = pd.read_sql(query, conn, params=[search_id])
            conn.close()
            st.subheader("🩺 Historial de Atenciones Clínicas (Oracle)")
            if not historial_df.empty:
                st.dataframe(historial_df, use_container_width=True)
            else:
                st.info("El paciente no tiene atenciones clínicas registradas en Oracle.")
        except Exception as e:
            st.error(f"Error en Oracle: {e}")
        status.update(label="Búsqueda completada", state="complete")

st.markdown("---")

# --- SECCIÓN 2: GESTIÓN DE REGISTROS CON VALIDACIÓN ---
st.header("➕ 2. Gestión de Registros (con Lógica Transaccional Mejorada)")

def id_exists(engine, db_name, table, id_column, id_value):
    conn, cursor = None, None
    try:
        if engine == "MariaDB":
            conn = mysql.connector.connect(**DB_CONFIG['mariadb'], database=db_name)
            query = f"SELECT COUNT(*) FROM {table} WHERE {id_column} = %s"
            params = (id_value,)
        elif engine == "SQL Server":
            conn = pymssql.connect(**DB_CONFIG['sqlserver'], database=db_name)
            query = f"SELECT COUNT(*) FROM {table} WHERE {id_column} = %s"
            params = (id_value,)
        else: return True
        cursor = conn.cursor()
        log.log_sql(engine, query, params)
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        st.error(f"Error de validación en {engine}: {e}")
        return True
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_next_id(engine, db_name, table, id_column):
    conn, cursor = None, None
    try:
        if engine == "MariaDB":
            conn = mysql.connector.connect(**DB_CONFIG['mariadb'], database=db_name)
            query = f"SELECT MAX({id_column}) FROM {table}"
        elif engine == "SQL Server":
            conn = pymssql.connect(**DB_CONFIG['sqlserver'], database=db_name)
            query = f"SELECT MAX({id_column}) FROM {table}"
        elif engine == "Oracle":
            conn = oracledb.connect(**DB_CONFIG['oracle'])
            query = f"SELECT MAX({id_column}) FROM {table}"
        cursor = conn.cursor()
        log.log_sql(engine, query)
        cursor.execute(query)
        max_id = cursor.fetchone()[0]
        return (max_id or 0) + 1
    except Exception as e:
        st.error(f"Error obteniendo next_id de {engine}: {e}")
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

tab_pac, tab_med, tab_ate = st.tabs(["👤 Registrar Paciente", "👨‍⚕️ Registrar Médico", "🩺 Registrar Nueva Atención"])

with tab_pac:
    with st.form("nuevo_paciente_form", clear_on_submit=True):
        st.subheader("Formulario de Nuevo Paciente")
        pac_nombre = st.text_input("Nombre Completo")
        pac_fnac = st.date_input("Fecha de Nacimiento")
        pac_gen = st.selectbox("Género", ["M", "F", "O"])
        pac_tel = st.text_input("Teléfono")
        submitted = st.form_submit_button("Registrar Paciente")
        if submitted:
            conn = None
            try:
                if not all([pac_nombre, pac_fnac, pac_gen, pac_tel]):
                    raise ValueError("Todos los campos son obligatorios.")
                next_id = get_next_id("MariaDB", "gestion_administrativa", "pacientes", "paciente_id")
                if not next_id: raise Exception("No se pudo generar un nuevo ID de paciente.")
                conn = mysql.connector.connect(**DB_CONFIG['mariadb'], database="gestion_administrativa")
                cursor = conn.cursor()
                query = "INSERT INTO pacientes (paciente_id, nombre, fecha_nacimiento, genero, telefono) VALUES (%s, %s, %s, %s, %s)"
                params = (next_id, pac_nombre, pac_fnac, pac_gen, pac_tel)
                cursor.execute(query, params)
                if cursor.rowcount == 1:
                    conn.commit()
                    log.log_sql("MariaDB", "COMMIT")
                    st.success(f"¡Paciente '{pac_nombre}' (ID: {next_id}) registrado con éxito! Filas afectadas: {cursor.rowcount}")
                else:
                    conn.rollback()
                    log.log_sql("MariaDB", "ROLLBACK")
                    raise Exception("La inserción no afectó ninguna fila.")
            except Exception as e:
                if conn: conn.rollback(); log.log_sql("MariaDB", "ROLLBACK")
                st.error(f"Error al registrar paciente: {e}")
            finally:
                if conn: conn.close()

with tab_med:
    with st.form("nuevo_medico_form", clear_on_submit=True):
        st.subheader("Formulario de Nuevo Médico")
        med_nombre = st.text_input("Nombre Completo")
        med_spec = st.text_input("Especialidad")
        med_lic = st.text_input("Licencia")
        submitted = st.form_submit_button("Registrar Médico")
        if submitted:
            conn = None
            try:
                if not all([med_nombre, med_spec, med_lic]):
                    raise ValueError("Todos los campos son obligatorios.")
                next_id = get_next_id("MariaDB", "gestion_administrativa", "profesionales", "medico_id")
                if not next_id: raise Exception("No se pudo generar un nuevo ID de médico.")
                conn = mysql.connector.connect(**DB_CONFIG['mariadb'], database="gestion_administrativa")
                cursor = conn.cursor()
                query = "INSERT INTO profesionales (medico_id, nombre, especialidad, licencia) VALUES (%s, %s, %s, %s)"
                params = (next_id, med_nombre, med_spec, med_lic)
                cursor.execute(query, params)
                if cursor.rowcount == 1:
                    conn.commit()
                    log.log_sql("MariaDB", "COMMIT")
                    st.success(f"¡Médico '{med_nombre}' (ID: {next_id}) registrado! Filas afectadas: {cursor.rowcount}")
                else:
                    conn.rollback()
                    log.log_sql("MariaDB", "ROLLBACK")
                    raise Exception("La inserción no afectó ninguna fila.")
            except Exception as e:
                if conn: conn.rollback(); log.log_sql("MariaDB", "ROLLBACK")
                st.error(f"Error al registrar médico: {e}")
            finally:
                if conn: conn.close()

with tab_ate:
    st.subheader("Formulario de Nueva Atención")
    st.info("Esto crea una cita en SQL Server y un registro clínico en Oracle de forma transaccional.")
    with st.form("nueva_atencion_form", clear_on_submit=True):
        pac_id = st.number_input("ID del Paciente", min_value=1, step=1)
        med_id = st.number_input("ID del Médico", min_value=1, step=1)
        diagnostico = st.text_area("Diagnóstico de la Atención")
        tratamiento = st.text_area("Tratamiento Prescrito")
        submitted = st.form_submit_button("Registrar Atención Transaccional")
        if submitted:
            pac_ok = id_exists("MariaDB", "gestion_administrativa", "pacientes", "paciente_id", pac_id)
            med_ok = id_exists("MariaDB", "gestion_administrativa", "profesionales", "medico_id", med_id)
            if not pac_ok: st.error(f"ID de Paciente '{pac_id}' NO existe.")
            if not med_ok: st.error(f"ID de Médico '{med_id}' NO existe.")
            if pac_ok and med_ok:
                s_conn, o_conn = None, None
                try:
                    s_conn = pymssql.connect(**DB_CONFIG['sqlserver'], database="gestion_citas")
                    o_conn = oracledb.connect(**DB_CONFIG['oracle'])
                    s_cursor, o_cursor = s_conn.cursor(), o_conn.cursor()
                    with st.spinner("Paso 1/2: Ejecutando inserciones..."):
                        new_cita_id = get_next_id("SQL Server", "gestion_citas", "dbo.citas", "cita_id")
                        new_atencion_id = get_next_id("Oracle", None, "historial_atenciones", "atencion_id")
                        if not all([new_cita_id, new_atencion_id]):
                            raise Exception("No se pudieron generar los IDs necesarios.")
                        q_sql = "INSERT INTO dbo.citas (cita_id, paciente_id, medico_id, fecha_cita, estado) VALUES (%s, %s, %s, GETDATE(), 'Realizada')"
                        params_sql = (new_cita_id, pac_id, med_id)
                        log.log_sql("SQL Server", q_sql, params_sql)
                        s_cursor.execute(q_sql, params_sql)
                        if s_cursor.rowcount != 1:
                            raise Exception("Fallo la inserción en SQL Server (citas).")
                        st.info("✅ Inserción en SQL Server preparada.")
                        q_ora = "INSERT INTO historial_atenciones (atencion_id, cita_id, paciente_id, fecha_atencion, diagnostico, tratamiento) VALUES (:1, :2, :3, SYSDATE, :4, :5)"
                        params_ora = (new_atencion_id, new_cita_id, pac_id, diagnostico, tratamiento)
                        log.log_sql("Oracle", q_ora, params_ora)
                        o_cursor.execute(q_ora, params_ora)
                        if o_cursor.rowcount != 1:
                            raise Exception("Fallo la inserción en Oracle (historial_atenciones).")
                        st.info("✅ Inserción en Oracle preparada.")
                    with st.spinner("Paso 2/2: Confirmando commits..."):
                        s_conn.commit()
                        log.log_sql("SQL Server", "COMMIT")
                        st.info("✅ Commit en SQL Server confirmado.")
                        o_conn.commit()
                        log.log_sql("Oracle", "COMMIT")
                        st.info("✅ Commit en Oracle confirmado.")
                    st.balloons()
                    st.success(f"¡Transacción completada! Cita ID: {new_cita_id}, Atención ID: {new_atencion_id}")
                except Exception as e:
                    st.error(f"❌ Error en la transacción: {e}")
                    st.warning("Iniciando rollback para deshacer cambios...")
                    if s_conn:
                        try: s_conn.rollback(); log.log_sql("SQL Server", "ROLLBACK"); st.info("Rollback en SQL Server completado.")
                        except Exception as rb_e: st.error(f"Error durante rollback de SQL Server: {rb_e}")
                    if o_conn:
                        try: o_conn.rollback(); log.log_sql("Oracle", "ROLLBACK"); st.info("Rollback en Oracle completado.")
                        except Exception as rb_e: st.error(f"Error durante rollback de Oracle: {rb_e}")
                finally:
                    if s_conn: s_conn.close()
                    if o_conn: o_conn.close()

st.markdown("---")

# --- SECCIÓN 3: ESTRUCTURA DE LA CAPA DE DATOS ---
st.header("📊 3. Referencia Visual del Ecosistema")
st.write("Estructura lógica de las tablas distribuidas en la infraestructura híbrida.")
col_m, col_s, col_o = st.columns(3)
with col_m:
    st.subheader("📦 MariaDB")
    st.info("**DB:** `gestion_administrativa`")
    with st.expander("Tabla: pacientes", expanded=False):
        st.markdown("Maestro de identidad.")
        try:
            conn = mysql.connector.connect(**DB_CONFIG['mariadb'], database="gestion_administrativa")
            df = pd.read_sql("SELECT * FROM pacientes LIMIT 5", conn)
            st.dataframe(df, use_container_width=True)
            conn.close()
        except Exception as e: st.error(f"No se pudo cargar preview: {e}")
    with st.expander("Tabla: profesionales", expanded=False):
        st.markdown("Datos de personal médico.")
        try:
            conn = mysql.connector.connect(**DB_CONFIG['mariadb'], database="gestion_administrativa")
            df = pd.read_sql("SELECT * FROM profesionales LIMIT 5", conn)
            st.dataframe(df, use_container_width=True)
            conn.close()
        except Exception as e: st.error(f"No se pudo cargar preview: {e}")
with col_s:
    st.subheader("📅 SQL Server")
    st.info("**DB:** `gestion_citas`")
    with st.expander("Tabla: dbo.citas", expanded=False):
        st.markdown("Log de programación y estados.")
        try:
            conn = pymssql.connect(**DB_CONFIG['sqlserver'], database="gestion_citas")
            df = pd.read_sql("SELECT TOP 5 * FROM dbo.citas", conn)
            st.dataframe(df, use_container_width=True)
            conn.close()
        except Exception as e: st.error(f"No se pudo cargar preview: {e}")
with col_o:
    st.subheader("📜 Oracle")
    st.info("**Service:** `XEPDB1`")
    with st.expander("Tabla: historial_atenciones", expanded=False):
        st.markdown("Datos clínicos sensibles.")
        try:
            conn = oracledb.connect(**DB_CONFIG['oracle'])
            df = pd.read_sql("SELECT * FROM historial_atenciones FETCH FIRST 5 ROWS ONLY", conn)
            st.dataframe(df, use_container_width=True)
            conn.close()
        except Exception as e: st.error(f"No se pudo cargar preview: {e}")

st.markdown("---")

# --- SECCIÓN 4: LABORATORIO DE MOTORES ---
st.header("🛠️ 4. Laboratorio de Motores y Pruebas de Carga")
tabs = st.tabs(["📊 Estadísticas Globales", "🗂️ Explorador de Datos", "🔗 Joins Federados", "⚡ Benchmark de Latencia", "🔋 Info del Sistema"])

with tabs[0]:
    st.subheader("Conteo de Registros en Tiempo Real")
    if st.button("Ejecutar Auditoría de Volumetría", key="audit_vol_btn"):
        stats_data = []
        with st.spinner("Consultando motores..."):
            try:
                conn = mysql.connector.connect(**DB_CONFIG['mariadb'], database="gestion_administrativa")
                cursor = conn.cursor()
                for t in ["pacientes", "profesionales"]:
                    query = f"SELECT COUNT(*) FROM {t}"
                    cursor.execute(query)
                    log.log_sql("MariaDB", query)
                    stats_data.append({"Motor": "MariaDB", "Tabla": t, "Registros": cursor.fetchone()[0]})
                conn.close()
            except Exception as e: st.error(f"Error en MariaDB audit: {e}")
            try:
                conn = pymssql.connect(**DB_CONFIG['sqlserver'], database="gestion_citas")
                cursor = conn.cursor()
                query = "SELECT COUNT(*) FROM dbo.citas"
                cursor.execute(query)
                log.log_sql("SQL Server", query)
                stats_data.append({"Motor": "SQL Server", "Tabla": "dbo.citas", "Registros": cursor.fetchone()[0]})
                conn.close()
            except Exception as e: st.error(f"Error en SQL Server audit: {e}")
            try:
                conn = oracledb.connect(**DB_CONFIG['oracle'])
                cursor = conn.cursor()
                query = "SELECT COUNT(*) FROM historial_atenciones"
                cursor.execute(query)
                log.log_sql("Oracle", query)
                stats_data.append({"Motor": "Oracle", "Tabla": "historial_atenciones", "Registros": cursor.fetchone()[0]})
                conn.close()
            except Exception as e: st.error(f"Error en Oracle audit: {e}")
        df_stats = pd.DataFrame(stats_data)
        st.table(df_stats)
        st.bar_chart(df_stats.set_index("Tabla")["Registros"])

with tabs[1]:
    st.subheader("Inspección de Tablas")
    id_column_map = {"pacientes": "paciente_id", "profesionales": "medico_id", "dbo.citas": "cita_id", "historial_atenciones": "atencion_id"}
    c_eng, c_tab = st.columns(2)
    with c_eng: engine_sel = st.selectbox("Motor", ["MariaDB", "SQL Server", "Oracle"], key="exp_eng")
    with c_tab:
        tables = {"MariaDB": ["pacientes", "profesionales"], "SQL Server": ["dbo.citas"], "Oracle": ["historial_atenciones"]}
        table_sel = st.selectbox("Tabla", tables[engine_sel], key="exp_tab")
    search_by_id = st.checkbox("Buscar por ID específico", key="search_by_id_chk")
    search_id_val = st.number_input("ID a buscar", min_value=1, step=1, key="search_id_val") if search_by_id else 0
    limit_sel = st.slider("Límite de filas", 5, 100, 10, key="limit_sel", disabled=search_by_id)
    if st.button(f"Explorar {table_sel}", key="explore_data_btn"):
        try:
            conn, query, params = None, None, None
            if engine_sel == "MariaDB":
                conn = mysql.connector.connect(**DB_CONFIG['mariadb'], database="gestion_administrativa")
                id_col = id_column_map[table_sel]
                if search_by_id and search_id_val > 0:
                    query = f"SELECT * FROM {table_sel} WHERE {id_col} = %s"
                    params = (search_id_val,) # Corregido: Usar tupla para MariaDB
                else:
                    query = f"SELECT * FROM {table_sel} ORDER BY {id_col} DESC LIMIT %s"
                    params = (limit_sel,) # Corregido: Usar tupla para MariaDB
            elif engine_sel == "SQL Server":
                conn = pymssql.connect(**DB_CONFIG['sqlserver'], database="gestion_citas")
                id_col = id_column_map[table_sel]
                if search_by_id and search_id_val > 0:
                    query = f"SELECT * FROM {table_sel} WHERE {id_col} = %s"
                    params = (search_id_val,)
                else:
                    query = f"SELECT TOP {limit_sel} * FROM {table_sel} ORDER BY {id_col} DESC"
                    params = None
            else: # Oracle
                conn = oracledb.connect(**DB_CONFIG['oracle'])
                id_col = id_column_map[table_sel]
                if search_by_id and search_id_val > 0:
                    query = f"SELECT * FROM {table_sel} WHERE {id_col} = :1"
                    params = [search_id_val]
                else:
                    query = f"SELECT * FROM {table_sel} ORDER BY {id_col} DESC FETCH FIRST {limit_sel} ROWS ONLY"
                    params = None
            
            log.log_sql(engine_sel, query, params)
            df_view = pd.read_sql(query, conn, params=params)
            st.dataframe(df_view, use_container_width=True)
            if df_view.empty: st.info("La consulta no devolvió resultados.")
        except Exception as e:
            st.error(f"Error al explorar: {e}")
        finally:
            if conn: conn.close()

with tabs[2]:
    st.subheader("🔗 Orquestación de Reportes Federados")
    st.info("Estas operaciones cruzan datos de motores distintos en la RAM de este Middleware.")
    def get_df_safe(conn_config, db_name, query, engine_name, params=None):
        conn = None
        try:
            if engine_name == "MariaDB": conn = mysql.connector.connect(**conn_config, database=db_name)
            elif engine_name == "SQL Server": conn = pymssql.connect(**conn_config, database=db_name)
            elif engine_name == "Oracle": conn = oracledb.connect(**conn_config)
            log.log_sql(engine_name, query, params)
            df = pd.read_sql(query, conn, params=params)
            df.columns = [c.lower() for c in df.columns] 
            return df
        except Exception as e:
            st.error(f"Error en {engine_name} al obtener datos: {e}")
            return pd.DataFrame()
        finally:
            if conn: conn.close()
    escenario = st.selectbox("Seleccione el Escenario de Datos", [
        "1. Reporte Maestro de Red (MariaDB + SQL Server + Oracle)",
        "2. Carga Laboral Médica (MariaDB + SQL Server)",
        "3. Actividad Clínica Detallada (MariaDB + Oracle)"
    ], key="scenario_sel")
    if st.button(f"🚀 Ejecutar Inteligencia Federada", key="federated_btn"):
        with st.spinner("Sincronizando motores de base de datos..."):
            try:
                if "1" in escenario:
                    st.write("### 🌐 Reporte Consolidado de la Red Hospitalaria")
                    
                    df_m = get_df_safe(DB_CONFIG['mariadb'], "gestion_administrativa", "SELECT paciente_id, nombre FROM pacientes LIMIT 500", "MariaDB")
                    df_s = get_df_safe(DB_CONFIG['sqlserver'], "gestion_citas", "SELECT paciente_id, COUNT(*) as citas FROM dbo.citas GROUP BY paciente_id", "SQL Server")
                    df_o = get_df_safe(DB_CONFIG['oracle'], None, "SELECT paciente_id, COUNT(*) as historial FROM historial_atenciones GROUP BY paciente_id", "Oracle")

                    m1 = pd.merge(df_m, df_s, on="paciente_id", how="left")
                    res = pd.merge(m1, df_o, on="paciente_id", how="left").fillna(0)
                    
                    st.dataframe(res, use_container_width=True)
                    st.caption(f"Se han analizado {len(res)} registros de identidad contra la actividad transaccional.")
                    
                elif "2" in escenario:
                    st.write("### 👨‍⚕️ Carga de Trabajo por Profesional")
                    
                    df_med = get_df_safe(DB_CONFIG['mariadb'], "gestion_administrativa", "SELECT medico_id, nombre as medico, especialidad FROM profesionales", "MariaDB")
                    df_cit = get_df_safe(DB_CONFIG['sqlserver'], "gestion_citas", "SELECT medico_id, COUNT(*) as citas_totales FROM dbo.citas GROUP BY medico_id", "SQL Server")

                    res = pd.merge(df_med, df_cit, on="medico_id", how="inner").sort_values(by="citas_totales", ascending=False)
                    
                    st.table(res)
                    st.bar_chart(res.set_index("medico")["citas_totales"])
                    
                elif "3" in escenario:
                    st.write("### 🏥 Correlación Identidad - Historial Clínico")
                    
                    df_pac = get_df_safe(DB_CONFIG['mariadb'], "gestion_administrativa", "SELECT paciente_id, nombre FROM pacientes LIMIT 200", "MariaDB")
                    df_his = get_df_safe(DB_CONFIG['oracle'], None, "SELECT paciente_id, COUNT(*) as evoluciones FROM historial_atenciones GROUP BY paciente_id", "Oracle")

                    res = pd.merge(df_pac, df_his, on="paciente_id", how="left").fillna(0)
                    
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.write("**Tabla de Auditoría Clínica:**")
                        st.dataframe(res, use_container_width=True)
                    with c2:
                        st.write("**Distribución de Atenciones:**")
                        st.bar_chart(res.set_index("nombre")["evoluciones"])
                    
                st.success("✅ Interconexión federada completada con éxito.")

            except Exception as e:
                st.error(f"❌ Fallo Crítico en la Federación: {str(e)}")

with tabs[3]:
    st.subheader("Prueba de Stress y Tiempo de Respuesta")
    if st.button("Iniciar Test de Latencia", key="latency_btn"):
        latency_results = []
        progress = st.progress(0)
        for i, engine in enumerate(["MariaDB", "SQL Server", "Oracle"]):
            start_time = time.time()
            try:
                if engine == "MariaDB": c = mysql.connector.connect(**DB_CONFIG['mariadb'])
                elif engine == "SQL Server": c = pymssql.connect(**DB_CONFIG['sqlserver'])
                else: c = oracledb.connect(**DB_CONFIG['oracle'])
                cur = c.cursor()
                cur.execute("SELECT 1" if engine != "Oracle" else "SELECT 1 FROM DUAL")
                cur.fetchone()
                end_time = time.time()
                diff = (end_time - start_time) * 1000
                latency_results.append({"Motor": engine, "Latencia (ms)": round(diff, 2), "Status": "Óptimo 🚀"})
                c.close()
            except:
                latency_results.append({"Motor": engine, "Latencia (ms)": 0, "Status": "Timeout 💀"})
            progress.progress((i + 1) / 3)
        df_lat = pd.DataFrame(latency_results)
        st.table(df_lat)
        st.line_chart(df_lat.set_index("Motor")["Latencia (ms)"])
        
with tabs[4]:
    st.subheader("🕵️ Metadata de Infraestructura")
    if st.button("Extraer Firmas de Motores", key="metadata_btn"):
        info_data = []
        try:
            conn = mysql.connector.connect(**DB_CONFIG['mariadb'])
            cur = conn.cursor()
            cur.execute("SELECT @@version, @@version_compile_os, @@hostname")
            v, os, host = cur.fetchone()
            info_data.append(["MariaDB", f"Versión: {v} | OS: {os} | Host: {host}"])
            conn.close()
        except Exception as e: info_data.append(["MariaDB", f"Sin respuesta ({e})"])
        try:
            conn = pymssql.connect(**DB_CONFIG['sqlserver'])
            cur = conn.cursor()
            cur.execute("SELECT @@VERSION")
            v = cur.fetchone()[0]
            info_data.append(["SQL Server", v.split('\n')[0]])
            conn.close()
        except Exception as e: info_data.append(["SQL Server", f"Sin respuesta ({e})"])
        try:
            conn = oracledb.connect(**DB_CONFIG['oracle'])
            cur = conn.cursor()
            cur.execute("SELECT banner FROM v$version")
            v = cur.fetchone()[0]
            info_data.append(["Oracle", v])
            conn.close()
        except Exception as e: info_data.append(["Oracle", f"Sin respuesta ({e})"])
        st.table(pd.DataFrame(info_data, columns=["Motor", "Detalle Técnico"]))