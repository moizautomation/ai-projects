from fastapi import FastAPI,UploadFile, File
import pandas as pd
import sqlite3
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv 

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""
    1. Never guess or assume any values. Only use the exact numbers provided.
    2. Always return valid JSON. Nothing before it. Nothing after it. No markdown. No backticks.
    3. Always follow this exact structure:

{
  "summary": "one sentence describing the dataset using exact numbers provided",
  "issues": [
    "list only real issues based on the numbers provided"
  ],
  "recommendations": [
    "list only actionable recommendations based on the data"
  ]
}

4. If there are no issues, return an empty list for issues: []
5. If there are no duplicates, do not mention duplicates in issues.
6. Use exact numbers from the input. Never round or estimate.
    """)

conn = sqlite3.connect("database.db")

cursor = conn.cursor()

app = FastAPI()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS cleaned_uploads(
                   Id INTEGER PRIMARY KEY AUTOINCREMENT,
                   FileName TEXT,
                   Original_rows INT,
                   Cleaned_rows INT,
                   Columns TEXT
        )
    """)

def clean_dataframe(df):
    #removing duplicates
    df = df.drop_duplicates()

    for col in df.columns:
        #to get the type of the column
        if df[col].dtype == "object":
            #placing 0 in missing columns
            df[col] = df[col].fillna("Unknown")
        else:
            df[col] = df[col].fillna(0)

    #standardizing the columns name
    df.columns = df.columns.str.lower().str.replace(" ","_")

    return df

@app.get("/home")
def home():
    return {
        "message" : "Welcome back"
    }

#User uploads a csv file, it gets cleaned,saved and sent to ai for insights.
@app.post("/process-file")
async def save(file: UploadFile = File(...)):

    try:
        #if file is not uploaded
        if not file:
            return {
                "error": "No File Uploaded"
            }
        
        if not file.filename.endswith(".csv"):
            return {
                "error": "Only CSV Files are Allowed"
            }
        
        #try to read the file content
        try:
            df = pd.read_csv(file.file, encoding="latin1")
        except Exception as e:
            return {
                "error": "File could not be processed",
                "details": str(e)
            }

        before = len(df)

        #calculating no of empty cells
        missing = int(df.isna().sum().sum())

        #calculating number of dupplicates
        duplicates = int(df.duplicated().sum())

        #calculating column with the most missing values
        name = ""
        highest = 0
        for col in df.columns:
            maxx = df[col].isna().sum()

            if maxx > highest: 
                highest = maxx
                name = col

        #removing duplicates + cleaning + standardizing
        df = clean_dataframe(df)

        after = len(df)

        names = df.columns.to_list()
        
        cursor.execute("""
        INSERT INTO cleaned_uploads(Filename,Original_rows,Cleaned_rows,Columns)
        VALUES(:Filename,:Original_rows,:Cleaned_rows,:names)
        """, {
            "Filename": file.filename,
            "Original_rows": before,
            "Cleaned_rows": after,
            "names": str(names)
        })
        conn.commit()
        

        #df.shape is used then panda return a tuple (rows,columns)
        rows = df.shape[0]
        columns = df.shape[1]

        summary_data = {
            "rows": rows,
            "columns": columns,
            "missing_values": missing,
            "duplicates": duplicates,
            "worst_column": name,
            "missing_in_worst_column": highest
        }

        user_message = f"""
    Analyze this dataset:
    - Rows: {summary_data['rows']}
    - Columns: {summary_data['columns']}
    - Missing values: {summary_data['missing_values']}
    - Duplicates: {summary_data['duplicates']}
    - Worst column: {summary_data['worst_column']}
    - Missing in worst column: {summary_data['missing_in_worst_column']}
    """
        
        response = model.generate_content(user_message)

        result = json.loads(response.text)

        return {
            "ai-summary": result
        }
    except Exception as e:
        return {
            "error": "Something went wrong",
            "details": str(e)
        }

