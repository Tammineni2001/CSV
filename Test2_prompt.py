import openai
import os
import json
from dotenv import load_dotenv
from string import Template

# Load environment variables
load_dotenv()

# Load OpenAI API credentials from environment variables
api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

# Validate environment variables
if not all([api_key, endpoint, deployment_name, api_version]):
    raise ValueError("One or more environment variables are missing! Check your .env file.")

# Configure OpenAI client for Azure OpenAI
openai.api_type = "azure"
openai.api_key = api_key
openai.api_base = endpoint
openai.api_version = api_version

# Define KPI Prompt Template
kpi_prompt = Template("""
You are an expert data analyst specializing in generating business insights. I am providing you with structured data **in the form of column names only**. Your task is to generate key business performance indicators (KPIs) strictly based on these columns.

Here are the column names:
$formatted_columns

Steps to follow:
1. Identify the column names and their relevance to business KPIs.
2. Select a minimum of two columns from the data to create meaningful KPIs.
3. Generate business KPIs such as (but not limited to) growth rates, trends, average values, or ratios.
4. Provide a brief explanation of how each KPI is calculated and its business significance.

Output format (valid JSON array of objects):
[
    {
        "kpi_name": "Name of the KPI",
        "formula": "How the KPI is calculated using the columns",
        "explanation": "Brief explanation of the business significance of the KPI",
        "columns_used": ["Column1", "Column2", ...]
    },
    ...
]

Important Notes:
- Only provide a valid JSON array in your response.
- Do not include additional text, comments, or explanations outside the JSON array.
""")

# Function to Interact with LLM
def llm_response(prompt, client):
    try:
        response = client.ChatCompletion.create(
            engine=os.getenv("AZURE_DEPLOYMENT_NAME"),  # Use Azure deployment name as engine
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=1000  # Adjust token limit as needed
        )
        
        response_content = response["choices"][0]["message"]["content"].strip()
        if not response_content:
            raise ValueError("Received an empty response from the LLM.")
        
        return response_content
    except Exception as e:
        print(f"Error during LLM call: {e}")
        return ""  # Return empty string in case of failure

# Function to Generate KPIs in Array of Objects Format
def generateKPIs(client, formatted_columns):
    print('Preparing KPI prompt...')
    final_kpi_prompt = kpi_prompt.substitute(formatted_columns=formatted_columns)
    print('Final KPI Prompt:\n', final_kpi_prompt)
    
    try:
        # Call LLM to generate KPIs
        kpi_response = llm_response(final_kpi_prompt, client)
        print("Raw KPI Response:\n", kpi_response)

        # Parse KPI response into structured objects
        try:
            kpi_content = json.loads(kpi_response)  # Parse the JSON output
            print("Parsed KPI Content:\n", kpi_content)
            return kpi_content
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON response. Ensure the prompt strictly enforces JSON output. Raw response:\n{kpi_response}")

    except Exception as e:
        print(f"Error occurred during KPI generation: {e}")
        return []

# Main Execution Block
if __name__ == "__main__":
    # Example usage
    formatted_columns = """Transaction_ID, Customer_ID, State, Total_Purchases, Total_Amount"""
    client = openai  # Assuming OpenAI client has been initialized
    
    # Run KPI generation testing
    kpis = generateKPIs(client, formatted_columns)
    print("\nGenerated KPIs:\n", kpis)
