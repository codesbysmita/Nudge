import json
import os
import time
import threading
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from app.database import (
    add_task,
    get_pending_tasks,
    complete_task,
    delete_task,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


FEATHERLESS_BASE_URL = "https://api.featherless.ai/v1"
FEATHERLESS_MODEL = "MiniMaxAI/MiniMax-M2.5"


SYSTEM_PROMPT = """
You are Nudge, a personal deadline and task assistant.

Your job is to understand what the user wants and classify the message
into exactly one of these actions:

ADD_TASK
LIST_TASKS
COMPLETE_TASK
DELETE_TASK
CHAT

Return ONLY valid JSON. Never use markdown. Never add explanations
outside the JSON.

For ADD_TASK, return:
{
  "action": "ADD_TASK",
  "title": "short task title",
  "due_at": "YYYY-MM-DD HH:MM or null",
  "priority": "low",
  "message": "short confirmation"
}

For LIST_TASKS, return:
{
  "action": "LIST_TASKS"
}

For COMPLETE_TASK, return:
{
  "action": "COMPLETE_TASK",
  "task_id": 1
}

For DELETE_TASK, return:
{
  "action": "DELETE_TASK",
  "task_id": 1
}

For CHAT, return:
{
  "action": "CHAT",
  "message": "your helpful response"
}

Priority must be exactly one of:
low
medium
high

Use the current date and time provided by the application when
interpreting relative dates such as today, tomorrow, or Friday.

If the user has not provided enough information to create a task,
use CHAT and ask a concise clarification question.

Current date and time:
"""


def create_featherless_client():
    api_key = os.environ.get("FEATHERLESS_API_KEY")

    if not api_key:
        raise RuntimeError(
            "FEATHERLESS_API_KEY is missing from the environment."
        )

    return OpenAI(
        api_key=api_key,
        base_url=FEATHERLESS_BASE_URL,
    )


featherless = create_featherless_client()
ai_lock = threading.Lock()


def understand_message(user_text):
    current_time = datetime.now().astimezone().strftime(
        "%Y-%m-%d %H:%M:%S %Z"
    )

    system_message = SYSTEM_PROMPT + current_time

    with ai_lock:
        response = None

        for attempt in range(3):
            try:
                response = featherless.chat.completions.create(
                    model=FEATHERLESS_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": system_message,
                        },
                        {
                            "role": "user",
                            "content": user_text,
                        },
                    ],
                    temperature=0,
                )
                break

            except Exception as error:
                error_text = str(error)

                if (
                    "429" not in error_text
                    and "concurrency" not in error_text.lower()
                ):
                    raise

                if attempt == 2:
                    raise

                wait_seconds = 3 * (attempt + 1)

                print(
                    f"Featherless is busy. "
                    f"Retrying in {wait_seconds} seconds..."
                )

                time.sleep(wait_seconds)

    if response is None:
        raise RuntimeError("The AI request did not return a response.")

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("The AI returned an empty response.")

    content = content.strip()

    if content.startswith("```"):
        content = content.replace("```json", "", 1)
        content = content.replace("```", "", 1)
        content = content.strip()

    return json.loads(content)

def execute_action(result):
    action = result.get("action")

    if action == "ADD_TASK":
        title = result.get("title")
        due_at = result.get("due_at")
        priority = result.get("priority", "medium")

        if not title:
            return "I couldn't determine what task you want me to add."

        task_id = add_task(
            title=title,
            due_at=due_at,
            priority=priority,
            created_at=datetime.now().astimezone().isoformat(),
        )

        return (
            f"Added task #{task_id}: {title}"
            + (f" — due {due_at}" if due_at else "")
            + f" — priority {priority}."
        )

    if action == "LIST_TASKS":
        tasks = get_pending_tasks()

        if not tasks:
            return "You don't have any pending tasks. You're all caught up! 🎉"

        lines = ["Here are your pending tasks:"]

        for task in tasks:
            due = task["due_at"] or "No deadline"
            lines.append(
                f"#{task['id']} — {task['title']} "
                f"| due: {due} | priority: {task['priority']}"
            )

        return "\n".join(lines)

    if action == "COMPLETE_TASK":
        task_id = result.get("task_id")

        if not task_id:
            return "Which task number should I mark as complete?"

        if complete_task(task_id):
            return f"Task #{task_id} marked as complete. ✅"

        return f"I couldn't find a pending task with ID #{task_id}."

    if action == "DELETE_TASK":
        task_id = result.get("task_id")

        if not task_id:
            return "Which task number should I delete?"

        if delete_task(task_id):
            return f"Task #{task_id} deleted. 🗑️"

        return f"I couldn't find a task with ID #{task_id}."

    if action == "CHAT":
        return result.get(
            "message",
            "I'm here to help you manage your deadlines and tasks.",
        )

    return "I didn't understand that request."