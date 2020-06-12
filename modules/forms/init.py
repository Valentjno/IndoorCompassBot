import logging

from modules.pytg.ModulesLoader import ModulesLoader

from modules.forms.FormsManager import FormsManager

from telegram.ext import CallbackQueryHandler, MessageHandler, Filters 

from modules.forms.handlers.callback.forms import forms_callback_handler

from modules.forms.handlers.messages.text import text_message_handler
from modules.forms.handlers.messages.photo import photo_message_handler
from modules.forms.handlers.messages.video import video_message_handler
from modules.forms.handlers.messages.animation import animation_message_handler

def load_messages_handlers(dispatcher):
    module_id = ModulesLoader.get_module_id("forms")

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, text_message_handler), group=module_id)
    dispatcher.add_handler(MessageHandler(Filters.photo, photo_message_handler), group=module_id)
    dispatcher.add_handler(MessageHandler(Filters.video, video_message_handler), group=module_id)
    dispatcher.add_handler(MessageHandler(Filters.animation, animation_message_handler), group=module_id)

def load_callback_handlers(dispatcher):
    dispatcher.add_handler(CallbackQueryHandler(forms_callback_handler, pattern="forms,.*"))

def initialize():
    logging.info("Initializing forms module...")

    FormsManager.initialize()

def connect():
    logging.info("Connecting forms module...")

    bot_manager = ModulesLoader.load_manager("bot")

    load_callback_handlers(bot_manager.updater.dispatcher)
    load_messages_handlers(bot_manager.updater.dispatcher)

def load_manager():
    return FormsManager.load()

def depends_on():
    return ["bot", "data", "cache"]