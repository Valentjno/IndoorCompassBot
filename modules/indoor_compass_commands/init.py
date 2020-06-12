import telegram, logging

from modules.pytg.ModulesLoader import ModulesLoader

from telegram.ext import CommandHandler

from .handlers.commands.start import start_cmd_handler

def load_command_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler(["start", "menu"], start_cmd_handler))

def initialize():
    logging.info("Initializing your_bot_commands module...")
    pass

def connect():
    logging.info("Connecting your_bot_commands module...")

    bot_manager = ModulesLoader.load_manager("bot")

    load_command_handlers(bot_manager.updater.dispatcher)

def load_manager():
    # There is no need for a manager in this package
    return None

def depends_on():
    return ["bot"]