import re
from datetime import datetime
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, field_validator

app = FastAPI()

LANGUAGE_PATTERN = r"^[a-zA-Z\-]+(,[a-zA-Z\-]+(;q=\d+\.\d+)?)*$"


class CommonHeaders(BaseModel):
    user_agent: str = Header(..., alias="User-Agent")
    accept_language: str = Header(..., alias="Accept-Language")

    @field_validator("accept_language")
    @classmethod
    def validate_accept_language(cls, value: str) -> str:
        clean_lang = value.replace(" ", "")
        if not re.match(LANGUAGE_PATTERN, clean_lang):
            raise ValueError(
                f"Invalid Accept-Language format: '{value}'. "
                f"Expected pattern like: 'en-US,en;q=0.9,es;q=0.8'"
            )
        return value


@app.get("/headers")
async def get_headers(headers: CommonHeaders = Header()):
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language,
    }


@app.get("/info")
async def get_info(headers: CommonHeaders = Header()):
    from fastapi.responses import JSONResponse

    server_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    return JSONResponse(
        content={
            "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
            "headers": {
                "User-Agent": headers.user_agent,
                "Accept-Language": headers.accept_language,
            },
        },
        headers={"X-Server-Time": server_time},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
