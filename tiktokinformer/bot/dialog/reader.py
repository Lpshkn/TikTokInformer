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


def stop_bot_info():
    return _get_info(os.path.join(INFO_DIRECTORY, "stop_info.html"))

