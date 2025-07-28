from sqlalchemy.orm import Session
from sqlalchemy import desc # for ordering created_at

from app.database.database import Task 
from app.schemas.schemas import TaskCreate, TaskUpdateText

def get_tasks(db: Session, skip: int = 0, limit: int = 10):
    # .all() -> executes the querry and returns all results 
    # offset(skip) and .limit(limit) -> are for pagination
    return db.query(Task).order_by(desc(Task.created_at)).offset(skip).limit(limit).all()

def get_task(db: Session, task_id: int):
    # .first() -> executes the querry, returns the first matching result / None
    return db.query(Task).filter(Task.id == task_id).first()

def create_task(db: Session, task: TaskCreate):
    db_task = Task(text=task.text)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task

def delete_task(db: Session, task_id: int):
    db_task = get_task(db, task_id)

    if db_task:
        db.delete(db_task)
        # Commit the transaction to apply the deletion to the database
        db.commit()
    return db_task

def delete_completed_tasks(db: Session):
    tasks_to_delete = db.query(Task).filter(Task.done == True).all()
    deleted_count = 0

    for task in tasks_to_delete:
        db.delete(task)
        deleted_count += 1
    # Commit the transaction to apply all deletions
    db.commit()
    return deleted_count

def update_task_status(db: Session, task_id: int, done: bool):
    db_task = get_task(db, task_id)

    if db_task:
        db_task.done = done
        db.commit()
        # Refresh the object to ensure it has the latest state from the db
        db.refresh(db_task)
    return db_task

def update_task_text(db: Session, task_id: int, new_text: str):
    db_task = get_task(db, task_id)

    if db_task:
        db_task.text = new_text
        db.commit()
        db.refresh(db_task)
    return db_task