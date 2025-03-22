from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.warnings import PTBUserWarning
from warnings import filterwarnings
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import requests

# Load environment variables from .env file if it exists
load_dotenv()

# Get environment variables or use default values
OLLAMA_ENDPOINT = os.environ.get("OLLAMA_ENDPOINT", "http://localhost:11434")
TELEBOT_TOKEN = os.environ.get("TELEBOT-TOKEN", None)
API_ENDPOINT = os.environ.get("API_ENDPOINT", "http://localhost:8000")

# Check if TELEBOT_TOKEN is set
if TELEBOT_TOKEN is None:
    raise ValueError("TELEBOT-TOKEN environment variable is not set. Please set it before running the script.")

from utils import *

# States
MAINMENU, MENUWRAPPER, MAKAN, JOMXZ, SEMBANG, SEMBANG_FREQUENCY, SEMBANG_DAY, SEMBANG_TIME, SEMBANG_REFLECTION = range(9)
# Profile states
PROFILE_MENU, PROFILE_VIEW, PROFILE_EDIT, PROFILE_NICKNAME, PROFILE_DOB, PROFILE_ROLE, PROFILE_EMAIL, PROFILE_HOBBIES, PROFILE_FOOD_LIKES, PROFILE_FOOD_DISLIKES, PROFILE_PARENT_ID, PROFILE_EDIT_MENU, PROFILE_EDIT_HOBBIES, PROFILE_EDIT_FOOD_LIKES, PROFILE_EDIT_FOOD_DISLIKES = range(9, 24)

# Profiles directory
PROFILES_DIR = "profiles"
os.makedirs(PROFILES_DIR, exist_ok=True)

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

def profile_menu_buttons():
    keyboard = [
        [InlineKeyboardButton("View my profile", callback_data="view_profile")],
        [InlineKeyboardButton("Edit my profile", callback_data="edit_profile")],
        [InlineKeyboardButton("Exit menu", callback_data="exit_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)
# <--END OF BUTTON CREATION FUNCTIONS-->

# <--START OF HELPER FUNCTIONS-->
def get_profile_path(user_id):
    return os.path.join(PROFILES_DIR, f"{user_id}.json")

def save_profile(user_id, profile_data):
    # Ensure profiles directory exists
    os.makedirs(PROFILES_DIR, exist_ok=True)
    
    # Save to local JSON file
    profile_path = os.path.join(PROFILES_DIR, f"{user_id}.json")
    with open(profile_path, 'w') as f:
        json.dump(profile_data, f, indent=4)
    
    # Prepare data for API
    api_data = {
        "userNickName": profile_data.get('nickname', ''),
        "userEmail": profile_data.get('email', ''),
        "userDob": profile_data.get('dob', ''),
        "userType": profile_data.get('role', ''),
        "hobbies": profile_data.get('hobbies', ''),
        "food_likes": profile_data.get('food_likes', ''),
        "food_dislikes": profile_data.get('food_dislikes', ''),
        "parentId": profile_data.get('parent_id', ''),
        "userId": str(user_id)
    }
    
    # Send data to API
    try:
        response = requests.post(f"{API_ENDPOINT}/user", json=api_data)
        if response.status_code == 200 or response.status_code == 201:
            logging.info(f"Profile for user {user_id} successfully sent to API")
        else:
            logging.error(f"Failed to send profile to API. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        logging.error(f"Error sending profile to API: {str(e)}")

def load_profile(user_id):
    profile_path = get_profile_path(user_id)
    if os.path.exists(profile_path):
        with open(profile_path, 'r') as f:
            return json.load(f)
    return None
# <--END OF HELPER FUNCTIONS-->

# <--START OF STATE FUNCTIONS-->
async def start(update, context):
    # Get the user's Telegram ID
    user_id = update.message.from_user.id
    
    # Check if profile exists in database
    # TODO: Integrate with database later. Using static check for now.
    profile = load_profile(user_id)
    
    if profile:
        # Profile found, send welcome message
        await update.message.reply_text(
            "Selamat pagi Keluarga Bahagia! I'm KeluargaAI, your family assistant.\n\n"
            "Use my commands to help plan family meals, activities, and reflection time together.\n\n"
            "🍚 /makan - Decide what and where to eat\n\n"
            "📅 /jomxz - Find activities based on interests\n\n"
            "💬 /sembang - Schedule family reflection time\n\n"
            "👤 /profile - View and update your family profile"
        )
        return ConversationHandler.END
    else:
        # No profile found, start profile creation flow
        await update.message.reply_text(
            "Selamat datang! I'm KeluargaAI, your family companion designed to strengthen the bonds between families in Singapore.\n\n"
            "In today's busy world, I'm here to help your family stay connected, celebrate traditions, and create meaningful moments together.\n\n"
            "Whether you're looking for activities to do as a family, or ways to connect across generations, I'm here to assist.\n\n"
            "Let's set up your profile first so I can better assist you!"
        )
        await update.message.reply_text("Question 1: What's your nickname?")
        return PROFILE_NICKNAME

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
        f"{user.first_name} - {query.message.date.strftime('%I:%M %p')}\nGreat! I've scheduled family reflection time for {schedule_text}.\n✅ Family Reflection: {schedule_text.capitalize()}\n\nLet's start with today's reflection. Everyone please share:\n1. One highlight from your week\n2. One challenge you faced\n3. Something you're looking forward to next week\n\nWho would like to start?"
    )
    return SEMBANG_REFLECTION

async def sembang_reflection(update, context):
    user = update.message.from_user
    reflection = update.message.text
    
    await update.message.reply_text(
        f"Ayah - {update.message.date.strftime('%I:%M %p')}\nThank you for sharing, {user.first_name}! Who would like to go next?"
    )
    return SEMBANG_REFLECTION

# Profile functions
async def profile_command(update, context):
    await update.message.reply_text(
        "Profile Menu:",
        reply_markup=profile_menu_buttons()
    )
    return PROFILE_MENU

async def profile_menu_handler(update, context):
    query = update.callback_query
    await query.answer()
    choice = query.data
    
    if choice == "view_profile":
        user_id = query.from_user.id
        profile = load_profile(user_id)
        
        if profile:
            profile_text = f"Telegram ID: {profile.get('user_id', 'Not set')}\n"
            profile_text += f"Nickname: {profile.get('nickname', 'Not set')}\n"
            profile_text += f"Date of Birth: {profile.get('dob', 'Not set')}\n"
            profile_text += f"Role: {profile.get('role', 'Not set')}\n"
            if profile.get('role') == 'Child':
                profile_text += f"Parent ID: {profile.get('parent_id', 'Not set')}\n"
            else:  # Parent
                profile_text += f"Email: {profile.get('email', 'Not set')}\n"
            profile_text += f"Hobbies: {profile.get('hobbies', 'Not set')}\n"
            profile_text += f"Food likes: {profile.get('food_likes', 'Not set')}\n"
            profile_text += f"Food dislikes: {profile.get('food_dislikes', 'Not set')}"
            
            # Create keyboard with edit and back buttons
            keyboard = [
                [InlineKeyboardButton("Edit Profile", callback_data="edit_profile")],
                [InlineKeyboardButton("Back to Main Menu", callback_data="exit_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(profile_text, reply_markup=reply_markup)
            return PROFILE_MENU
        else:
            # Start profile creation automatically
            await query.edit_message_text("Let's set up your profile! I'll ask you a few questions.")
            await query.message.reply_text("Question 1: What's your nickname?")
            return PROFILE_NICKNAME
    
    elif choice == "edit_profile":
        # Show edit menu with options for what can be edited
        keyboard = [
            [InlineKeyboardButton("Edit Hobbies", callback_data="edit_hobbies")],
            [InlineKeyboardButton("Edit Food Likes", callback_data="edit_food_likes")],
            [InlineKeyboardButton("Edit Food Dislikes", callback_data="edit_food_dislikes")],
            [InlineKeyboardButton("Back", callback_data="view_profile")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text("What would you like to edit?", reply_markup=reply_markup)
        return PROFILE_EDIT_MENU
    
    elif choice == "exit_menu":
        await query.edit_message_text("Returning to main menu.")
        return ConversationHandler.END

async def profile_edit_menu_handler(update, context):
    query = update.callback_query
    await query.answer()
    choice = query.data
    
    if choice == "edit_hobbies":
        await query.edit_message_text("Please enter your new hobbies:")
        return PROFILE_EDIT_HOBBIES
    elif choice == "edit_food_likes":
        await query.edit_message_text("Please enter your new food likes:")
        return PROFILE_EDIT_FOOD_LIKES
    elif choice == "edit_food_dislikes":
        await query.edit_message_text("Please enter your new food dislikes:")
        return PROFILE_EDIT_FOOD_DISLIKES
    elif choice == "view_profile":
        # Go back to viewing profile
        return await profile_menu_handler(update, context)

async def profile_edit_hobbies(update, context):
    user_id = update.message.from_user.id
    profile = load_profile(user_id)
    if profile:
        profile['hobbies'] = update.message.text
        save_profile(user_id, profile)
        await update.message.reply_text(f"Your hobbies have been updated to: {update.message.text}")
    else:
        await update.message.reply_text("No profile found. Please create a profile first.")
    return ConversationHandler.END

async def profile_edit_food_likes(update, context):
    user_id = update.message.from_user.id
    profile = load_profile(user_id)
    if profile:
        profile['food_likes'] = update.message.text
        save_profile(user_id, profile)
        await update.message.reply_text(f"Your food likes have been updated to: {update.message.text}")
    else:
        await update.message.reply_text("No profile found. Please create a profile first.")
    return ConversationHandler.END

async def profile_edit_food_dislikes(update, context):
    user_id = update.message.from_user.id
    profile = load_profile(user_id)
    if profile:
        profile['food_dislikes'] = update.message.text
        save_profile(user_id, profile)
        await update.message.reply_text(f"Your food dislikes have been updated to: {update.message.text}")
    else:
        await update.message.reply_text("No profile found. Please create a profile first.")
    return ConversationHandler.END

async def profile_nickname(update, context):
    # Initialize profile with user_id
    user_id = update.message.from_user.id
    context.user_data['profile'] = context.user_data.get('profile', {})
    context.user_data['profile']['user_id'] = user_id
    context.user_data['profile']['nickname'] = update.message.text
    
    # Create calendar for date selection
    # For now, we'll use a simple text input as Telegram doesn't have a built-in date picker
    # In a real implementation, you might want to use a custom calendar component
    await update.message.reply_text("Question 2: Please input your Date Of Birth (DD/MM/YYYY):")
    return PROFILE_DOB

async def profile_dob(update, context):
    context.user_data['profile']['dob'] = update.message.text
    
    # Create role selection buttons
    keyboard = [
        [InlineKeyboardButton("Parent", callback_data="Parent")],
        [InlineKeyboardButton("Child", callback_data="Child")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("Question 3: Are you a parent or child?", reply_markup=reply_markup)
    return PROFILE_ROLE

async def profile_role(update, context):
    query = update.callback_query
    await query.answer()
    
    role = query.data
    context.user_data['profile']['role'] = role
    
    await query.edit_message_text(f"You selected: {role}")
    
    # Different flow based on role
    if role == 'Parent':
        await query.message.reply_text("Question 4: What is your email address?")
        return PROFILE_EMAIL
    else:  # Child
        await query.message.reply_text("Question 4: What are your hobbies?")
        return PROFILE_HOBBIES

async def profile_email(update, context):
    context.user_data['profile']['email'] = update.message.text
    
    await update.message.reply_text("Question 5: What are your hobbies?")
    return PROFILE_HOBBIES

async def profile_hobbies(update, context):
    context.user_data['profile']['hobbies'] = update.message.text
    
    await update.message.reply_text("Question 6: What food do you like to eat?")
    return PROFILE_FOOD_LIKES

async def profile_food_likes(update, context):
    context.user_data['profile']['food_likes'] = update.message.text
    
    await update.message.reply_text("Question 7: What food do you dislike to eat?")
    return PROFILE_FOOD_DISLIKES

async def profile_food_dislikes(update, context):
    context.user_data['profile']['food_dislikes'] = update.message.text
    
    # If role is Child, ask for parent ID
    if context.user_data['profile'].get('role') == 'Child':
        await update.message.reply_text("Question 8: What is your parent id? This is required for child profiles.")
        return PROFILE_PARENT_ID
    else:
        # If role is Parent, save profile and finish
        user_id = update.message.from_user.id
        save_profile(user_id, context.user_data['profile'])
        return await complete_profile(update, context)

async def profile_parent_id(update, context):
    user_id = update.message.from_user.id
    context.user_data['profile']['parent_id'] = update.message.text
    
    # Save the profile
    save_profile(user_id, context.user_data['profile'])
    
    return await complete_profile(update, context)

async def complete_profile(update, context):
    profile = context.user_data['profile']
    profile_text = "Thank you! Here is the summary of your profile:\n\n"
    profile_text += f"Telegram ID: {profile.get('user_id', 'Not set')}\n"
    profile_text += f"Nickname: {profile.get('nickname', 'Not set')}\n"
    profile_text += f"Date of Birth: {profile.get('dob', 'Not set')}\n"
    profile_text += f"Role: {profile.get('role', 'Not set')}\n"
    if profile.get('role') == 'Child':
        profile_text += f"Parent ID: {profile.get('parent_id', 'Not set')}\n"
    else:  # Parent
        profile_text += f"Email: {profile.get('email', 'Not set')}\n"
    profile_text += f"Hobbies: {profile.get('hobbies', 'Not set')}\n"
    profile_text += f"Food likes: {profile.get('food_likes', 'Not set')}\n"
    profile_text += f"Food dislikes: {profile.get('food_dislikes', 'Not set')}"
    
    await update.message.reply_text(profile_text)
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
    
    # Main conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENUWRAPPER:[
                CallbackQueryHandler(buttonClick)
            ],
            PROFILE_NICKNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_nickname)],
            PROFILE_DOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_dob)],
            PROFILE_ROLE: [CallbackQueryHandler(profile_role)],
            PROFILE_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_email)],
            PROFILE_HOBBIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_hobbies)],
            PROFILE_FOOD_LIKES: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_food_likes)],
            PROFILE_FOOD_DISLIKES: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_food_dislikes)],
            PROFILE_PARENT_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_parent_id)],
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
    
    # Profile conversation handler
    profile_handler = ConversationHandler(
        entry_points=[CommandHandler("profile", profile_command)],
        states={
            PROFILE_MENU: [CallbackQueryHandler(profile_menu_handler)],
            PROFILE_NICKNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_nickname)],
            PROFILE_DOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_dob)],
            PROFILE_ROLE: [CallbackQueryHandler(profile_role)],
            PROFILE_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_email)],
            PROFILE_HOBBIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_hobbies)],
            PROFILE_FOOD_LIKES: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_food_likes)],
            PROFILE_FOOD_DISLIKES: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_food_dislikes)],
            PROFILE_PARENT_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_parent_id)],
            PROFILE_EDIT_MENU: [CallbackQueryHandler(profile_edit_menu_handler)],
            PROFILE_EDIT_HOBBIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_edit_hobbies)],
            PROFILE_EDIT_FOOD_LIKES: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_edit_food_likes)],
            PROFILE_EDIT_FOOD_DISLIKES: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_edit_food_dislikes)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Add all handlers
    application.add_handler(conv_handler)
    application.add_handler(sembang_handler)
    application.add_handler(profile_handler)
    application.add_handler(CommandHandler("makan", makan_command))
    application.add_handler(CommandHandler("jomxz", jomxz_command))
    
    application.run_polling()

if __name__ == '__main__':
    main()