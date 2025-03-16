from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.warnings import PTBUserWarning
from warnings import filterwarnings
import os

from utils import *

OLLAMA_ENDPOINT = os.environ["OLLAMA_ENDPOINT"]
TELEBOT_TOKEN = os.environ["TELEBOT-TOKEN"]

# States
MAINMENU, MENUWRAPPER = range(2)

# <--START OF BUTTON CREATION FUNCTIONS-->
def buttonOption():
    return InlineKeyboardMarkup([[InlineKeyboardButton("Nani1", callback_data="Nani1")],[InlineKeyboardButton("Nani2", callback_data="Nani2")]])
# <--END OF BUTTON CREATION FUNCTIONS-->

# <--START OF STATE FUNCTIONS-->
async def start(update, context):
    await update.message.reply_text("Welcome to ZIMBABA, what would you like to do?",reply_markup=buttonOption())
    return MENUWRAPPER

async def cancel(update, context):
    await update.message.reply_text("Thank you for using this service.")
    return ConversationHandler.END
# <--END OF STATE FUNCTIONS-->

# <--START OF CALLBACK FUNCTIONS-->
async def buttonClick(update, context):
    query = update.callback_query
    await query.answer()
    # contextData = context.user_data[""]
    buttonInput = query.data
    await query.edit_message_text("You have selected "+buttonInput)
    return MENUWRAPPER
# <--END OF CALLBACK FUNCTIONS-->

def main():
    application = Application.builder().token(TELEBOT_TOKEN).connect_timeout(30).read_timeout(30).write_timeout(30).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENUWRAPPER:[
                CallbackQueryHandler(buttonClick)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()