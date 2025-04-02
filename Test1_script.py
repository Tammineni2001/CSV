import requests

# Your Flask API URL for Excel upload (replace with the correct URL)
EXCEL_API_URL = "http://127.0.0.1:5000/api/csv1/upload-excel"

def test_upload_excel():
    # File path for the Excel file
    file_path = "C:\\Users\\TA115023\\Desktop\\Data\\TANXL.xls"
    schema = "PUBLIC"  # Schema name

    # Open the file in binary mode
    with open(file_path, "rb") as file:
        files = {"file": file}  # File data
        data = {"schema": schema}  # Schema as form data

        # Make the POST request
        response = requests.post(EXCEL_API_URL, files=files, data=data)

        # Check response status
        if response.status_code == 200:
            print("✅ Excel API request successful!")
            print("🔹 Response Data:", response.json())  # Print responses for all sheets
        else:
            print(f"❌ Excel API request failed with status code {response.status_code}")
            print("🔹 Error:", response.text)

if __name__ == "__main__":
    test_upload_excel()