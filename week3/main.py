import os
from fastapi import FastAPI, Depends, Response
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from typing import List

# Load environment variables from .env
load_dotenv()

from week3.models import Task, TaskCreate, TaskUpdate
from week3.repositories import TaskRepository, InMemoryTaskRepository, PostgresTaskRepository

app = FastAPI(title="FlyRank Task Manager API - Postgres CRUD")

DATABASE_URL = os.getenv("DATABASE_URL")

# Shared in-memory repository fallback
in_memory_repo = InMemoryTaskRepository()

def get_repository() -> TaskRepository:
    """Dependency injection provider that swaps storage dynamically based on DATABASE_URL configuration."""
    if DATABASE_URL:
        return PostgresTaskRepository(DATABASE_URL)
    return in_memory_repo

@app.get("/")
def read_root():
    """Get basic API metadata and description."""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def read_health():
    """Get server health status."""
    return {
        "status": "ok"
    }

@app.get("/tasks", response_model=List[Task])
def read_tasks(repo: TaskRepository = Depends(get_repository)):
    """Retrieve the complete list of tasks."""
    return repo.get_all()

@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: int, repo: TaskRepository = Depends(get_repository)):
    """Retrieve details of a single task by ID."""
    task = repo.get_by_id(task_id)
    if task:
        return task
    return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})

@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task_data: TaskCreate, repo: TaskRepository = Depends(get_repository)):
    """Create a new task with validation."""
    if not task_data.title or task_data.title.strip() == "":
        return JSONResponse(status_code=400, content={"error": "Title is required and cannot be empty"})
    
    return repo.create(title=task_data.title)

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_data: TaskUpdate, repo: TaskRepository = Depends(get_repository)):
    """Update an existing task's title and/or done status."""
    if task_data.title is None and task_data.done is None:
        return JSONResponse(status_code=400, content={"error": "Body cannot be empty"})
    
    if task_data.title is not None and task_data.title.strip() == "":
        return JSONResponse(status_code=400, content={"error": "Title cannot be empty"})

    task = repo.update(task_id, title=task_data.title, done=task_data.done)
    if task:
        return task
    return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, repo: TaskRepository = Depends(get_repository)):
    """Remove a task from the list by ID."""
    success = repo.delete(task_id)
    if success:
        return Response(status_code=204)
    return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
