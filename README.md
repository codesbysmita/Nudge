🧠 Nudge

An AI-powered personal deadline and task assistant that makes sure important things don't slip through the cracks.

Nudge turns natural-language messages into actionable tasks, stores them locally, tracks deadlines, and proactively sends reminders through Discord and Email.

Instead of manually maintaining a to-do list, you can simply tell Nudge what you need to remember.

---

✨ What is Nudge?

Students and busy individuals often keep deadlines scattered across chats, notes, calendars, and their memory.

Nudge provides a simple conversational interface:

You tell it → Nudge understands it → Nudge remembers it → Nudge reminds you.

For example:

«"I have a Machine Learning assignment due tomorrow at 6 PM and it is very important."»

Nudge extracts:

Action: ADD_TASK
Title: Machine Learning assignment
Deadline: Tomorrow, 6 PM
Priority: High

It then stores the task and can automatically remind you as the deadline approaches.

---

🚀 Features

🧠 Natural-language task understanding

Nudge uses an AI model through Featherless to interpret natural-language requests and convert them into structured actions.

Supported actions include:

- Add tasks
- List pending tasks
- Complete tasks
- Delete tasks

🗄️ Persistent task storage

Tasks are stored using SQLite with information including:

- Task ID
- Title
- Deadline
- Priority
- Status
- Creation time
- Reminder status

⏰ Automatic reminders

Nudge continuously checks for upcoming deadlines and supports:

- 24-hour reminders
- 3-hour reminders
- Overdue reminders
- Duplicate-reminder prevention

📡 Multi-channel notifications

Reminders can be delivered through:

- Discord
- Email

Both channels are handled through the Caspian SDK.

🔄 Background scheduler

A background scheduler checks the database every 60 seconds for reminders that need to be sent.

---

🏗️ Architecture

                         ┌─────────────────────┐
                         │       User          │
                         └──────────┬──────────┘
                                    │
                         Natural-language message
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     Nudge Agent     │
                         │ Featherless + LLM   │
                         └──────────┬──────────┘
                                    │
                           Structured action
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      SQLite DB      │
                         │                     │
                         │ Tasks + Deadlines   │
                         │ Status + Reminders  │
                         └──────────┬──────────┘
                                    │
                         Reminder scheduler
                            every 60 seconds
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  Reminder Sender    │
                         └──────────┬──────────┘
                                    │
                       ┌────────────┴────────────┐
                       ▼                         ▼
                ┌─────────────┐           ┌─────────────┐
                │   Discord   │           │    Email    │
                └─────────────┘           └─────────────┘

---

🛠️ Tech Stack

Technology with their purpose:
Python for Core application
SQLite for Local task persistence
Featherless for AI inference
MiniMax M2.5 for model
OpenAI Python SDK for API Client
Caspian SDK for Communication channels
Discord for Reminder delivery
Email for Reminder delivery
python-dotenv for Environment configuration

---

📁 Project Structure

Nudge/
│
├── app/
│   ├── __init__.py
│   ├── agent.py
│   ├── database.py
│   ├── main.py
│   ├── reminder_sender.py
│   ├── reminders.py
│   └── scheduler.py
│
├── .env.example
├── .gitignore
├── requirements.txt
├── test_featherless.py
└── README.md

---

⚙️ Setup

1. Clone the repository

git clone https://github.com/codesbysmita/Nudge.git
cd Nudge

2. Create a virtual environment

python -m venv .venv

Activate it on Windows:

.venv\Scripts\Activate.ps1

3. Install dependencies

pip install -r requirements.txt

4. Configure environment variables

Create a ".env" file based on ".env.example".

FEATHERLESS_API_KEY=your_key
CASPIAN_API_KEY=your_key
CASPIAN_BASE_URL=your_base_url

CASPIAN_CONVERSATION_ID=your_discord_conversation_id
CASPIAN_DISCORD_CONNECTION_ID=your_discord_connection_id

CASPIAN_EMAIL_CONNECTION_ID=your_email_connection_id
CASPIAN_EMAIL_RECIPIENT=your_email_address

Never commit ".env" to GitHub.

---

▶️ Running Nudge

From the project root:

python -m app.main

You should see:

Nudge reminder scheduler started.
===================================
        NUDGE IS RUNNING
===================================
Connected channels: Email + Discord
Reminder scheduler: ON
Waiting for messages...

---

💬 Example Interactions

Add a task

I have a DBMS assignment due Friday at 8 PM

Nudge understands:

Action: ADD_TASK
Title: DBMS assignment
Priority: High

List tasks

What are my pending tasks?

Example:

Here are your pending tasks:

#2 — Machine Learning assignment
due: 2026-08-11 18:00
priority: high

Delete a task

Delete task 1

Nudge:

Task #1 deleted.

---

⏰ Reminder Example

When a task approaches its deadline:

⏰ Due tomorrow

Task: Machine Learning assignment
Deadline: 2026-08-11 18:00
Priority: HIGH

You've got this. — Nudge

The reminder can be delivered to both Discord and Email.

---

🔐 Security

Nudge uses environment variables for credentials.

The repository intentionally excludes:

.env
*.db
pycache/

A ".env.example" file is provided as a safe configuration template.

Never commit API keys or other credentials to GitHub.

---

📌 Current Scope

Nudge is currently a local MVP.

The application runs as a continuously running Python process and uses SQLite for local persistence.

This architecture was intentionally kept lightweight for rapid prototyping and demonstration.

---

🔮 Future Improvements

Potential future versions could include:

- ☁️ Cloud database
- 🌐 Web dashboard
- 📱 Telegram support
- 📅 Calendar integration
- 🔁 Recurring tasks
- 🎯 Smarter priority detection
- 🧠 Personalized reminder timing
- 📊 Productivity analytics
- 🔐 User authentication
- ☁️ Fully hosted deployment

---

🎯 Why Nudge?

Deadlines don't usually fail because people don't know what they need to do.

They fail because the reminder comes too late — or never comes at all.

Nudge is built around one simple idea:

"Remember it once. Let Nudge remind you."