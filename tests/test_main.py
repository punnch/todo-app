from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool 
from sqlalchemy.orm import sessionmaker

from app.api.api import app, get_db
# Use static pool for tests to prevent multiple connections
from app.database.database import (
    SessionLocal, 
    Base,   
    Task
)

# -- Pytest fixture for robust db isolation -- 

@pytest.fixture(name="client")
def setup_test_db_and_client(monkeypatch):
    """
    Fixture to set up a clean database before each test.
    It creates a new engine and session factory, drops/creates tables
    and overrides the app's get_db dependency for the duration of the test.
    """
    # Create a new in-memory SQLite database engine for each test
    # The ':memory:' string tells SQLite to create a temporary database in RAM.
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    # Create a new SessionLocal for this special test_engine
    TestSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=test_engine
    )
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    monkeypatch.setattr("app.database.database.SessionLocal", TestSessionLocal)
    monkeypatch.setattr("app.database.database.engine", test_engine)

    monkeypatch.setenv("ENV", "test")

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Yield the TestClient, which will now use the overriden dependency
    with TestClient(app) as client:
        yield client  

    # Close the test engine conntection (importan for in-memory databases)
    test_engine.dispose()
    app.dependency_overrides.clear()

# -- Test functions --
# Note: All test functions now accept 'client' as an argument,
# because the fixture now yields the TestClient.    

# Test creating a new task
def test_create_task(client: TestClient):
    response = client.post("/tasks/", json={"text": "created test task"})
    # assert that the status code of task is 201 (created)
    assert response.status_code == 201
    # json() -> converts the JSON string into a Python dictionary
    data = response.json()
    assert data["text"] == "created test task"
    assert data["done"] is False
    assert "id" in data
    assert "created_at" in data

# Test getting all tasks
def test_read_tasks(client: TestClient):
    # create a test task to read it later
    client.post("/tasks/", json={"text": "another created test task"})

    response = client.get("/tasks/")
    # 200 (OK)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(task["text"] == "another created test task" for task in data)

# Test getting a single task by id
def test_read_single_task(client: TestClient):
    # create a task to get an id
    create_response = client.post(
        "/tasks/", 
        json={"text": "test text"}
    ) 
    task_id = create_response.json()["id"]

    # try to retrieve a task
    respone = client.get(f"/tasks/{task_id}")
    assert respone.status_code == 200
    data = respone.json()
    assert data["id"] == task_id 
    assert data["text"] == "test text"

    # test for a non-existent task
    not_found_response = client.get("/tasks/99999")
    assert not_found_response.status_code == 404
    assert "Task not found" in not_found_response.json()["detail"]

# Test updating a task status by id
def test_update_task_status(client: TestClient):
    create_response = client.post(
        "/tasks/",
        json={"text": "test task to update"}
    )
    task_id = create_response.json()["id"]

    # switch to True status
    update_response = client.put(
        f"/tasks/{task_id}/status", 
        params={"done": True}
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["done"] is True
    assert data["id"] == task_id

    # check if status is actually updated in database to True
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.json()["done"] is True

    # switch to False status
    update_response = client.put(
        f"/tasks/{task_id}/status", 
        params={"done": False}
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["done"] is False
    assert data["id"] == task_id

    # check if status is actually updated in database to False
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.json()["done"] is False

# Test updating a task text by id
def test_update_task_text(client: TestClient):
    create_response = client.post(
        "/tasks/",
        json={"text": "original text"}
    )
    task_id = create_response.json()["id"]

    update_response = client.put(
        f"/tasks/{task_id}/text",
        json={"text": "updated text"}
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["id"] == task_id
    assert data["text"] == "updated text"

    # check if text is actually updated in database
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.json()["text"] == "updated text"

# Test deleting a task by id
def test_delete_task(client: TestClient):
    create_response = client.post(
        "/tasks/",
        json={"text": "task to delete"}
    )
    task_id = create_response.json()["id"]

    # delete a task
    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": f"Task with ID {task_id} removed successfully."}

    # check if task is actually deleted in database
    not_found_response = client.get(f"/tasks/{task_id}")
    assert not_found_response.status_code == 404
    assert "Task not found" in not_found_response.json()["detail"]

# Test deleting all completed task (true)
def test_delete_completed_tasks(client: TestClient):
    # task 1 (not done)
    client.post("/tasks/", json={"text": "task 1 (not done, should remain)"})

    # task 2 (done)
    task_id_2 = client.post(
        "/tasks/", 
        json={"text": "task 2 (should be deleted)"}
    ).json()["id"]
    client.put(f"/tasks/{task_id_2}/status", params={"done": True})
    
    # task 3 (not done)
    client.post("/tasks/", json={"text": "task 3 (not done, should remain)"})

    # task 4 (done)
    task_id_4 = client.post(
        "/tasks/", 
        json={"text": "task 4 (should be deleted)"}
    ).json()["id"]
    client.put(f"/tasks/{task_id_4}/status", params={"done": True}) 

    # delete completed tasks
    delete_response = client.delete("/tasks/completed")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Removed 2 completed tasks."}

    # verify that only incomplete tasks remain
    get_all_response = client.get("/tasks/")
    assert get_all_response.status_code == 200
    remaining_tasks = get_all_response.json()
    # Task 1 and task 3 should remain
    assert len(remaining_tasks) == 2

    # verify the text of the remain tasks
    remaining_texts = {task["text"] for task in remaining_tasks} # set
    assert "task 1 (not done, should remain)" in remaining_texts
    assert "task 3 (not done, should remain)" in remaining_texts
    # verify that complete tasks're deleted
    assert "task 2 (should be deleted)" not in remaining_texts
    assert "task 4 (should be deleted)" not in remaining_texts
    
    print([task["text"] for task in remaining_tasks])