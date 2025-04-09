# Telegram To-Do List Bot

A feature-rich Telegram bot for managing your tasks and to-do lists in Persian language.

## Features

- ➕ Add new tasks with title and due date
- 📋 View list of all tasks
- ❌ Delete tasks by ID
- ✏️ Edit existing tasks
- 🔄 Automatic task ID management
- 🇮🇷 Full Persian language support

## Requirements

- Python 3.7+
- python-telegram-bot v20.0+
- python-decouple

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/telegram-todo-list-bot.git
cd telegram-todo-list-bot
````

2. Install dependencies:

```bash
pip install python-telegram-bot python-decouple
```

3. Create a `.env` file in the project root and add your Telegram Bot API token:

```
API_TOKEN=your_telegram_bot_token_here
```

4. Run the bot:

```bash
python handlers.py
```

## Usage

1. Start a chat with your bot on Telegram
2. Use the keyboard buttons to interact with the bot:
   - **➕ افزودن تسک**: Add a new task
   - **📋 لیست تسک‌ها**: View all tasks
   - **❌ حذف تسک**: Delete a task
   - **✏️ ویرایش تسک**: Edit a task

## Project Structure

- `handlers.py`: Main bot code with all command handlers
- `database.py`: Database operations for task management
- `.env`: Environment variables (not included in repository)

## Database Schema

The bot uses SQLite for data storage with the following schema:

```sql
CREATE TABLE tasks (
    user_id INTEGER,
    task_id INTEGER,
    task_text TEXT,
    due_date TEXT,
    PRIMARY KEY (user_id, task_id)
)
```

## How It Works

1. **Adding Tasks**: Users can add new tasks with a title and due date
2. **Viewing Tasks**: Users can view all their tasks with IDs, titles, and due dates
3. **Deleting Tasks**: Users can delete tasks by specifying the task ID
4. **Editing Tasks**: Users can edit task titles by specifying the task ID


## Contact

For any questions or suggestions, please open an issue on GitHub or contact [alighadami812@gmail.com].
