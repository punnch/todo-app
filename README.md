
# 📝 ToDo App API

A simple and clean ToDo application built with **FastAPI** and **PostgreSQL**.  
It allows you to manage your tasks: create, read, update, delete — all via a RESTful API.

---

## 🚀 Features

- 📋 Create, read, update, and delete tasks
- ✅ Mark tasks as done or undone
- 🧹 Delete all completed tasks
- 🗃️ PostgreSQL database integration
- 🧪 Full test coverage with `pytest` and SQLite (in-memory)
- 🛠️ Modular structure using FastAPI, SQLAlchemy, and Pydantic

---

## 📂 Project Structure

```
todo-app/
├── app/
│   ├── api/          # FastAPI endpoints
│   ├── crud/         # Database operations
│   ├── database/     # DB config and models
│   └── schemas/      # Pydantic models
├── tests/            # Automated test cases
├── .env              # Environment variables (DO NOT commit secrets!)
├── .gitignore        # Git ignore rules
├── main.py           # Entry point (Uvicorn server)
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

---

## 🔧 Installation

### 1. Clone the repo

```bash
git clone https://github.com/punnch/todo-app.git
cd todo-app
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file

```env
DB_USER=todo_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=todo_db
```

---

## ▶️ Running the App

### Start the development server:

```bash
python main.py
```

---

## ✅ Run Tests

```bash
pytest
```

---

## 📬 API Endpoints

| Method | Endpoint             | Description                    |
|--------|----------------------|--------------------------------|
| GET    | `/tasks/`            | Get all tasks                  |
| GET    | `/tasks/{id}`        | Get a task by ID               |
| POST   | `/tasks/`            | Create a new task              |
| PUT    | `/tasks/{id}/status` | Update task status             |
| PUT    | `/tasks/{id}/text`   | Update task text               |
| DELETE | `/tasks/{id}`        | Delete a task by ID            |
| DELETE | `/tasks/completed`   | Delete all completed tasks     |

---

## 💻 Author

Made with ❤️ by [punnch](https://github.com/punnch)
