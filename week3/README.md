# Week 3 - PostgreSQL CRUD API with Docker Compose

This folder contains the Week 3 project: a Postgres-backed FastAPI CRUD service running inside Docker Compose.

## 🏗️ Clean Architecture & Swapping Strategy

The application is structured to decouple the web routes from the storage layer using the **Repository Pattern**:

1. **`repositories.py`**:
   - Defines a `TaskRepository` interface class detailing all database methods.
   - Implements `InMemoryTaskRepository` (using a Python list fallback).
   - Implements `PostgresTaskRepository` (using SQL queries via `psycopg`).

2. **`main.py`**:
   - Uses FastAPI's dependency injection (`Depends`) to resolve the active repository.
   - Dynamically swaps between storage classes depending on whether a `DATABASE_URL` is set in the environment:
     ```python
     def get_repository() -> TaskRepository:
         if DATABASE_URL:
             return PostgresTaskRepository(DATABASE_URL)
         return in_memory_repo
     ```

This approach allows swapping database backends in **one single line of code** while keeping all routes, request handlers, and business logic completely unchanged.

---

## 🛠️ Getting Started (Docker Compose)

The easiest way to start both the PostgreSQL database and the API service is with Docker Compose.

### 1. Configure the Environment
Copy the example environment template file:
```bash
cp .env.example .env
```
Ensure the `.env` contains the correct connection string:
```env
DATABASE_URL=postgresql://postgres:password@db:5432/taskdb
```

### 2. Start the Stack
Run the following command to build the image and run the database and web app together:
```bash
docker compose up --build
```
*Note: Make sure Docker Desktop is running on your machine.*

PostgreSQL will automatically run the schema defined in `init.sql` on startup to create the `tasks` table.

---

## 🧪 Proof of Data Persistence

To prove that the data persists across container restarts and shutdowns:

1. **Start the stack**:
   ```bash
   docker compose up -d
   ```
2. **Create a task**:
   Use Swagger UI at `http://localhost:8000/docs` to send a `POST /tasks` request:
   ```json
   {
     "title": "Test Persistence"
   }
   ```
3. **Verify the task exists**:
   Send a `GET /tasks` request and verify that the task has been saved in the PostgreSQL database.
4. **Shutdown the stack**:
   Stop and remove the running containers:
   ```bash
   docker compose down
   ```
5. **Restart the stack**:
   Start the containers again:
   ```bash
   docker compose up -d
   ```
6. **Verify the task still exists**:
   Send a `GET /tasks` request again. The task "Test Persistence" is still returned!

**Why it works:**
The Postgres service in `docker-compose.yml` mounts a named Docker volume (`postgres_data_week3`) to `/var/lib/postgresql/data`. This mounts the raw SQL files to your host storage, ensuring data survives even when the database container is destroyed.
