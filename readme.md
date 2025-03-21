# Versioning
Python - 3.12.8

# How To Start
1. Open terminal/cmd in project directory
2. Run ```pip install -r ./requirements.txt```
3. Set up environment variables:
   - Option 1: Create a .env file in the project root (copy from .env.example)
   - Option 2: Set environment variables in your system:
     ```
     # For macOS/Linux
     export OLLAMA_ENDPOINT="http://localhost:11434"
     export TELEBOT_TOKEN="your_telegram_bot_token_here"
     
     # For Windows
     set OLLAMA_ENDPOINT=http://localhost:11434
     set TELEBOT_TOKEN=your_telegram_bot_token_here
     ```
4. Run main.py
   ```
   python main.py
   ```