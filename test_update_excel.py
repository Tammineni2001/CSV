import requests

API_URL = "http://127.0.0.1:5000/api/csv1/update-excel"

def test_update_excel():
    file_path = "C:\\Users\\TA115023\\Desktop\\Data\\Updated_TANXL.xls"
    schema = "PUBLIC"
    with open(file_path, "rb") as file:
        files = {"file": file}
        data = {"schema": schema}
        response = requests.put(API_URL, files=files, data=data)
        if response.status_code == 200:
            print("✅ Update request successful!")
            print("🔹 Response Data:", response.json())
        else:
            print(f"❌ Update request failed with status code {response.status_code}")
            print("🔹 Error:", response.text)

if __name__ == "__main__":
    test_update_excel()
