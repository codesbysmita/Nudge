import os
import threading

from app.scheduler import run_scheduler
from dotenv import load_dotenv
from caspian_sdk import CommClient

from app.agent import understand_message, execute_action
from app.database import initialize_database


load_dotenv()


def create_caspian_client():
    caspian_key = os.environ.get("CASPIAN_API_KEY")
    caspian_base_url = os.environ.get("CASPIAN_BASE_URL")

    if not caspian_key:
        raise RuntimeError("CASPIAN_API_KEY is missing from .env")

    if not caspian_base_url:
        raise RuntimeError("CASPIAN_BASE_URL is missing from .env")

    return CommClient(
        api_key=caspian_key,
        base_url=caspian_base_url,
    )


caspian = create_caspian_client()


@caspian.on_message
def handle_message(message):
    try:
        user_text = getattr(message, "text", None)

        if not user_text:
            return

        print(f"Message ID: {message.id}")
        print(f"User: {user_text}")

        result = understand_message(user_text)

        print(f"Agent decision: {result}")

        reply_text = execute_action(result)

        print(f"Nudge: {reply_text}")

        caspian.reply(
            message_id=message.id,
            text=reply_text,
        )

    except Exception as error:
        print(f"Error while processing message: {error}")

        try:
            caspian.reply(
                message_id=message.id,
                text=(
                    "Sorry, I ran into a problem while processing that. "
                    "Please try again."
                ),
            )
        except Exception as reply_error:
            print(f"Could not send error reply: {reply_error}")




if __name__ == "__main__":
    initialize_database()

    scheduler_thread = threading.Thread(
        target=run_scheduler,
        daemon=True,
    )
    scheduler_thread.start()

    print("===================================")
    print("        NUDGE IS RUNNING")
    print("===================================")
    print("Connected channels: Email + Discord")
    print("Reminder scheduler: ON")
    print("Waiting for messages...")
    print()

    caspian.listen()