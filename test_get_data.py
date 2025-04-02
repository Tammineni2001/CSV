import requests

API_URL = "http://127.0.0.1:5000/api/csv1/get-data"

def test_get_data():
    table_name = "SHEET1"
    schema = "PUBLIC"
    params = {"table_name": table_name, "schema": schema}
    print("🔹 Sending Request with Parameters:", params)
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        print("✅ Get request successful!")
        print("🔹 Retrieved Data:", response.json())
    else:
        print(f"❌ Get request failed with status code {response.status_code}")
        print("🔹 Error:", response.text)

if __name__ == "__main__":
    test_get_data()
