"""
Module for printing and processing all the information about the bot or about actions with this bot
"""
import codecs
import os


def _get_info(filename: str) -> str:
    """
    Reads an HTML file and returns its content as a string
    :param filename: the filename of an HTML file
    :return: content of the file
    """
    with codecs.open(filename, 'r', 'utf-8') as file:
        return file.read()


INFO_DIRECTORY = os.path.join("tiktokinformer", "bot", "dialog", "info")


def start_info():
    return _get_info(os.path.join(INFO_DIRECTORY, "start_info.html"))


def stop_bot_info(language_code: str):
    return _get_info(os.path.join("./localization", get_language_code(language_code), "info", "stop_bot_info.html"))


def main_menu(language_code: str):
    return _get_menu(os.path.join("./localization", get_language_code(language_code), "menu", "main.json"))


def accept_cancel_menu(language_code: str):
    return _get_menu(os.path.join("./localization", get_language_code(language_code), "menu", "accept_cancel.json"))


def add_lists_info(language_code: str):
    return _get_info(os.path.join("./localization", get_language_code(language_code), "info", "add_lists_info.html"))


def error_adding_entry(language_code: str):
    return _get_info(
        os.path.join("./localization", get_language_code(language_code), "info", "error_adding_entry.html"))


def cancel(language_code: str):
    return _get_info(os.path.join("./localization", get_language_code(language_code), "info", "cancel.html"))


def accept(language_code: str):
    return _get_info(os.path.join("./localization", get_language_code(language_code), "info", "accept.html"))


def recall_message(language_code: str):
    return _get_info(os.path.join("./localization", get_language_code(language_code), "info", "recall_message.html"))
