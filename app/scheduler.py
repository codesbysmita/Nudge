import time

from app.reminder_sender import send_pending_reminders


CHECK_INTERVAL_SECONDS = 60


def run_scheduler():
    print("Nudge reminder scheduler started.")
    print("Checking for reminders every 60 seconds...")

    while True:
        try:
            send_pending_reminders()

        except Exception as error:
            print(f"Reminder scheduler error: {error}")

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_scheduler()