import requests

API_URL = "http://127.0.0.1:5000/api/csv1/delete-table"

def test_delete_table():
    table_name = "SHEET1"
    schema = "PUBLIC"
    data = {"table_name": table_name, "schema": schema}
    response = requests.delete(API_URL, json=data)
    if response.status_code == 200:
        print("✅ Delete request successful!")
        print("🔹 Response Data:", response.json())
    else:
        print(f"❌ Delete request failed with status code {response.status_code}")
        print("🔹 Error:", response.text)

if __name__ == "__main__":
    test_delete_table()
