from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import os

from app.database.database import (
    create_db_tables,  
    SessionLocal
)
from app.schemas.schemas import (
    TaskCreate, 
    TaskUpdateText, 
    TaskResponse, 
    TaskMessage
)
from app.crud import crud

app = FastAPI (
    title="ToDo App Api",
    description="A simple ToDo application API built with FastAPI and PostgreSQL.",
    version="1.0.0"
)

# -- Database Dependency --
# This function will create a new db session for each request
# and ensure that it is closed after the request is finished
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Startup Event Handler ---
# This decorator ensures that the create_db_tables() function is called
# when the FastAPI application starts up. This will create all defined
# tables in the database if they don't already exist.
@app.on_event("startup")
async def startup_event():
    if os.getenv("ENV") != "test":
        print("Starting up application...")
        create_db_tables()
        print("Database tables checked/created!")

# -- Api Endponts --

# Endpont to get all tasks
@app.get(
    "/tasks/", 
    response_model=List[TaskResponse], 
    summary="Get all tasks"
)
def read_tasks(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks

# Endpoint to delete completed tasks (done)
@app.delete(
    "/tasks/completed",
    response_model=TaskMessage,
    summary="Delete the 'done = True' tasks"
)
def delete_completed_tasks_endpoint(db: Session = Depends(get_db)):
    removed_count = crud.delete_completed_tasks(db)
    return {"message": f"Removed {removed_count} completed tasks."}

# Endpont to get a task by ID
@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse, 
    summary="Get a single task by ID"
)
def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id=task_id)

    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Task not found"
        )
    return db_task

# Endpont to create a task
@app.post(
    "/tasks/", 
    response_model=TaskResponse, 
    status_code=status.HTTP_201_CREATED, 
    summary="Create a task"
)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, task=task) 

# Endpoint to update task status (done/undone)
@app.put(
    "/tasks/{task_id}/status", 
    response_model=TaskResponse,
    summary="Update a task status by ID (done/undone)"
)
def update_task_status_endpoint(
    task_id: int, 
    done: bool, 
    db: Session = Depends(get_db)
):
    db_task = crud.update_task_status(db, task_id=task_id, done=done)

    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Task not found"
        )
    return db_task

# Endpoint to update task text
@app.put(
    "/tasks/{task_id}/text",
    response_model=TaskResponse,
    summary="Update a task text by ID"
)
def update_task_text_endpoint(
    task_id: int, 
    task_update: TaskUpdateText,
    db: Session = Depends(get_db)
):
    db_task = crud.update_task_text(
        db, 
        task_id=task_id, 
        new_text=task_update.text
    )

    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Task not found"
        )
    return db_task

# Endpoint to delete task
@app.delete(
    "/tasks/{task_id}", 
    response_model=TaskMessage, 
    summary="Delete a task by ID"
    )
def delete_single_task_endpoint(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.delete_task(db, task_id=task_id)

    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Task not found"
        )
    return {"message": f"Task with ID {task_id} removed successfully."}