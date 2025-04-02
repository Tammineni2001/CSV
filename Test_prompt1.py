# import openai
# import os
# import json
# import pandas as pd
# from sqlalchemy import create_engine, text
# from dotenv import load_dotenv
# from string import Template

# # Load environment variables from .env file
# load_dotenv()

# # Load OpenAI API credentials
# api_key = os.getenv("AZURE_OPENAI_API_KEY")
# endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
# deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME")
# api_version = os.getenv("AZURE_OPENAI_API_VERSION")

# if not all([api_key, endpoint, deployment_name, api_version]):
#     raise ValueError("One or more environment variables are missing! Check your .env file.")

# # Configure OpenAI client for Azure OpenAI
# openai.api_type = "azure"
# openai.api_key = api_key
# openai.api_base = endpoint
# openai.api_version = api_version

# # KPI Prompt Template
# kpi_prompt = Template("""
# You are an expert data analyst specializing in generating business insights. I am providing you with structured data from a CSV file. Your task is to analyze this data and generate key business performance indicators (KPIs) strictly based on the columns provided.
 
# Here is the CSV data:
# $formatted_columns
 
# Steps to follow:
# 1. Identify the column names and their relevance to business KPIs.
# 2. Select a minimum of two columns from the data to create meaningful KPIs.
# 3. Generate business KPIs such as (but not limited to) growth rates, trends, average values, or ratios.
# 4. Provide a brief explanation of how each KPI is calculated and its business significance.
 
# Constraints:
# - Only use the data from the provided columns to calculate the KPIs.
# - Do not assume additional data or context outside of the CSV.
# - Clearly mention the selected columns and how they are utilized.
 
# Output format:
# 1. List of selected columns with their roles.
# 2. KPIs with calculations and explanations.
# 3. Suggestions for leveraging the KPIs for business decision-making.
# """)

# # SQL Prompt Template for Queries
# sql_prompt = Template("""
# Your task is to generate SQL queries based on the provided table structure and business KPIs description. The table structure includes various columns related to the $table_name table, and the business KPIs describe specific metrics that need to be calculated.
# **Table Name**: $table_name
# **Table Columns:**
# $formatted_columns
 
# **Business KPIs:** $kpis
 
# **Instructions:**
# - Generate SQL queries for each provided business KPI description based on the table columns.
# - Ensure that all columns and table names in the query are in uppercase and wrapped in double quotes.
# - Generate PostgreSQL-compatible syntax queries.
# - Use the provided columns only, and see their datatypes while constructing the queries.
# - Ensure the queries are valid and based only on the provided columns.
 
# Output format:
# {
#     "Queries": [
#                 {
#                     "description": "provided description",
#                     "kpi": "provided KPI name",
#                     "columns": "comma-separated columns (do not add any extra columns or text just provide the columns from the provided structure above that are needed for this KPI)",
#                     "sql": "sql query"
#                 },
#             ...
#     ]
# }
# """)

# # Function to Generate KPIs and SQL Queries
# def generateKPIs(client, formatted_columns, table_name):
#     print('Preparing KPI prompt...')
#     final_kpi_prompt = kpi_prompt.substitute(formatted_columns=formatted_columns)
#     print('Final KPI Prompt:\n', final_kpi_prompt)
    
#     # Generate KPIs using LLM
#     kpi_response = llm_response(final_kpi_prompt, client)
#     kpi_content = json.loads(kpi_response)
#     print("KPI Content Generated:\n", kpi_content)
    
#     # Convert KPIs into a string for the SQL prompt
#     str_kpis = str(kpi_content['KPIs'])
    
#     print('Preparing SQL prompt...')
#     final_sql_prompt = sql_prompt.substitute(formatted_columns=formatted_columns, kpis=str_kpis, table_name=table_name)
#     print('Final SQL Prompt:\n', final_sql_prompt)
    
#     # Generate SQL Queries using LLM
#     sql_response = llm_response(final_sql_prompt, client)
#     sql_content = json.loads(sql_response)
#     print("SQL Content Generated:\n", sql_content)
    
#     # Execute the SQL queries and fetch the data
#     engine, session, Base = initialize_connection("CSV_DASHBOARD_DB")
#     graphTypes = ["line", "bar", "area", "scatter", "pie", "donut", "bubble", "histogram"]
#     queries = sql_content['Queries']
#     final_data = []
    
#     print('Fetching data for the queries...')
#     for index, query in enumerate(queries):
#         sql = query['sql']
#         print('SQL:', sql)
#         try:
#             result = session.execute(text(sql))
#             data = result.fetchall()
            
#             # Convert the data to a DataFrame
#             df = pd.DataFrame(data, columns=result.keys())
#             ChartOptions = {}
            
#             # Prepare ChartOptions based on the columns
#             if len(df.columns) == 1:
#                 ChartOptions['axis'] = 1
#                 ChartOptions['columns_count'] = 1
#                 ChartOptions['xAxis'] = df.columns[0]
#                 ChartOptions['yAxis'] = None
#             elif len(df.columns) == 2:
#                 ChartOptions['axis'] = 2
#                 ChartOptions['columns_count'] = len(df.columns)
#                 if isinstance(df[df.columns[0]][0], str):
#                     ChartOptions['xAxis'] = df.columns[0]
#                     ChartOptions['yAxis'] = df.columns[1]
#                 else:
#                     ChartOptions['yAxis'] = df.columns[1]
#                     ChartOptions['xAxis'] = df.columns[0]
                    
#             ChartOptions['type'] = 'bar'
#             data_records = df.to_dict(orient='records')
#             final_data.append({
#                 "kpi": query['kpi'],
#                 "data": data_records,
#                 "description": query['description'],
#                 "graphTypes": graphTypes,
#                 "ChartOptions": ChartOptions,
#                 "data_columns": df.columns.tolist(),
#                 "columns": query['columns'],
#                 "sql": query['sql'],
#             })
            
#             print(f"Index: {index}, KPI: {query['kpi']}")
#             print(df, '\n')
#         except Exception as e:
#             query['data'] = f'Error executing query: {str(e)}'
    
#     return final_data

# Function to Interact with LLM
# def llm_response(prompt, client):
#     response = client.ChatCompletion.create(
#         model="GPT35",
#         messages=[{"role": "system", "content": prompt}],
#         temperature=0
#     )
#     response_content = response.choices[0].message.content
#     return response_content

# def llm_response(prompt, client):
#     response = client.ChatCompletion.create(
#         engine=os.getenv("AZURE_DEPLOYMENT_NAME"),  # Use engine for Azure deployment
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": prompt}
#         ],
#         temperature=0,
#         max_tokens=1000  # Optional: Adjust token limit as needed
#     )
#     response_content = response["choices"][0]["message"]["content"]
#     return response_content


# # Main Execution Block
# if __name__ == "__main__":
#     # Example usage
#     formatted_columns = """Transaction_ID, Customer_ID, Name, Email, Phone, Address, City, State, Zipcode, Country, Age, Gender, Income, Customer_Segment, Date, Year, Month, Time, Total_Purchases, Amount, Total_Amount, Product_Category, Product_Brand, Product_Type, Feedback, Shipping_Method, Payment_Method, Order_Status, Ratings, Products"""
#     table_name = "Sales"
#     client = openai  # Assuming you have initialized the OpenAI client
#     generateKPIs(client, formatted_columns, table_name)

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

Constraints:
- Only use the data from the provided column names to calculate the KPIs.
- Do not assume additional data or request the contents of the CSV.
- Clearly mention the selected columns and how they are utilized.

Output format (structured as JSON):
{
    "columns": [
        {
            "column_name": "Column Name",
            "role": "Role of the column in generating KPIs"
        },
        ...
    ],
    "KPIs": [
        {
            "kpi_name": "Name of the KPI",
            "calculation": "How the KPI is calculated using the columns",
            "explanation": "Brief explanation of the business significance of the KPI"
        },
        ...
    ],
    "suggestions": [
        "Suggestions for leveraging the KPIs for business decision-making"
    ]
}
""")

# Define SQL Prompt Template
sql_prompt = Template("""
Your task is to generate SQL queries based on the provided table structure and business KPIs description.

**Table Name**: $table_name
**Table Columns:**
$formatted_columns

**Business KPIs:** $kpis

**Instructions:**
- Generate SQL queries for each provided business KPI description based on the table columns.
- Ensure all columns and table names in the query are in uppercase and wrapped in double quotes.
- Generate PostgreSQL-compatible syntax queries.
- Use the provided columns only, and ensure queries are valid with only the provided columns and datatypes.

Output format:
{
    "Queries": [
        {
            "description": "provided description",
            "kpi": "provided KPI name",
            "columns": "comma-separated columns (do not add any extra columns or text just provide the columns from the provided structure above that are needed for this KPI)",
            "sql": "sql query"
        },
        ...
    ]
}
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
            max_tokens=1000 
        )
        
        response_content = response["choices"][0]["message"]["content"].strip()
        if not response_content:
            raise ValueError("Received an empty response from the LLM.")
        
        return response_content
    except Exception as e:
        print(f"Error during LLM call: {e}")
        return ""  

# Function to Generate KPIs and SQL Queries
def generateKPIs(client, formatted_columns, table_name):
    print('Preparing KPI prompt...')
    final_kpi_prompt = kpi_prompt.substitute(formatted_columns=formatted_columns)
    print('Final KPI Prompt:\n', final_kpi_prompt)
    
    try:
        # Call LLM to generate KPIs
        kpi_response = llm_response(final_kpi_prompt, client)
        print("Raw KPI Response:\n", kpi_response)

        # Validate and parse the KPI response
        try:
            kpi_content = json.loads(kpi_response)
            print("Parsed KPI Content:\n", kpi_content)
        except json.JSONDecodeError:
            raise ValueError("The LLM response is not valid JSON. Response received: " + kpi_response)

        # Extract KPIs as a string
        str_kpis = json.dumps(kpi_content['KPIs'])  # Use json.dumps to ensure JSON format
        print('Preparing SQL prompt...')
        
        # Correctly substitute the SQL prompt template
        final_sql_prompt = sql_prompt.substitute(
            formatted_columns=formatted_columns,
            kpis=str_kpis,
            table_name=table_name
        )
        print('Final SQL Prompt:\n', final_sql_prompt)

        # Call LLM to generate SQL queries
        sql_response = llm_response(final_sql_prompt, client)
        print("Raw SQL Response:\n", sql_response)
        
        # Parse the SQL response
        sql_content = json.loads(sql_response)
        print("Parsed SQL Content:\n", sql_content)
        return sql_content['Queries']

    except KeyError as e:
        print(f"Missing placeholder in template: {e}")
    except Exception as e:
        print(f"Error occurred: {e}")
        return []

# Main Execution Block
if __name__ == "__main__":
    # Example usage
    formatted_columns = """Transaction_ID, Customer_ID, Name, Email, Phone, Address, City, State, Zipcode, Country, Age, Gender, Income, Customer_Segment, Date, Year, Month, Time, Total_Purchases, Amount, Total_Amount, Product_Category, Product_Brand, Product_Type, Feedback, Shipping_Method, Payment_Method, Order_Status, Ratings, Products"""
    table_name = "Sales"
    client = openai  # Assuming OpenAI client has been initialized
    
    # Run KPI generation and SQL query testing
    queries = generateKPIs(client, formatted_columns, table_name)
    print("\nGenerated SQL Queries:\n", queries)

