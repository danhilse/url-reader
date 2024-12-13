from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

app = FastAPI()

class UrlInput(BaseModel):
    url: HttpUrl

@app.post("/convert")
async def convert_url(input: UrlInput):
    # TODO: Implement URL processing
    return {"status": "processing"}
