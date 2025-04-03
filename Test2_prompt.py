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
    
print("Environment variables loaded successfully.")

# Configure OpenAI client for Azure OpenAI
openai.api_type = "azure"
openai.api_key = api_key
openai.api_base = endpoint
openai.api_version = api_version

# Define KPI Prompt Template
kpi_prompt = Template("""
You are a data analyst specializing in deriving **unique, high-impact KPIs** that directly address key business challenges. I am providing structured data **in the form of column names and their respective data types** extracted from a structured dataset. Your task is to analyze the dataset schema and craft **powerful KPIs** that provide actionable insights for strategic decision-making.

### Dataset Schema
Here are the column names and their respective data types:
$formatted_columns

### Objective:
**Generate KPIs that are uniquely meaningful**, avoiding redundancy and overly simplistic metrics. Your KPIs must focus on solving **high-priority business problems**, with clear relevance to objectives such as:
   - Maximizing revenue and profitability
   - Identifying high-value customer segments
   - Improving operational efficiency
   - Understanding customer satisfaction and loyalty
   - Uncovering growth opportunities or emerging market trends

### Output Format:
Return the output strictly as a **valid JSON array**. Do not include any explanations, headings, or extra text outside the JSON array. The JSON format must strictly follow this structure:

[
    {
        "kpi": "KPI name",
        "description": "A detailed, actionable description of the KPI. Include the **business relevance**, calculation method, and the specific insights it provides.",
        "columns": "Comma-separated columns used for the KPI"
    }
]

### Constraints:
1. Ensure every KPI is **unique**, avoiding duplication across batches.
2. Avoid any overly simplistic KPIs like "Total Revenue" or "Average Order Value" unless paired with deeper analysis (e.g., segmented by customer demographics or product categories).
3. Use at least **two or more columns** in every KPI to ensure multi-dimensional analysis and insights.
4. Ensure the output JSON is clean and well-formed, with no redundant descriptions or headings.
5. **Strictly return only the JSON array**; do not include any additional text or explanations.

""")

# Function to extract schema dynamically from CSV file
def extract_schema_from_csv(file_path):
    df = pd.read_csv(file_path)
    for col in df.columns:
        if df[col].dtype == 'float64':
            non_null_values = df[col].dropna()  # Exclude NaN values for type check
            if non_null_values.apply(lambda x: x.is_integer()).all():
                df[col] = df[col].fillna(0).astype(int)  # Replace NaN with 0 and safely convert to int type
            else:
                df[col] = df[col].fillna(df[col].mean())  # Replace NaN with column mean for non-integer data
    schema = [f"{col} ({df[col].dtype})" for col in df.columns]
    return ", ".join(schema)

# Function to interact with the LLM
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



# Function to dynamically generate the KPI prompt
def generate_kpi_prompt(formatted_columns):
    return kpi_prompt.substitute(formatted_columns=formatted_columns)

if __name__ == "__main__":
    # Path to your updated CSV file
    csv_file_path = "C:\\Users\\TA115023\\Desktop\\Data\\csv\\TRACKING.csv"
    formatted_columns = extract_schema_from_csv(csv_file_path)
    print("Extracted Schema from CSV:\n", formatted_columns)
    prompt = generate_kpi_prompt(formatted_columns)
    print("\nGenerated KPI Prompt:\n", prompt)
    kpi_response = llm_response(prompt)
    parsed_kpis = validate_json_response(kpi_response)
    if parsed_kpis:
        print("\nParsed KPI Content:")
        print(json.dumps(parsed_kpis, indent=4))
    else:
        print("The response could not be validated as JSON.")
