from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List

app = FastAPI(title="FlyRank Task Manager API")

class Task(BaseModel):
    id: int
    title: str
    done: bool = False

# In-memory database pre-filled with 3 tasks
tasks_db: List[Task] = [
    Task(id=1, title="Buy groceries", done=False),
    Task(id=2, title="Finish homework", done=True),
    Task(id=3, title="Call friend", done=False),
]

@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def read_health():
    return {
        "status": "ok"
    }

@app.get("/tasks", response_model=List[Task])
def read_tasks():
    return tasks_db

@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: int):
    for task in tasks_db:
        if task.id == task_id:
            return task
    return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
