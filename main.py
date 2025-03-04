from fastapi import FastAPI
from config.config import settings
# other imports
import os
import json
from fastapi import FastAPI, HTTPException, UploadFile, File
import aiofiles

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
async def output(id: int, file: UploadFile = File(...)):
    # verify file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image.")
    
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
