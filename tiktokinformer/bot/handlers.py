"""
Module for all the handlers which will be processed by the ConversationHandler
"""
import datetime as dt
import re
import telegram
from tiktokinformer.bot.dialog import reader
from telegram.ext import Updater

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
    code = update.effective_user.language_code
    context.bot.sendMessage(chat_id=update.effective_chat.id,
                            text=reader.stop_bot_info(),
                            parse_mode=telegram.ParseMode.HTML,
                            disable_web_page_preview=True)

    return telegram.ext.ConversationHandler.END


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


def main_menu_handler(update: telegram.Update, context: telegram.ext.CallbackContext):
    """
    The handler for the main menu. This handler process commands for the main menu.
    """
    pass


def process_entries(text: str, update: telegram.Update, context: telegram.ext.CallbackContext) -> set:
    """
    Method processes the text received from the user and checks that entries are correct.
    This method will be called by add_lists_handler that processes adding new lists of entries.
    Returns a list of tuples that contain the name of an entry and the date.
    """
    language_code = update.effective_user.language_code if update.effective_user.language_code == 'ru' else 'en'

    incorrect_lines = set()
    entries = set()
    for line in text.splitlines():
        line.strip()
        # Check the line matches the pattern
        if not re.match(
                r"^[\w ]+ *- *((0?[1-9])|([1-2][0-9])|(3[0-1]))(( +[а-яА-Яa-zA-Z]{3,9})|([./]((0?[1-9])|(1[0-2]))))"
                r"( +((0?[0-9])|(1[0-9])|(2[0-3])):([0-5][0-9])(:[0-5][0-9])?)?$",
                line, re.IGNORECASE):
            incorrect_lines.add(line)
        else:
            # Get the name and the date of an entry
            name, date_entry = [x.strip() for x in line.split('-')]

            time = None
            _splits = re.split(r'[ ./]+', date_entry, maxsplit=2)
            if len(_splits) == 2:
                day, month = _splits
            elif len(_splits) == 3:
                day, month, time = _splits
                time = time.split(':')
                if len(time) == 2:
                    time = dt.time(hour=int(time[0]), minute=int(time[1]))
                elif len(time) == 3:
                    time = dt.time(hour=int(time[0]), minute=int(time[1]), second=int(time[2]))
                else:
                    time = dt.time.fromisoformat('12:00:00')
            else:
                raise ValueError("Incorrect entry in the process_entries function")

            year = dt.datetime.now().year

            # A day or a month may be incorrect
            try:
                date_entry = dt.date(year=year, month=int(month), day=int(day))
                entries.add((name, date_entry, time))
            except ValueError:
                incorrect_lines.add(line)

    # Send incorrect lines to the user
    if incorrect_lines:
        chat_id = update.effective_chat.id
        code = update.effective_user.language_code
        context.bot.sendMessage(chat_id=chat_id,
                                text="",
                                parse_mode=telegram.ParseMode.HTML)
    return entries
