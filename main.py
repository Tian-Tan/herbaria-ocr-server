from fastapi import FastAPI
from config.config import settings
# other imports
import os
import json
from fastapi import FastAPI, HTTPException, Query
import aiofiles
import httpx

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
async def evaluate(url: str = Query(...)):
    target_url = f"{settings.azure_route}?url={url}"
    print("Target url:", target_url)
    # Ascync calls ocr service
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(target_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling OCR service: {str(e)}")
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="OCR service returned an error")
    
    return response.json()