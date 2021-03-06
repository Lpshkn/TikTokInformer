"""
Module for all the handlers which will be processed by the ConversationHandler
"""
import re
import telegram
from bot.dialog import reader
from telegram.ext import Updater
from TikTokApi import TikTokApi
from TikTokApi.exceptions import TikTokNotFoundError

# Define all the states of the bot
MAIN, = range(1)


def start_handler(update: telegram.Update, context: telegram.ext.CallbackContext):
    """
    The handler to /start command. This handler send an localization message to the user.
    """
    chat_id = update.effective_chat.id
    context.bot.sendMessage(chat_id=chat_id,
                            text=reader.start_info(),
                            parse_mode=telegram.ParseMode.HTML,
                            disable_web_page_preview=True)

    update_chat_data(update, context)
    update_user_data(update, context)

    return MAIN


def stop_bot_handler(update: telegram.Update, context: telegram.ext.CallbackContext):
    """
    The handler to /stop command. This handler stops the bot and remove all data about the user
    """
    context.bot.sendMessage(chat_id=update.effective_chat.id,
                            text=reader.stop_bot_info(),
                            parse_mode=telegram.ParseMode.HTML,
                            disable_web_page_preview=True)

    return telegram.ext.ConversationHandler.END


def main_menu_handler(update: telegram.Update, context: telegram.ext.CallbackContext):
    """
    The handler for the main menu. This handler process commands for the main menu.
    """
    text = update.message.text
    delete = False
    correct = True
    unique_ids = []

    if text.startswith('-'):
        delete = True
        # Remove the minus
        text = text[1:].strip()

    # Check that all nicknames are corrected or send the error message
    for row in re.split(r'[\s]+', text):
        if re.match(r"^@[\w.]+$", row):
            # Remove '@' in the nickname
            unique_ids.append(row[1:])
        else:
            correct = False
            break

    if correct:
        api = TikTokApi.get_instance(use_selenium=True)
        for unique_id in unique_ids:
            try:
                # Check that users exist
                api.getUser(username=unique_id)
            except TikTokNotFoundError:
                context.bot.sendMessage(chat_id=update.effective_chat.id,
                                        text=f"Кажется, профиля с именем @{unique_id} не существует...\n"
                                             f"Пожалуйста, измените запрос.")
                return MAIN

        if delete:
            message = "Я удалил этих тиктокеров из вашего профиля. Не такие они и классные..."
        else:
            message = "Я добавил перечисленных тиктокеров к вам в профиль. Надеюсь, вы не ошибаетесь :)"

        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text=message)
        update_bot_data(update, context, unique_ids=unique_ids, delete=delete)
    else:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text="Я не понимаю о чём вы говорите :(")
    return MAIN


def update_chat_data(update: telegram.Update, context: telegram.ext.CallbackContext):
    """
    Function to update the chat_data receiving from the user.
    """
    context.chat_data['title'] = update.effective_chat.title
    context.chat_data['description'] = update.effective_chat.description
    context.chat_data['photo'] = update.effective_chat.photo


def update_user_data(update: telegram.Update, context: telegram.ext.CallbackContext):
    """
    Function to update the user_data receiving from the user.
    """
    context.user_data['chat_id'] = update.effective_chat.id
    context.user_data['username'] = update.effective_user.username
    context.user_data['first_name'] = update.effective_user.first_name
    context.user_data['last_name'] = update.effective_user.last_name


def update_bot_data(update: telegram.Update, context: telegram.ext.CallbackContext, unique_ids: list, delete=False):
    context.bot_data['unique_id'] = unique_ids
    context.bot_data['chat_id'] = update.effective_chat.id
    context.bot_data['delete'] = delete
