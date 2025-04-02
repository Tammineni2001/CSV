from sqlalchemy import text
from db import initialize_connection

engine, session, Base = initialize_connection("CSV_DASHBOARD_DB")

def table_exists(schema, table_name):
    with engine.connect() as conn:
        query = text(f"""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = '{schema}' AND table_name = '{table_name}'
        )
        """)
        result = conn.execute(query).scalar()
        return result

if __name__ == "__main__":
    schema = "PUBLIC"
    table_name = "SHEET1"
    exists = table_exists(schema, table_name)
    if exists:
        print(f"✅ The table '{schema}.{table_name}' exists!")
    else:
        print(f"❌ The table '{schema}.{table_name}' does NOT exist.")
