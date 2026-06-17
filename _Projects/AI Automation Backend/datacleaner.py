from fastapi import FastAPI,UploadFile, File
import pandas as pd
import sqlite3

conn = sqlite3.connect("database.db")

cursor = conn.cursor()

app = FastAPI()

@app.get("/home")
def home():
    return {
        "message" : "Welcome back"
    }

@app.post("/upload-file")
# tells FastAPI to expect a file in the request. The ... means it is required.
# async tell python to do other things while file is being uploaded instead of just waiting.
async def upload(file : UploadFile = File(...)):
    df = pd.read_csv(file.file, encoding="latin1")
    #orient = records will make a seperate dictionary for each row instead of a nested one.
    data = df.head().to_dict(orient="records")
    length = len(df)
    return {
        "name" : file.filename,
        "rows" : length,
        "Data" : data
    }

@app.post("/clean-file")
async def clean(file : UploadFile = File(...)):
    df = pd.read_csv(file.file, encoding="latin1")

    temp = df.head().to_dict(orient="records")
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
    
    cleaned = df.head().to_dict(orient="records")

    return {
        "normal" : temp,
        "cleaned" : cleaned
    }

@app.post("/save-clean-data")
async def save(file : UploadFile = File(...)):
    df = pd.read_csv(file.file, encoding="latin1")

    temp = df.head().to_dict(orient="records")

    before = len(df)

    #removing duplicates
    df = df.drop_duplicates()

    after = len(df)

    for col in df.columns:
        #to get the type of the column
        if df[col].dtype == "object":
            #placing 0 in missing columns
            df[col] = df[col].fillna("Unknown")
        else:
            df[col] = df[col].fillna(0)

    #standardizing the columns name
    df.columns = df.columns.str.lower().str.replace(" ","_")
    
    cleaned = df.head().to_dict(orient="records")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cleaned_uploads(
                   Id INTEGER PRIMARY KEY AUTOINCREMENT,
                   FileName TEXT,
                   Original_rows INT,
                   Cleaned_rows INT,
                   Columns TEXT
        )
    """)
    cursor.execute("""
    INSERT INTO cleaned_uploads(Filename,Original_rows,Cleaned_rows,Columns) VALUES(:Filename,:Original_rows,:Cleaned_rows,:Columns)""",{"Filename" : File.filename, "Original_rows": before, "Cleaned_rows" : after, "Columns" : df.to_dict()})
    conn.commit()