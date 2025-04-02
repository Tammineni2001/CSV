import openai
import os
import json
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from string import Template

load_dotenv()

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

kpi_prompt = Template("""
You are an expert data analyst specializing in generating business insights. I am providing you with structured data from a CSV file. Your task is to analyze this data and generate key business performance indicators (KPIs) strictly based on the columns provided.
 
Here is the CSV data:
<insert CSV data here>
 
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

sql_prompt = Template("""
Your task is to generate SQL queries based on the provided table structure and business KPIs description. The table structure includes various columns related to $table_name table, and the business KPIs describe specific metrics that need to be calculated.
**Table Name**: $table_name
**Table Columns:**
$columns
 
**Business KPIs:** $kpis
 
**Instructions:**
- Generate SQL queries for each of the provided business KPI description based on the table columns.
- The database is PostgreySQL. Generate postgresql compatible.
- The dataset name is "CSV_DASHBOARD_DB"."PUBLIC"."$table_name".
- DO NOT construct a invalid queries using the columns that are not provided in the table structure and see there datatypes as well while constructing the queries.
- use the provided columns only and all the columns should be in uppercase and wrapped in double quotes.
- Ensure all the columns and table names in the query are in uppercase and wrapped in double quotes.
    For example, the query should look like this: SELECT "COLUMN" FROM "DATABASE"."SCHEMA"."TABLE" WHERE "COLUMN" > 0.
- Generate the queries syntax which is compatible for the PostgreySQL and DO NOT generate Invalid syntax queries.
 
output structure:
{
    "Queries": [
                {
                    "description": "provided description",
                    "kpi": "provided KPI name",
                    "columns": "comma-separated columns (do not add any extra columns or text  just provide the columns from the provided structure above that are needed for this KPI)",
                    "sql":"sql query"
                },
            ...
                ]
        }
""")

def generateKPIs(client, formatted_columns, table_name):
    print('preparing kpi prompt')
    final_kpi_prompt = kpi_prompt.substitute(table_name=table_name, columns=formatted_columns)
    print('final_kpi_prompt\n', final_kpi_prompt)
    kpi_response = llm_response(final_kpi_prompt, client)
    kpi_content = json.loads(kpi_response)
    print("kpi_content generated")
 
    str_kpis = str(kpi_content['KPIs'])
 
    print('preparing sql prompt')
    final_sql_prompt = sql_prompt.substitute(columns=formatted_columns, kpis=str_kpis, table_name=table_name)
    print('final_sql_prompt\n', final_sql_prompt)
    sql_response = llm_response(final_sql_prompt, client)
 
    sql_content = json.loads(sql_response)
    print("sql_content generated\n", sql_response)
 
    # fetch the data for the sqls and return the data
    engine, session, Base = initialize_connection("CSV_DASHBOARD_DB")
    graphTypes = ["line", "bar", "area", "scatter", "pie", "donut", "bubble", "histogram"]
    queries = sql_content['Queries']
    final_data = []
    print('fetching data for the queries')
    for index, query in enumerate(queries):
        sql = query['sql']
        print('sql:', sql)
        try:
            result = session.execute(text(sql))
            data = result.fetchall()      
            # convert the data to df
            df = pd.DataFrame(data, columns=result.keys())
            # for one column
            ChartOptions = {}
            if len(df.columns) == 1:
                ChartOptions['axis'] = 1
                ChartOptions['columns_count'] = 1
                ChartOptions['xAxis'] = df.columns[0]
                ChartOptions['yAxis'] = None
            elif len(df.columns) == 2:
                ChartOptions['axis'] = 2
                ChartOptions['columns_count'] = len(df.columns)
                # check for the columns[0] type if it is string then it is yAxis
                if isinstance(df[df.columns[0]][0], str):
                    ChartOptions['xAxis'] = df.columns[0]
                    ChartOptions['yAxis'] = df.columns[1]
                else:
                    ChartOptions['yAxis'] = df.columns[1]
                    ChartOptions['xAxis'] = df.columns[0]
            ChartOptions['type'] = 'bar'
            data_records = df.to_dict(orient='records')
            final_data.append({
                "kpi": query['kpi'],
                "data": data_records,
                "description": query['description'],
                "graphTypes": graphTypes,
                "ChartOptions": ChartOptions,
                "data_columns": df.columns.tolist(),
                "columns": query['columns'],
                "sql": query['sql'],
            })
 
            print(f"Index: {index}, KPI: {query['kpi']}")
            print(df, '\n')
        except Exception as e:
            query['data'] = f'Error executing query: {str(e)}'
   
    return final_data
 
def llm_response(prompt, client):
    response = client.chat.completions.create(
        model="GPT35",
        messages=[{"role": "system", "content": prompt}],
        temperature=0,
    )
    response_content = response.choices[0].message.content
    return response_content

if __name__ == "__main__":
    # Example usage
    formatted_columns = """Transaction_ID, Customer_ID, Name, Email, Phone, Address, City, State, Zipcode, Country, Age, Gender, Income, Customer_Segment, Date, Year, Month, Time, Total_Purchases, Amount, Total_Amount, Product_Category, Product_Brand, Product_Type, Feedback, Shipping_Method, Payment_Method, Order_Status, Ratings, Products"""
    table_name = "Sales"
    client = openai  # Assuming you have initialized the OpenAI client
    generateKPIs(client, formatted_columns, table_name)

# import openai
# import os
# from dotenv import load_dotenv

# load_dotenv()

# api_key = os.getenv("AZURE_OPENAI_API_KEY")
# endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
# deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME")
# api_version = os.getenv("AZURE_OPENAI_API_VERSION")

# if not all([api_key, endpoint, deployment_name, api_version]):
#     raise ValueError("One or more environment variables are missing! Check your .env file.")


# openai.api_type = "azure"
# openai.api_key = api_key
# openai.api_base = endpoint
# openai.api_version = api_version

# def test_prompt():
#     dataset_structure = """Transaction_ID
#     Customer_ID
#     Name
#     Email
#     Phone
#     Address
#     City
#     State
#     Zipcode
#     Country
#     Age
#     Gender
#     Income
#     Customer_Segment
#     Date
#     Year
#     Month
#     Time
#     Total_Purchases
#     Amount
#     Total_Amount
#     Product_Category
#     Product_Brand
#     Product_Type
#     Feedback
#     Shipping_Method
#     Payment_Method
#     Order_Status
#     Ratings
#     Products"""
#     prompt = f"For the given dataset structure, generate business KPIs. For every object, include `kpi` and `columns` keys only.\n\nDataset structure:\n{dataset_structure}"

#     try:
        
#         response = openai.ChatCompletion.create(
#             engine=deployment_name,
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=500,
#             temperature=0.0
            
#         )
#         print("Prompt Response:")
#         print(response["choices"][0]["message"]["content"].strip())
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")

# if __name__ == "__main__":
#     test_prompt()
