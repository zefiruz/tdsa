import re
from fastapi import FastAPI, Header, HTTPException
from typing import Optional

app = FastAPI()

LANGUAGE_PATTERN = r"^[a-zA-Z\-]+(,[a-zA-Z\-]+(;q=\d+\.\d+)?)*$"

@app.get("/headers")
async def get_headers(
    user_agent: Optional[str] = Header(None, alias="User-Agent"),
    accept_language: Optional[str] = Header(None, alias="Accept-Language")
):
    if not user_agent or not accept_language:
        raise HTTPException(
            status_code=400, 
            detail="Missing required headers: User-Agent or Accept-Language"
        )

    clean_lang = accept_language.replace(" ", "")
    if not re.match(LANGUAGE_PATTERN, clean_lang):
        raise HTTPException(
            status_code=400, 
            detail="Invalid Accept-Language format"
        )

    return {
        "User-Agent": user_agent,
        "Accept-Language": accept_language
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)