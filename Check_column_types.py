import pandas as pd
import chardet

file_path = "C:\\Users\\TA115023\\Desktop\\Data\\ORDERS 1.csv"

# Detect file encoding
with open(file_path, "rb") as file:
    raw_data = file.read()
    encoding = chardet.detect(raw_data)["encoding"]

# Read CSV file with correct encoding
df = pd.read_csv(file_path, encoding=encoding, delimiter="\t", on_bad_lines="skip")

# Clean column names
df.columns = [col.strip().upper() for col in df.columns]

# Convert columns to proper data types
df["ORDER_ID"] = pd.to_numeric(df["ORDER_ID"], errors="coerce").fillna(0).astype(int)
df["ORDER_DATE"] = pd.to_datetime(df["ORDER_DATE"], errors="coerce")
df["SHIP_DATE"] = pd.to_datetime(df["SHIP_DATE"], errors="coerce")
df["CUSTOMER_ID"] = pd.to_numeric(df["CUSTOMER_ID"], errors="coerce").fillna(0).astype(int)
df["PRODUCT_ID"] = pd.to_numeric(df["PRODUCT_ID"], errors="coerce").fillna(0).astype(int)
df["SALES"] = pd.to_numeric(df["SALES"], errors="coerce").fillna(0).astype(int)
df["QUANTITY"] = pd.to_numeric(df["QUANTITY"], errors="coerce").fillna(0).astype(int)
df["DISCOUNT"] = pd.to_numeric(df["DISCOUNT"], errors="coerce").fillna(0).astype(int)
df["PROFIT"] = pd.to_numeric(df["PROFIT"], errors="coerce").fillna(0).astype(float)
df["CASE_ID"] = pd.to_numeric(df["CASE_ID"], errors="coerce").fillna(0).astype(int)


df["MONTH_NAME"] = df["MONTH_NAME"].astype("category")
df["QUARTER_NAME"] = df["QUARTER_NAME"].astype("category")
df["SHIP_MODE"] = df["SHIP_MODE"].astype("category")
df["REGION"] = df["REGION"].astype("category")


# Print sample data and column types
print("Sample Data:")
print(df.head())
print("\nColumn Data Types:")
print(df.dtypes)
