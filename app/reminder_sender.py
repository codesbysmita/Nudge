import os

from dotenv import load_dotenv
from caspian_sdk import CommClient

from app.reminders import get_due_reminders, mark_reminder_sent


load_dotenv(".env")


def create_caspian_client():
    api_key = os.environ.get("CASPIAN_API_KEY")
    base_url = os.environ.get("CASPIAN_BASE_URL")

    if not api_key:
        raise RuntimeError(
            "CASPIAN_API_KEY is missing from the environment."
        )

    if not base_url:
        raise RuntimeError(
            "CASPIAN_BASE_URL is missing from the environment."
        )

    return CommClient(
        api_key=api_key,
        base_url=base_url,
    )


def build_reminder_message(reminder):
    title = reminder["title"]
    due_at = reminder["due_at"]
    priority = reminder["priority"]
    reminder_type = reminder["reminder_type"]

    if reminder_type == "24_hour":
        return (
            "Hey! Just a heads-up!\n\n"
            f"Your task {title} is due tomorrow.\n\n"
            f"Deadline: {due_at}\n"
            f"Priority: {priority.upper()}\n\n"
            "You've still got time. Want to get it done today? "
            "You've got this! - Nudge"
        )

    if reminder_type == "3_hour":
        return (
            "Quick reminder!\n\n"
            f"{title} is due in about 3 hours.\n\n"
            f"Deadline: {due_at}\n"
            f"Priority: {priority.upper()}\n\n"
            "Time to wrap this one up. You've got this! - Nudge"
        )

    return (
        "Deadline alert\n\n"
        f"{title} is now overdue.\n\n"
        f"Deadline was: {due_at}\n"
        f"Priority: {priority.upper()}\n\n"
        "Don't panic. Let's get this back on track. - Nudge"
    )


def send_to_discord(client, message):
    conversation_id = os.environ.get("CASPIAN_CONVERSATION_ID")

    if not conversation_id:
        raise RuntimeError(
            "CASPIAN_CONVERSATION_ID is missing from the environment."
        )

    return client.send_message(
        conversation_id,
        text=message,
    )


def send_to_email(client, message):
    connection_id = os.environ.get(
        "CASPIAN_EMAIL_CONNECTION_ID"
    )

    recipient = os.environ.get(
        "CASPIAN_EMAIL_RECIPIENT"
    )

    if not connection_id:
        raise RuntimeError(
            "CASPIAN_EMAIL_CONNECTION_ID is missing from the environment."
        )

    if not recipient:
        raise RuntimeError(
            "CASPIAN_EMAIL_RECIPIENT is missing from the environment."
        )

    return client.initiate(
        connection_id,
        recipient,
        message,
    )


def send_pending_reminders():
    client = create_caspian_client()

    reminders = get_due_reminders()

    if not reminders:
        print("No reminders to send.")
        return

    for reminder in reminders:
        message = build_reminder_message(reminder)

        print(
            f"Sending reminder for task #{reminder['task_id']}..."
        )

        discord_result = send_to_discord(
            client,
            message,
        )

        print(
            "Discord delivery successful:",
            discord_result,
        )

        email_result = send_to_email(
            client,
            message,
        )

        print(
            "Email delivery successful:",
            email_result,
        )

        mark_reminder_sent(
            reminder["task_id"],
            reminder["reminder_type"],
        )

        print(
            f"Marked reminder as sent for task "
            f"#{reminder['task_id']}."
        )


if __name__ == "__main__":
    send_pending_reminders()