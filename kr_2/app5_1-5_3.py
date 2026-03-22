import time
import uuid
from fastapi import FastAPI, Response, Request, HTTPException
from itsdangerous import TimestampSigner, BadSignature, SignatureExpired

app = FastAPI()
SECRET_KEY = "super-secret-key" 
signer = TimestampSigner(SECRET_KEY)

USERS_DB = {"user123": {"password": "password123", "id": str(uuid.uuid4())}}

@app.post("/login")
async def login(response: Response, data: dict):
    username = data.get("username")
    password = data.get("password")

    if USERS_DB.get(username) and USERS_DB[username]["password"] == password:
        user_id = USERS_DB[username]["id"]
        current_ts = str(int(time.time()))
        
        raw_value = f"{user_id}.{current_ts}"
        signed_token = signer.sign(raw_value).decode()
        
        response.set_cookie(
            key="session_token",
            value=signed_token,
            httponly=True, 
            max_age=300
        )
        return {"message": "Login successful"}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/profile")
async def get_profile(request: Request, response: Response):
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        unsigned_data = signer.unsign(token, max_age=300).decode()
        user_id, last_ts = unsigned_data.split(".")
        
        now = int(time.time())
        diff = now - int(last_ts)

        if 3 <= diff < 5:
            new_ts = str(now)
            new_raw = f"{user_id}.{new_ts}"
            new_token = signer.sign(new_raw).decode()
            response.set_cookie(key="session_token", value=new_token, httponly=True, max_age=300)
        elif diff >= 5:
             raise HTTPException(status_code=401, detail="Session expired")

        return {"user_id": user_id, "message": "Welcome to your profile"}

    except (BadSignature, SignatureExpired, ValueError):
        raise HTTPException(status_code=401, detail="Invalid session")