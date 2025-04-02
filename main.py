import openai
from langchain.prompts import PromptTemplate
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME")

if not all([api_key, endpoint, api_version, deployment_name]):
    raise ValueError("One or more environment variables are missing! Check your .env file.")

openai.api_type = "azure"
openai.api_key = api_key
openai.api_base = endpoint
openai.api_version = api_version

prompt_template = PromptTemplate(
    input_variables=["dataset_structure"],
    template=("""For the given dataset structure, generate business KPIs. 
    For every object, include `kpi` and `columns` keys only.

    Dataset structure:
    {dataset_structure}""")
)

def generate_kpis(file_path):
    try:
        if not os.path.exists(file_path):
            return {"error": f"File not found at {file_path}"}

        df = pd.read_excel(file_path)
        dataset_structure = "\n".join(df.columns)

        formatted_prompt = prompt_template.format(dataset_structure=dataset_structure)

        response = openai.ChatCompletion.create(
            engine=deployment_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": formatted_prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        result = response["choices"][0]["message"]["content"]
        print("Response with Newlines:")
        print(result)
        result = result.replace("\\n", "\n")
        return {"response": result}

    except FileNotFoundError:
        return {"error": f"The file at {file_path} does not exist or is inaccessible."}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

if __name__ == "__main__":
    file_path = "C:\\Users\\TA115023\\Desktop\\Data\\Book23.xls"
    result = generate_kpis(file_path)
    if "error" in result:
        print(result["error"])
    else:
        print("Processed Response:")
        print(result["response"])
