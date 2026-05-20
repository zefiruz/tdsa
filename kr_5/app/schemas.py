from pydantic import BaseModel, Field
from typing import Optional, Literal

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=80)
    description: Optional[str] = None
    status: Literal["todo", "in_progress", "done"]
    priority: int = Field(..., ge=1, le=5)

class TaskUpdateStatus(BaseModel):
    status: Literal["todo", "in_progress", "done"]

class TaskResponse(TaskCreate):
    id: int
    owner_id: int