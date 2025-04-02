import openai
import os
from dotenv import load_dotenv


load_dotenv()


openai.api_type = "azure"
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")

# Function to generate SQL queries based on user prompt
def generate_sql():
    dataset_structure = """Transaction_ID, Customer_ID, State, Country, Total_Amount, Total_Purchases, Amount, Product_Category, Product_Brand"""
    
    prompt = f"""For the given dataset structure ({dataset_structure}), generate SQL queries to calculate the following:
    1. Year-wise Sales: Sum of Total_Amount grouped by Year.
    2. State-wise Sales: Sum of Total_Amount grouped by State.
    3. State-wise Total Purchases: Sum of Total_Purchases grouped by State.
    4. State-wise Amount: Sum of Amount grouped by State.
    5. Country-wise Total Purchases: Sum of Total_Purchases grouped by Country.
    6. Country-wise Profit: Difference between the sum of Total_Amount and Amount grouped by Country.
    7. Number of Purchases by Product Category: Sum of Total_Purchases grouped by Product_Category.
    8. Number of Purchases by Product Brand: Sum of Total_Purchases grouped by Product_Brand.
    9. Average Purchase Amount by Country: Average Total_Amount grouped by Country.
    10. Customer Retention Rate by Country: Percentage of returning customers grouped by Country."""

    try:
        response = openai.ChatCompletion.create(
            engine=os.getenv("AZURE_DEPLOYMENT_NAME"),
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates SQL queries."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0
        )
        print("Generated SQL Queries:")
        print(response["choices"][0]["message"]["content"].strip())
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    generate_sql()
