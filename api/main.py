from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from openai import OpenAI
import os
import zipfile
import pandas as pd
import tempfile
from dotenv import load_dotenv
from mangum import Mangum

load_dotenv()

app = FastAPI()

##adding vercel handler 

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI on Vercel!"}

handler = Mangum(app)
async def process_question(...):

# Load proxy token and proxy base URL
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
AIPROXY_BASE_URL = "https://aiproxy.sanand.workers.dev/openai/v1"

if not AIPROXY_TOKEN:
    raise RuntimeError("AIPROXY_TOKEN not found in environment variables.")

# Initialize OpenAI client with proxy
client = OpenAI(
    api_key=AIPROXY_TOKEN,
    base_url=AIPROXY_BASE_URL
)

@app.post("/")
async def process_question(
    question: str = Form(...),
    file: UploadFile = File(None)
):
    # If a file is uploaded, process it
    if file:
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = os.path.join(tmp_dir, file.filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())

            # If it's a zip file, extract it
            if file.filename.endswith('.zip'):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(tmp_dir)

                # Search for CSV inside extracted files
                for root, _, files in os.walk(tmp_dir):
                    for csv_file in files:
                        if csv_file.endswith('.csv'):
                            csv_path = os.path.join(root, csv_file)
                            try:
                                df = pd.read_csv(csv_path)
                                if 'answer' in df.columns:
                                    answer = df['answer'].iloc[0]
                                    return JSONResponse(content={"answer": str(answer)})
                            except Exception as e:
                                return JSONResponse(
                                    content={"error": f"Failed to read CSV: {str(e)}"},
                                    status_code=400
                                )

    # If no valid CSV found or no file uploaded, fallback to OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": question}],
            temperature=0.3,
            max_tokens=500
        )
        answer = response.choices[0].message.content.strip()
        return JSONResponse(content={"answer": answer})
    except Exception as e:
        return JSONResponse(
            content={"error": f"OpenAI API failed: {str(e)}"},
            status_code=500
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)