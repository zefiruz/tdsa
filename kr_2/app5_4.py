from fastapi import FastAPI, Header, HTTPException
from typing import Optional

app = FastAPI()

@app.get("/headers")
async def get_headers(
    user_agent: Optional[str] = Header(None),
    accept_language: Optional[str] = Header(None)
):
    if not user_agent or not accept_language:
        raise HTTPException(status_code=400, detail="Missing required headers")
    
    return {
        "User-Agent": user_agent,
        "Accept-Language": accept_language
    }