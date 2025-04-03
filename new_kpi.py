import openai
import os
import json
import pandas as pd
from dotenv import load_dotenv
from string import Template
import re

# Load environment variables
load_dotenv()

# Validate and load OpenAI API credentials from environment variables
api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

if not all([api_key, endpoint, deployment_name, api_version]):
    raise ValueError("Missing environment variables! Please check your .env file.")

# Configure OpenAI client for Azure OpenAI
openai.api_type = "azure"
openai.api_key = api_key
openai.api_base = endpoint
openai.api_version = api_version

# Define KPI Prompt Template
kpi_prompt = Template("""
You are an expert data analyst specializing in generating business insights. I am providing you with structured data from a CSV file. Your task is to analyze this data and generate key business performance indicators (KPIs) strictly based on the columns provided.

### Dataset Schema:
$formatted_columns

### Steps:
1. Identify the column names and their relevance to business KPIs.
2. Select a minimum of two columns from the data to create meaningful KPIs.
3. Generate business KPIs such as (but not limited to) growth rates, trends, average values, or ratios.
4. Provide a brief explanation of how each KPI is calculated and its business significance.

### Constraints:
- Only use the data from the provided columns to calculate the KPIs.
- Do not assume additional data or context outside of the provided schema.
- Return ONLY a valid JSON array following the format below. DO NOT include extra text, headers, or explanations outside the JSON structure.

### Output Format:
[
    {
        "kpi": "KPI name",
        "description": "Detailed explanation of the KPI, including how it is calculated and its business significance.",
        "columns": "Comma-separated columns used for the KPI"
    }
]
""")

# Define SQL Prompt Template
sql_prompt = Template("""
Your task is to generate SQL queries based on the provided table structure and business KPIs description. The table structure includes various columns related to the $table_name table, and the business KPIs describe specific metrics that need to be calculated.

**Table Name**: $table_name  
**Table Columns:**  
$columns  

**Business KPIs:**  
$kpis  

**Instructions:**
- Generate SQL queries for each provided business KPI description based on the table columns.
- The database is PostgreSQL. Ensure the queries are PostgreSQL-compatible.
- Only use the provided columns, ensure their datatypes are respected, and do NOT include invalid queries.
- Use the provided columns, and all columns should be in uppercase and wrapped in double quotes.
- Ensure the columns and table names in the query are in uppercase and wrapped in double quotes (e.g., SELECT "COLUMN" FROM "DATABASE"."SCHEMA"."TABLE").
- Return the output as valid JSON, strictly following this structure:

[
    {
        "kpi": "Provided KPI name",
        "description": "Provided description",
        "columns": "Comma-separated columns (only those required for the KPI)",
        "sql": "SQL query to calculate the KPI"
    }
]
""")

# Function to dynamically generate the KPI prompt
def generate_kpi_prompt(formatted_columns):
    return kpi_prompt.substitute(formatted_columns=formatted_columns)

# Function to dynamically generate the SQL prompt
def generate_sql_prompt(table_name, columns, kpis):
    return sql_prompt.substitute(table_name=table_name, columns=columns, kpis=kpis)

# Function to interact with OpenAI
def llm_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            engine=deployment_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=1000
        )
        response_content = response["choices"][0]["message"]["content"].strip()
        if not response_content:
            raise ValueError("Received an empty response from the LLM.")
        return response_content
    except Exception as e:
        print(f"Error during LLM call: {e}")
        return ""

# Function to validate and parse JSON response
def validate_json_response(response):
    """
    Validates and extracts a JSON array from the given text response.
    Uses regex to locate and parse the JSON correctly.
    
    Args:
        response (str): The raw response text to extract JSON from.

    Returns:
        list: Parsed JSON array as a Python object, or None if extraction/parsing fails.
    """
    try:
        # Use regex to locate and extract JSON array within the text response
        json_match = re.search(r"\[.*\]", response, re.DOTALL)  # Match JSON array
        if json_match:
            json_str = json_match.group(0)  # Extract JSON string
            return json.loads(json_str)  # Convert the JSON string into a Python object
        else:
            raise ValueError("No valid JSON array found in the response.")
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return None


# Main execution block
if __name__ == "__main__":
    # Example for KPI generation
    csv_file_path = "C:\\Users\\TA115023\\Desktop\\Data\\csv\\RETURNS.csv"  # Path to your CSV file
    df = pd.read_csv(csv_file_path)
    formatted_columns = ", ".join([f"{col.upper()} ({df[col].dtype})" for col in df.columns])
    
    # Generate KPI prompt
    kpi_prompt_text = generate_kpi_prompt(formatted_columns)
    print("Generated KPI Prompt:\n", kpi_prompt_text)

    # Fetch KPI response
    kpi_response = llm_response(kpi_prompt_text)
    print("\nRaw KPI Response:\n", kpi_response)

    # Validate and parse the JSON response
    parsed_kpis = validate_json_response(kpi_response)
    if parsed_kpis:
        print("\nParsed KPI Content:")
        print(json.dumps(parsed_kpis, indent=4))  # Print parsed KPIs in a pretty format
    else:
        print("Failed to parse KPI JSON.")

    # Example for SQL generation
    table_name = "RETURNS"
    columns = ", ".join([f'"{col.upper()}" ({df[col].dtype})' for col in df.columns])
    kpis = "\n".join([f"{item['kpi']}: {item['description']}" for item in parsed_kpis]) if parsed_kpis else "No valid KPIs available."

    # Generate SQL prompt
    sql_prompt_text = generate_sql_prompt(table_name, columns, kpis)
    print("\nGenerated SQL Prompt:\n", sql_prompt_text)

    # Fetch SQL response
    sql_response = llm_response(sql_prompt_text)
    parsed_sql = validate_json_response(sql_response)
    if parsed_sql:
        print("\nParsed SQL Content:")
        print(json.dumps(parsed_sql, indent=4))  # Print parsed SQL in a pretty format
    else:
        print("Failed to validate SQL JSON.")
