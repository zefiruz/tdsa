from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

app = FastAPI()

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = Field(None, gt=0)
    is_subscribed: Optional[bool] = False

@app.post("/create_user")
async def create_user(user: UserCreate):
    return user

#http://127.0.0.1:8000/docs