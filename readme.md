# KeluargaAI Telegram Bot

A family assistant Telegram bot designed to strengthen the bonds between families in Singapore. The bot helps families plan meals, activities, and reflection time together.

## Features

- 👤 **/profile** - View or edit your personal profile
- 🍚 **/makan** - Decide what and where to eat
- 📅 **/jomxz** - Find activities based on interests
- 💬 **/sembang** - Schedule family reflection time

## Requirements

Python - 3.11 or higher

## Setup and Installation

### 1. Setting up UV through Homebrew

UV is a fast Python package installer and resolver. To install UV using Homebrew:

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install UV
brew install uv
```

### 2. Setting up the Project

1. Clone the repository
2. Set up environment variables:
   - Option 1: Create a `.env` file in the project root with the following content:
     ```
     OLLAMA_ENDPOINT="http://localhost:11434"
     TELEBOT-TOKEN="your_telegram_bot_token_here"
     ```
   - Option 2: Set environment variables in your system:
     ```bash
     # For macOS/Linux
     export OLLAMA_ENDPOINT="http://localhost:11434"
     export TELEBOT-TOKEN="your_telegram_bot_token_here"
     
     # For Windows
     set OLLAMA_ENDPOINT=http://localhost:11434
     set TELEBOT-TOKEN=your_telegram_bot_token_here
     ```

### 3. Running the Bot with UV

UV provides a faster and more reliable way to run Python applications with dependency management:

```bash
# Navigate to the project directory
cd /path/to/project

# Run the bot using UV
uv run python main.py
```

## Troubleshooting

### Solving Multiple Instances of Bot Issue

If you encounter the error: `Conflict: terminated by other getUpdates request; make sure that only one bot instance is running`, follow these steps:

1. Find running bot instances:
   ```bash
   ps aux | grep python | grep main.py
   ```

2. Terminate existing instances (replace PID1, PID2 with the actual process IDs from the previous command):
   ```bash
   kill PID1 PID2
   ```

3. Verify that no instances are running:
   ```bash
   ps aux | grep python | grep main.py
   ```

4. Start a new instance:
   ```bash
   uv run python main.py
   ```

## Adding New Routes to the Telegram Bot

To add a new command/route to the bot, follow these steps:

1. **Define a new state constant** in the States section:
   ```python
   # Add your new states
   NEW_COMMAND, NEW_COMMAND_STEP1, NEW_COMMAND_STEP2 = range(18, 21)  # Continue from the last state number
   ```

2. **Create command handler function** in the STATE FUNCTIONS section:
   ```python
   async def new_command(update, context):
       user = update.message.from_user
       await update.message.reply_text(
           f"{user.first_name} - {update.message.date.strftime('%I:%M %p')}\n"
           "Your new command response here."
       )
       return ConversationHandler.END  # Or return to next state if using conversation
   ```

3. **Create a conversation handler** (if your command has multiple steps):
   ```python
   # In the main() function
   new_command_handler = ConversationHandler(
       entry_points=[CommandHandler("new_command", new_command)],
       states={
           NEW_COMMAND_STEP1: [MessageHandler(filters.TEXT & ~filters.COMMAND, step1_handler)],
           NEW_COMMAND_STEP2: [MessageHandler(filters.TEXT & ~filters.COMMAND, step2_handler)],
       },
       fallbacks=[CommandHandler("cancel", cancel)],
   )
   ```

4. **Register the handler** in the main() function:
   ```python
   # For simple commands
   application.add_handler(CommandHandler("new_command", new_command))
   
   # Or for conversation handlers
   application.add_handler(new_command_handler)
   ```

5. **Update the start command** to include your new command in the welcome message:
   ```python
   await update.message.reply_text(f"...\n\n🆕 /new_command - Description of your new command")
   ```

## Project Structure

- `main.py` - Main application file with bot logic
- `utils.py` - Utility functions
- `profiles/` - Directory for storing user profiles
- `requirements.txt` - Python dependencies
- `pyproject.toml` - Project configuration
- `.env` - Environment variables (create this file)

## License

MIT