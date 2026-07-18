from abc import ABC, abstractmethod
from typing import List, Optional
import psycopg
from psycopg.rows import dict_row
from week3.models import Task

class TaskRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Task]:
        pass

    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional[Task]:
        pass

    @abstractmethod
    def create(self, title: str) -> Task:
        pass

    @abstractmethod
    def update(self, task_id: int, title: Optional[str], done: Optional[bool]) -> Optional[Task]:
        pass

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        pass


class InMemoryTaskRepository(TaskRepository):
    def __init__(self):
        self.tasks: List[Task] = [
            Task(id=1, title="Buy groceries", done=False),
            Task(id=2, title="Finish homework", done=True),
            Task(id=3, title="Call friend", done=False),
        ]

    def get_all(self) -> List[Task]:
        return self.tasks

    def get_by_id(self, task_id: int) -> Optional[Task]:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def create(self, title: str) -> Task:
        next_id = max([t.id for t in self.tasks]) + 1 if self.tasks else 1
        new_task = Task(id=next_id, title=title, done=False)
        self.tasks.append(new_task)
        return new_task

    def update(self, task_id: int, title: Optional[str], done: Optional[bool]) -> Optional[Task]:
        for task in self.tasks:
            if task.id == task_id:
                if title is not None:
                    task.title = title
                if done is not None:
                    task.done = done
                return task
        return None

    def delete(self, task_id: int) -> bool:
        for index, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks.pop(index)
                return True
        return False


class PostgresTaskRepository(TaskRepository):
    def __init__(self, conn_str: str):
        self.conn_str = conn_str

    def _get_connection(self):
        return psycopg.connect(self.conn_str, row_factory=dict_row)

    def get_all(self) -> List[Task]:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, title, done FROM tasks ORDER BY id")
                rows = cur.fetchall()
                return [Task(**row) for row in rows]

    def get_by_id(self, task_id: int) -> Optional[Task]:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
                row = cur.fetchone()
                if row:
                    return Task(**row)
        return None

    def create(self, title: str) -> Task:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done",
                    (title, False)
                )
                row = cur.fetchone()
                conn.commit()
                return Task(**row)

    def update(self, task_id: int, title: Optional[str], done: Optional[bool]) -> Optional[Task]:
        fields = []
        params = []
        if title is not None:
            fields.append("title = %s")
            params.append(title)
        if done is not None:
            fields.append("done = %s")
            params.append(done)
            
        if not fields:
            return self.get_by_id(task_id)
            
        params.append(task_id)
        query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = %s RETURNING id, title, done"
        
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, tuple(params))
                row = cur.fetchone()
                conn.commit()
                if row:
                    return Task(**row)
        return None

    def delete(self, task_id: int) -> bool:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM tasks WHERE id = %s RETURNING id", (task_id,))
                row = cur.fetchone()
                conn.commit()
                return row is not None
