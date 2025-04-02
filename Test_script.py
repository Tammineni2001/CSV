import requests

# # Your Flask API URL for CSV upload (replace with the correct URL)
# API_URL = "http://127.0.0.1:5000/api/csv/upload-csv"

# def test_upload_csv():
#     # File path for the .csv file
#     file_path = "C:\\Users\\TA115023\\Desktop\\Data\\Excel.csv"
#     schema = "PUBLIC"  # Schema name

#     # Open the file in binary mode
#     with open(file_path, "rb") as file:
#         files = {"file": file}  # File data
#         data = {"schema": schema}  # Schema as form data

#         # Make the POST request
#         response = requests.post(API_URL, files=files, data=data)

#         # Check response status
#         if response.status_code == 200:
#             print("✅ API request successful!")
#             print("🔹 Response Data:", response.json())  # Print API response
#         else:
#             print(f"❌ API request failed with status code {response.status_code}")
#             print("🔹 Error:", response.text)

# if __name__ == "__main__":
#     test_upload_csv()




# Your Flask API URL for CSV upload (replace with the correct URL)
API_URL = "http://127.0.0.1:5000/api/csv/upload-csv"

def test_upload_csv():
    # File path for the .csv file
    file_path = "C:/Users/TA115023/Desktop/Data/ORDERS 1.csv"
    schema = "PUBLIC"  # Schema name

    # Open the file in binary mode
    with open(file_path, "rb") as file:
        files = {"file": file}  # File data
        data = {"schema": schema}  # Schema as form data

        # Make the POST request
        response = requests.post(API_URL, files=files, data=data)

        # Check response status
        if response.status_code == 200:
            print("✅ API request successful!")
            print("🔹 Response Data:", response.json())  # Print API response
        else:
            print(f"❌ API request failed with status code {response.status_code}")
            print("🔹 Error:", response.text)

if __name__ == "__main__":
    test_upload_csv()
