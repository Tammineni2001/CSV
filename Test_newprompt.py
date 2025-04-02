import openai
import os
from dotenv import load_dotenv
from string import Template

# Load environment variables
load_dotenv()

# Set up OpenAI API configuration
api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

if not all([api_key, endpoint, deployment_name, api_version]):
    raise ValueError("One or more environment variables are missing! Check your .env file.")

openai.api_type = "azure"
openai.api_key = api_key
openai.api_base = endpoint
openai.api_version = api_version

# Define the prompt template
kpi_prompt = Template("""
You are an expert data analyst specializing in generating business insights. I am providing you with structured data from a CSV file. Your task is to analyze this data and generate key business performance indicators (KPIs) strictly based on the columns provided.
 
Here is the CSV data:
$formatted_columns
 
Steps to follow:
1. Identify the column names and their relevance to business KPIs.
2. Select a minimum of two columns from the data to create meaningful KPIs.
3. Generate business KPIs such as (but not limited to) growth rates, trends, average values, or ratios.
4. Provide a brief explanation of how each KPI is calculated and its business significance.
 
Constraints:
- Only use the data from the provided columns to calculate the KPIs.
- Do not assume additional data or context outside of the CSV.
- Clearly mention the selected columns and how they are utilized.
 
Output format:
1. List of selected columns with their roles.
2. KPIs with calculations and explanations.
3. Suggestions for leveraging the KPIs for business decision-making.
""")

def test_prompt():
    # Replace with your formatted column names
    formatted_columns = """Transaction_ID, Customer_ID, State, Total_Purchases, Total_Amount"""
    
    # Generate the final prompt
    final_prompt = kpi_prompt.substitute(formatted_columns=formatted_columns)
    print("Testing Prompt:\n")
    print(final_prompt)
    
    try:
        # Send the prompt to Azure OpenAI and get a response
        response = openai.ChatCompletion.create(
            engine=deployment_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": final_prompt}
            ],
            max_tokens=1000,
            temperature=0
        )
        
        # Print the response from the LLM
        print("\nResponse from LLM:")
        print(response["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    test_prompt()
