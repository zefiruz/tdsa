from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import require_admin, get_storage
from app.storage import Storage

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/stats")
def get_stats(user: dict = Depends(require_admin), db: Storage = Depends(get_storage)):
    stats = {
        "total_tasks": len(db.tasks),
        "by_status": {"todo": 0, "in_progress": 0, "done": 0}
    }
    for t in db.tasks.values():
        stats["by_status"][t["status"]] += 1
    return stats

@router.delete("/tasks/{task_id}", status_code=204)
def admin_delete_task(task_id: int, user: dict = Depends(require_admin), db: Storage = Depends(get_storage)):
    if task_id not in db.tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del db.tasks[task_id]
    return None