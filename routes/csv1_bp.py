from flask import Blueprint, request, jsonify
import pandas as pd
import chardet
from sqlalchemy import text
from db import initialize_connection
import datetime

csv1_blueprint = Blueprint("csv1_blueprint", __name__)
engine, session, Base = initialize_connection("CSV_DASHBOARD_DB")

def save_to_database(df, table_name, schema, if_exists="replace"):
    try:
        table_name_upper = table_name.upper()
        df.columns = [col.upper() for col in df.columns]
        with engine.connect() as conn:
            df.to_sql(table_name_upper, conn, schema=schema, if_exists=if_exists, index=False)
        return {"message": f"Data saved to table '{schema}.{table_name_upper}' successfully"}
    except Exception as e:
        return {"error": f"An error occurred while saving to the database: {str(e)}"}

@csv1_blueprint.route("/upload-excel", methods=["POST"])
def upload_excel():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected for uploading"}), 400

    schema = request.form.get("schema", "PUBLIC").strip()
    try:
        if file.filename.endswith('.csv'):
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            file.seek(0)
            df = pd.read_csv(file, encoding=encoding, on_bad_lines='skip')
            table_name = request.form.get("table_name", "default_table").strip()
            result = save_to_database(df, table_name, schema)
            return jsonify(result)
        elif file.filename.endswith('.xls') or file.filename.endswith('.xlsx'):
            excel_data = pd.ExcelFile(file)
            responses = {}
            for sheet_name in excel_data.sheet_names:
                df = excel_data.parse(sheet_name)
                table_name = sheet_name.strip()
                result = save_to_database(df, table_name, schema)
                responses[sheet_name] = result
            return jsonify(responses)
        else:
            return jsonify({"error": "Unsupported file type"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred while processing the file: {str(e)}"}), 500

# @csv1_blueprint.route("/update-excel", methods=["PUT"])
# def update_excel():
#     if "file" not in request.files:
#         return jsonify({"error": "No file part in the request"}), 400
#     file = request.files["file"]
#     if file.filename == "":
#         return jsonify({"error": "No file selected for uploading"}), 400
#     schema = request.form.get("schema", "PUBLIC").strip()
#     try:
#         if file.filename.endswith(".csv"):
#             raw_data = file.read()
#             result = chardet.detect(raw_data)
#             encoding = result['encoding']
#             file.seek(0)
#             df = pd.read_csv(file, encoding=encoding, on_bad_lines='skip')
#             table_name = file.filename.rsplit(".", 1)[0].strip().upper()
#             result = save_to_database(df, table_name, schema, if_exists="append")
#             return jsonify(result)
#         elif file.filename.endswith(".xls") or file.filename.endswith(".xlsx"):
#             excel_data = pd.ExcelFile(file)
#             responses = {}
#             for sheet_name in excel_data.sheet_names:
#                 df = excel_data.parse(sheet_name)
#                 table_name = sheet_name.strip().upper()
#                 result = save_to_database(df, table_name, schema, if_exists="append")
#                 responses[sheet_name] = result
#             return jsonify(responses)
#         else:
#             return jsonify({"error": "Unsupported file type"}), 400
#     except Exception as e:
#         return jsonify({"error": f"An error occurred while updating the table: {str(e)}"}), 500



# def table_exists(schema, table_name):
#     with engine.connect() as conn:
#         query = text(f"""
#         SELECT EXISTS (
#             SELECT FROM information_schema.tables
#             WHERE table_schema = '{schema}' AND table_name = '{table_name}'
#         )
#         """)
#         result = conn.execute(query).scalar()
#         return result


# @csv1_blueprint.route("/get-data", methods=["GET"])
# def get_data():
#     table_name = request.args.get("table_name", "").strip()
#     schema = request.args.get("schema", "PUBLIC").strip()
#     if not table_name:
#         return jsonify({"error": "Table name is required"}), 400
#     if not table_exists(schema, table_name):
#         return jsonify({"error": f"Table '{schema}.{table_name}' does not exist"}), 404
#     with engine.connect() as conn:
#         query = f'SELECT * FROM "{schema}"."{table_name}"'
#         result = pd.read_sql(query, conn)
#         data = result.to_dict(orient="records")
#         serialized_data = [
#             {key: (str(value) if isinstance(value, (datetime.time, datetime.datetime)) else value)
#              for key, value in row.items()}
#             for row in data
#         ]
#         return jsonify(serialized_data)

# @csv1_blueprint.route("/delete-table", methods=["DELETE"])
# def delete_table():
#     table_name = request.json.get("table_name", "").strip().upper()
#     schema = request.json.get("schema", "PUBLIC").strip()
#     if not table_name:
#         return jsonify({"error": "Table name is required"}), 400
#     with engine.connect() as conn:
#         conn.execute(text(f"DROP TABLE {schema}.{table_name}"))
#         return jsonify({"message": f"Table '{schema}.{table_name}' deleted successfully"})
