from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from app.schemas import TaskCreate, TaskResponse, TaskUpdateStatus
from app.dependencies import get_current_user, get_storage
from app.storage import Storage

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate, user: dict = Depends(get_current_user), db: Storage = Depends(get_storage)):
    task_id = db.task_counter
    db.task_counter += 1
    new_task = task.model_dump()
    new_task["id"] = task_id
    new_task["owner_id"] = user["id"]
    db.tasks[task_id] = new_task
    return new_task

@router.get("", response_model=List[TaskResponse])
def get_tasks(
    status: Optional[str] = None, 
    min_priority: Optional[int] = None, 
    user: dict = Depends(get_current_user), 
    db: Storage = Depends(get_storage)
):
    result = [
        t for t in db.tasks.values() 
        if t["owner_id"] == user["id"] 
        and (status is None or t["status"] == status)
        and (min_priority is None or t["priority"] >= min_priority)
    ]
    return result

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, user: dict = Depends(get_current_user), db: Storage = Depends(get_storage)):
    task = db.tasks.get(task_id)
    if not task or task["owner_id"] != user["id"]:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(task_id: int, update_data: TaskUpdateStatus, user: dict = Depends(get_current_user), db: Storage = Depends(get_storage)):
    task = db.tasks.get(task_id)
    if not task or task["owner_id"] != user["id"]:
        raise HTTPException(status_code=404, detail="Task not found")
    db.tasks[task_id]["status"] = update_data.status
    return db.tasks[task_id]

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, user: dict = Depends(get_current_user), db: Storage = Depends(get_storage)):
    task = db.tasks.get(task_id)
    if not task or task["owner_id"] != user["id"]:
        raise HTTPException(status_code=404, detail="Task not found")
    del db.tasks[task_id]
    return None