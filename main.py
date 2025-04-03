from fastapi import FastAPI
from config.config import settings
# other imports
import os
import json
from fastapi import FastAPI, HTTPException, UploadFile, Query
import aiofiles
import subprocess
import requests
from PIL import Image

app = FastAPI(title=settings.app_name)

@app.get("/")
def read_root():
    return {"Message": "Hello World. This message indicates that this server is up and running.",
            "Display name": settings.display_name,
            "Model name": settings.model_name,
            "Server version": settings.server_version,
            "API version": settings.api_version}

DATA_DIR = 'test_data'

@app.post("/evaluate/mock/{id}")
async def output(id: int, url: str = Query(...)):
    # Verify that the url is received
    print("Received URL:", url)
    
    # get filename
    filename = os.path.join(DATA_DIR, f"{id}.json")
    # Check if the JSON file exists; if not, raise a 404 error.
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="JSON file not found")

    # read json data
    async with aiofiles.open(filename, mode='r') as f:
        contents = await f.read()
        data = json.loads(contents)
    
    return data

@app.post("/evaluate/azure")
async def evaluate(url: str):
    # Create a temporary file
    temp_filename = 'temp.jpg'

    # Download the image
    def download_image():
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download image")
        with open(temp_filename, "wb") as f:
            f.write(response.content)

    try:
        download_image()
    except Exception as e:
        os.remove(temp_filename)
        raise HTTPException(status_code=400, detail=str(e))

    # Verify that the downloaded file is a valid image
    try:
        with Image.open(temp_filename) as img:
            img.verify()
    except Exception:
        os.remove(temp_filename)
        raise HTTPException(status_code=400, detail="Downloaded file is not a valid image")

    # Downloaded file path
    print("Downloaded image path:", temp_filename)

    # Invoke azure file from spark-symbiota-ml
    command = [
        settings.python_path,       # e.g. "python"
        settings.azure_file_path,   # path to your Azure script
        temp_filename               # your temp file
    ]

    # Run the command, capturing stdout and stderr
    azure_result = subprocess.run(command, capture_output=True, text=True)

    # Clean up by deleting the temporary file
    os.remove(temp_filename)

    return azure_result.stdout