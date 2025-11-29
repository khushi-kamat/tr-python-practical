# 📝 Task Management System
A simple Task Management API with a Python CLI tool, built using Django REST Framework.

## Features
- Create, read, update, and delete tasks
- Mark tasks as complete or incomplete
- Filtering (status, priority)
- CLI client to manage tasks from the terminal
- SQLite database with persistent storage

## Setup Instructions
- Create a Python 3.10 virtual environment
- Install dependencies: ```pip install -r requirements.txt```
- Run migrations for apps: ```python manage.py migrate```
- Runserver: ```python manage.py runserver```
- Create a `.env` file in the project root and add the following variables:<br>
  `SECRET_KEY=addsecretkey`<br>

## API Endpoint Documentation
### 1. List & Create Tasks
**Endpoint:** `/api/tasks/`  
**Methods:** `GET`, `POST`
### GET - List Tasks
- Returns all tasks (newest first)
- Supports filtering:
  - `status=true|false`
  - `priority=low|medium|high`
- Example:
  ```bash
  GET /api/tasks/?status=true&priority=high
  ```
### POST - Create Task
- Creates a new task. **`title` is required.**
- Example:
  ```bash
  POST /api/tasks/
  ```
- Request Body:
  ```json
  {
    "title": "Code Review for Feature X",
    "description": "Review pull request and provide feedback",
    "priority": "high",
    "due_date": "2025-12-30T15:00:00Z"
  }

  ```
### 2. Retrieve, Update, or Delete a Task
**Endpoint:** `/api/tasks/<id>/`  
**Methods:** `GET`, `PATCH`, `DELETE`
### GET - Retrieve Task
- Get task details
- Example
  ```bash
  GET /api/tasks/5/
  ```
### PATCH - Update Task (partial update)
- Partially update any field (title, description, priority, status, due_date)
- Example:
  ```bash
  PATCH /api/tasks/5/
  ```
- Request Body (any field):
  ```json
  {
    "priority": "medium",
    "status": false
  }
  ```
### DELETE - Delete Task
- Deletes a task and returns the deleted task data.
- Example
  ```bash
  DELETE /api/tasks/5/
  ```
- Response:
  ```json
  {
    "message": "Task deleted successfully",
    "deleted_task": {
      "id": 5,
      "title": "Code Review for Feature X",
      "description": "Review pull request and provide feedback",
      "priority": "high",
      "due_date": "2025-12-30T15:00:00Z"
    }
  }
  ```
### 3. Mark Task as Complete
**Endpoint:** `/api/tasks/<id>/complete/`  
**Method:** `POST`
- Sets task `status` to complete. Requires the task to have a `due_date`.
- Example:
  ```bash
  POST /api/tasks/5/complete/
  ```
- Response:
  ```json
  {
    "id": 5,
    "title": "Code Review for Feature X",
    "status": true,
    "priority": "high",
    "due_date": "2025-12-30T15:00:00Z"
  }
  ```
### 4. Mark Task as Incomplete
**Endpoint:** `/api/tasks/<id>/incomplete/`  
**Method:** `POST`
- Sets task `status` to incomplete.
- Example:
  ```bash
  POST /api/tasks/5/incomplete/
  ```
- Response:
  ```json
  {
    "id": 5,
    "title": "Code Review for Feature X",
    "status": false,
    "priority": "high",
    "due_date": "2025-12-30T15:00:00Z"
  }
  ```

## CLI Usage Examples
### 1. List Tasks
- List all tasks
  ```bash
  python manage.py tasks list
  ```
- List only completed tasks
  ```bash
  python manage.py tasks list --status true
  ```
- List tasks with high priority
  ```bash
  python manage.py tasks list --priority high
  ```
  **Note:** Tasks are displayed in batches of 50 (controlled by `BATCH_SIZE`).
### 2. Create a Task
- Create a new task with title, description, priority, and due date
  ```bash
  python manage.py tasks create --title "Code Review for Feature X" --description "Slides for client meeting" --priority high --due "2025-12-30 10:00"
  ```
- Create a task without description or due date
  ```bash
  python manage.py tasks create --title "Code Review for Feature X"
  ```
### 3. Update a Task
- Update title, description, or priority of a task
  ```bash
  python manage.py tasks update 3 --title "Code Review" --priority medium
  ```
- Mark task as completed
  ```bash
  python manage.py tasks update 3 --status true
  ```
- Update due date
  ```bash
  python manage.py tasks update 3 --due "2025-12-30 10:00"
  ```
### 4. Delete a Task
- Delete task by ID
  ```bash
  python manage.py tasks delete 3
  ```
### 5. Mark Task Complete / Incomplete
- Mark a task as complete
  ```bash
  python manage.py tasks complete 2
  ```
- Mark a task as incomplete
  ```bash
  python manage.py tasks incomplete 2
  ```

## Assumptions Made
1. `BATCH_SIZE` is set to 50 for CLI pagination.
2. Completed tasks must have a due date.
3. Priority of a completed task cannot be changed.
4. Date format for due dates is `"YYYY-MM-DD HH:MM"` (24-hour format).
