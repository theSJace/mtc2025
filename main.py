from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.warnings import PTBUserWarning
from warnings import filterwarnings
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Get environment variables or use default values
OLLAMA_ENDPOINT = os.environ.get("OLLAMA_ENDPOINT", "http://localhost:11434")
TELEBOT_TOKEN = os.environ.get("TELEBOT-TOKEN", None)

# Check if TELEBOT_TOKEN is set
if TELEBOT_TOKEN is None:
    raise ValueError("TELEBOT-TOKEN environment variable is not set. Please set it before running the script.")

from utils import *

# States
MAINMENU, MENUWRAPPER, MAKAN, JOMXZ, SEMBANG, SEMBANG_FREQUENCY, SEMBANG_DAY, SEMBANG_TIME, SEMBANG_REFLECTION = range(9)

# <--START OF BUTTON CREATION FUNCTIONS-->
def buttonOption():
    return InlineKeyboardMarkup([[InlineKeyboardButton("Nani1", callback_data="Nani1")],[InlineKeyboardButton("Nani2", callback_data="Nani2")]])

def frequency_buttons():
    keyboard = [
        [InlineKeyboardButton("Daily", callback_data="daily")],
        [InlineKeyboardButton("Weekly", callback_data="weekly")],
        [InlineKeyboardButton("Monthly", callback_data="monthly")],
        [InlineKeyboardButton("Custom", callback_data="custom")]
    ]
    return InlineKeyboardMarkup(keyboard)

def day_buttons():
    keyboard = [
        [InlineKeyboardButton("Monday", callback_data="monday")],
        [InlineKeyboardButton("Tuesday", callback_data="tuesday")],
        [InlineKeyboardButton("Wednesday", callback_data="wednesday")],
        [InlineKeyboardButton("Thursday", callback_data="thursday")],
        [InlineKeyboardButton("Friday", callback_data="friday")],
        [InlineKeyboardButton("Saturday", callback_data="saturday")],
        [InlineKeyboardButton("Sunday", callback_data="sunday")]
    ]
    return InlineKeyboardMarkup(keyboard)

def time_buttons():
    keyboard = [
        [InlineKeyboardButton("7:00 PM", callback_data="7:00 PM")],
        [InlineKeyboardButton("8:00 PM", callback_data="8:00 PM")],
        [InlineKeyboardButton("9:00 PM", callback_data="9:00 PM")],
        [InlineKeyboardButton("Custom time", callback_data="custom_time")]
    ]
    return InlineKeyboardMarkup(keyboard)
# <--END OF BUTTON CREATION FUNCTIONS-->

# <--START OF STATE FUNCTIONS-->
async def start(update, context):
    await update.message.reply_text("Selamat pagi Keluarga Bahagia! I'm KeluargaAI, your family assistant.\n\nUse my commands to help plan family meals, activities, and reflection time together.\n\n /makan - Decide what and where to eat\n /jomxz - Find activities based on interests\n /sembang - Schedule family reflection time")
    return ConversationHandler.END

async def cancel(update, context):
    await update.message.reply_text("Thank you for using this service.")
    return ConversationHandler.END

async def makan_command(update, context):
    user = update.message.from_user
    await update.message.reply_text(f"{user.first_name} - {update.message.date.strftime('%I:%M %p')}\nI'm checking preferences for all family members in this group...\n\nBased on everyone's food preferences and allergies, here are some recommendations:\n\nRecommended Dish: Nasi Lemak family set (safe for everyone, and a favorite of Abang and Kakak)\n\nRestaurant Options:\n1. Selera Rasa Nasi Lemak (Geylang)\n2. Punggol Nasi Lemak (Tanjong Katong)\n3. The Coconut Club (Ann Siang)\n\nConsiderations:\n• Adik is allergic to peanuts (all recommended places offer peanut-free options)\n• Ayah prefers spicy food (all locations have sambal options)\n• Abang has shellfish allergy (all recommended dishes are shellfish-free)\n\nWould you like more options or information about any of these places?")
    return ConversationHandler.END

async def jomxz_command(update, context):
    user = update.message.from_user
    await update.message.reply_text(f"{user.first_name} - {update.message.date.strftime('%I:%M %p')}\nLooking at everyone's hobbies and interests...\n\nFamily Activity Suggestions:\n\n1. Photography Walk at Gardens by the Bay\n• Perfect for Abang's photography hobby\n• Adik and Kakak can enjoy the outdoor environment\n• Ibu's interest in flowers is covered\n\n2. Board Game Café Visit\n• Matches Adik and Ayah's gaming interests\n• Indoor activity for hot weather\n• Food options available for everyone\n\n3. East Coast Park Cycling\n• Outdoor activity for everyone\n• Combines Ibu's cycling hobby\n• Food options nearby that match family preferences\n\nWhich activity sounds most interesting to everyone?")
    return ConversationHandler.END

async def sembang_command(update, context):
    user = update.message.from_user
    await update.message.reply_text(
        f"{user.first_name} - {update.message.date.strftime('%I:%M %p')}\nYou've initiated family reflection time. First, let's set up a schedule for regular reflections. How often would you like to have family reflection time?",
        reply_markup=frequency_buttons()
    )
    return SEMBANG_FREQUENCY

async def sembang_frequency(update, context):
    query = update.callback_query
    await query.answer()
    frequency = query.data
    context.user_data['frequency'] = frequency
    
    user = query.from_user
    
    if frequency == 'weekly':
        await query.edit_message_text(
            f"{user.first_name} - {query.message.date.strftime('%I:%M %p')}\nWhich day of the week works best for everyone?",
            reply_markup=day_buttons()
        )
        return SEMBANG_DAY
    else:
        # Handle other frequencies (daily, monthly, custom)
        # For simplicity, we'll just go to time selection for all other options
        await query.edit_message_text(
            f"{user.first_name} - {query.message.date.strftime('%I:%M %p')}\nWhat time would be good for everyone?",
            reply_markup=time_buttons()
        )
        return SEMBANG_TIME

async def sembang_day(update, context):
    query = update.callback_query
    await query.answer()
    day = query.data
    context.user_data['day'] = day
    
    user = query.from_user
    
    await query.edit_message_text(
        f"{user.first_name} - {query.message.date.strftime('%I:%M %p')}\nWhat time would be good for everyone?",
        reply_markup=time_buttons()
    )
    return SEMBANG_TIME

async def sembang_time(update, context):
    query = update.callback_query
    await query.answer()
    time = query.data
    context.user_data['time'] = time
    
    user = query.from_user
    frequency = context.user_data.get('frequency', 'weekly')
    day = context.user_data.get('day', 'Sunday')
    
    schedule_text = ''
    if frequency == 'daily':
        schedule_text = f"every day at {time}"
    elif frequency == 'weekly':
        schedule_text = f"every {day.capitalize()} at {time}"
    elif frequency == 'monthly':
        schedule_text = f"monthly at {time}"
    else:
        schedule_text = f"at {time}"
    
    await query.edit_message_text(
        f"{user.first_name} - {query.message.date.strftime('%I:%M %p')}\nGreat! I've scheduled family reflection time for {schedule_text}.\n✓ Family Reflection: {schedule_text.capitalize()}\n\nLet's start with today's reflection. Everyone please share:\n1. One highlight from your week\n2. One challenge you faced\n3. Something you're looking forward to next week\n\nWho would like to start?"
    )
    return SEMBANG_REFLECTION

async def sembang_reflection(update, context):
    user = update.message.from_user
    reflection = update.message.text
    
    await update.message.reply_text(
        f"Ayah - {update.message.date.strftime('%I:%M %p')}\nThank you for sharing, {user.first_name}! Who would like to go next?"
    )
    return SEMBANG_REFLECTION
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
    
    # Main conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENUWRAPPER:[
                CallbackQueryHandler(buttonClick)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Sembang (reflection) conversation handler
    sembang_handler = ConversationHandler(
        entry_points=[CommandHandler("sembang", sembang_command)],
        states={
            SEMBANG_FREQUENCY: [CallbackQueryHandler(sembang_frequency)],
            SEMBANG_DAY: [CallbackQueryHandler(sembang_day)],
            SEMBANG_TIME: [CallbackQueryHandler(sembang_time)],
            SEMBANG_REFLECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, sembang_reflection)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Add all handlers
    application.add_handler(conv_handler)
    application.add_handler(sembang_handler)
    application.add_handler(CommandHandler("makan", makan_command))
    application.add_handler(CommandHandler("jomxz", jomxz_command))
    
    application.run_polling()

if __name__ == '__main__':
    main()