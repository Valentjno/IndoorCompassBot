import telegram, logging

from datetime import datetime

from modules.pytg.ModulesLoader import ModulesLoader


def start_cmd_handler(update, context):
    bot = context.bot

    message = update.message
    chat_id = message.chat.id

    username = message.from_user.username
    user_id = message.from_user.id

    logging.info("Received start command update from {} ({}) in chat {}".format(username, user_id, chat_id))
    forms_manager = ModulesLoader.load_manager("forms")
    forms_manager.start_form(bot,chat_id,"send_photo")