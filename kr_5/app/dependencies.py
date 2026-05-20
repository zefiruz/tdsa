from fastapi import Header, HTTPException, Depends
from app.storage import db, Storage

def get_storage() -> Storage:
    return db

def get_current_user(
    x_user_id: str = Header(default=None, alias="X-User-Id"), 
    x_user_role: str = Header(default="user", alias="X-User-Role")
):
    if not x_user_id or not x_user_id.isdigit():
        raise HTTPException(status_code=401, detail="Invalid or missing X-User-Id header")
    return {
        "id": int(x_user_id),
        "role": x_user_role
    }

def require_admin(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not enough privileges")
    return user