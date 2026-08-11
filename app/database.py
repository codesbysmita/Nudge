import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent.parent / "nudge.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            due_at TEXT,
            priority TEXT NOT NULL DEFAULT 'medium',
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            last_reminder_type TEXT
        )
        """
    )

    columns = connection.execute(
        "PRAGMA table_info(tasks)"
    ).fetchall()

    column_names = [column["name"] for column in columns]

    if "last_reminder_type" not in column_names:
        connection.execute(
            """
            ALTER TABLE tasks
            ADD COLUMN last_reminder_type TEXT
            """
        )

    connection.commit()
    connection.close()


def add_task(title, due_at, priority, created_at):
    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO tasks (title, due_at, priority, status, created_at)
        VALUES (?, ?, ?, 'pending', ?)
        """,
        (title, due_at, priority, created_at),
    )

    connection.commit()
    task_id = cursor.lastrowid
    connection.close()

    return task_id


def get_pending_tasks():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT id, title, due_at, priority, status, created_at
        FROM tasks
        WHERE status = 'pending'
        ORDER BY
            CASE priority
                WHEN 'high' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'low' THEN 3
                ELSE 4
            END,
            due_at IS NULL,
            due_at ASC
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


def complete_task(task_id):
    connection = get_connection()

    cursor = connection.execute(
        """
        UPDATE tasks
        SET status = 'completed'
        WHERE id = ? AND status = 'pending'
        """,
        (task_id,),
    )

    connection.commit()
    updated = cursor.rowcount > 0
    connection.close()

    return updated


def delete_task(task_id):
    connection = get_connection()

    cursor = connection.execute(
        """
        DELETE FROM tasks
        WHERE id = ?
        """,
        (task_id,),
    )

    connection.commit()
    deleted = cursor.rowcount > 0
    connection.close()

    return deleted


def get_tasks_needing_reminders():
    """
    Return pending tasks that have deadlines.
    """
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT id, title, due_at, priority, status, created_at
        FROM tasks
        WHERE status = 'pending'
          AND due_at IS NOT NULL
        ORDER BY due_at ASC
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]

def get_last_reminder_type(task_id):
    connection = get_connection()

    row = connection.execute(
        """
        SELECT last_reminder_type
        FROM tasks
        WHERE id = ?
        """,
        (task_id,),
    ).fetchone()

    connection.close()

    if row is None:
        return None

    return row["last_reminder_type"]


def set_last_reminder_type(task_id, reminder_type):
    connection = get_connection()

    connection.execute(
        """
        UPDATE tasks
        SET last_reminder_type = ?
        WHERE id = ?
        """,
        (reminder_type, task_id),
    )

    connection.commit()
    connection.close()