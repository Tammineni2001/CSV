from flask import Blueprint, request, jsonify
import pandas as pd
import chardet
from db import initialize_connection

csv_blueprint = Blueprint("csv_blueprint", __name__)
engine, session, Base = initialize_connection("CSV_DASHBOARD_DB")

def save_to_database(df, table_name, schema):
    table_name_upper = table_name.upper()
    df.columns = [col.upper() for col in df.columns]
    with engine.connect() as conn:
        df.to_sql(table_name_upper, conn, schema=schema, if_exists="replace", index=False)
    return {"message": f"Data saved to table '{schema}.{table_name_upper}' successfully"}

@csv_blueprint.route("/upload-csv", methods=["POST"])
def upload_csv():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected for uploading"}), 400

    file_name = file.filename.rsplit(".", 1)[0].strip().replace(" ", "_").upper()
    schema = request.form.get("schema", "PUBLIC").strip()

    try:
        raw_data = file.read()
        encoding = chardet.detect(raw_data)["encoding"]
        file.seek(0)
        df = pd.read_csv(file, encoding=encoding, on_bad_lines="skip", sep=None, engine="python")
        df.columns = [col.strip().upper() for col in df.columns]

        for column in df.columns:
            if pd.api.types.is_string_dtype(df[column]) or pd.api.types.is_object_dtype(df[column]):
                if "DATE" in column.upper():
                    df[column] = pd.to_datetime(df[column], errors="coerce")
                elif df[column].nunique() < 50 or column.upper() == "GENDER":
                    df[column] = df[column].fillna("UNKNOWN").astype("category")
                else:
                    df[column] = df[column].fillna("UNKNOWN").astype(str)
            elif pd.api.types.is_numeric_dtype(df[column]):
                if df[column].dropna().apply(lambda x: isinstance(x, int) or (isinstance(x, float) and x.is_integer())).all():
                    df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0).astype(int)
                else:
                    df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

        for column in df.select_dtypes(include=["object"]).columns:
            if df[column].nunique() < 50:
                df[column] = df[column].astype("category")

        print("Sample Data:")
        print(df.head())
        print("\nColumn Data Types:")
        print(df.dtypes)        

        result = save_to_database(df, file_name, schema)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"An error occurred while processing the file: {str(e)}"}), 500

















           
            
           