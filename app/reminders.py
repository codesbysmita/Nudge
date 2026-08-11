from datetime import datetime, timedelta

from app.database import (
    get_tasks_needing_reminders,
    get_last_reminder_type,
    set_last_reminder_type,
)


def get_due_reminders():
    """
    Find pending tasks that are approaching or have passed their deadlines.

    Each reminder type is returned only once per task:
    - 24_hour
    - 3_hour
    - overdue
    """

    tasks = get_tasks_needing_reminders()

    now = datetime.now().astimezone()
    reminders = []

    for task in tasks:
        due_at = task.get("due_at")

        if not due_at:
            continue

        try:
            due_time = datetime.fromisoformat(due_at)

            if due_time.tzinfo is None:
                due_time = due_time.replace(tzinfo=now.tzinfo)

        except ValueError:
            continue

        time_remaining = due_time - now

        if time_remaining.total_seconds() < 0:
            reminder_type = "overdue"

        elif time_remaining <= timedelta(hours=3):
            reminder_type = "3_hour"

        elif time_remaining <= timedelta(hours=24):
            reminder_type = "24_hour"

        else:
            continue

        last_reminder = get_last_reminder_type(task["id"])

        if last_reminder == reminder_type:
            continue

        reminders.append(
            {
                "task_id": task["id"],
                "title": task["title"],
                "due_at": task["due_at"],
                "priority": task["priority"],
                "reminder_type": reminder_type,
            }
        )

    return reminders


def mark_reminder_sent(task_id, reminder_type):
    set_last_reminder_type(task_id, reminder_type)