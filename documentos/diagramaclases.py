# Este script genera la definición del diagrama en formato Mermaid
# Puedes copiar el resultado en: https://mermaid.live/

def generar_diagrama():
    mermaid_code = """
classDiagram
    direction LR
    
    class MariaDB_Admin {
        +paciente_id: int (PK)
        +medico_id: int (PK)
        nombre: varchar
        especialidad: varchar
    }
    
    class SQLServer_Citas {
        +cita_id: int (PK)
        #paciente_id: int (FK)
        #medico_id: int (FK)
        fecha_cita: datetime
        estado: varchar
    }
    
    class Oracle_Clinica {
        +atencion_id: number (PK)
        #cita_id: number (FK)
        #paciente_id: number (FK)
        fecha_atencion: timestamp
        diagnostico: varchar2
        tratamiento: varchar2
    }

    MariaDB_Admin --o SQLServer_Citas : "paciente_id / medico_id"
    SQLServer_Citas --o Oracle_Clinica : "cita_id"
    MariaDB_Admin --o Oracle_Clinica : "paciente_id"
    """
    print("\n--- COPIA EL SIGUIENTE CÓDIGO EN mermaid.live PARA VER EL DIAGRAMA ---")
    print(mermaid_code)
    print("----------------------------------------------------------------------")

if __name__ == "__main__":
    generar_diagrama()
