import telegram, logging

from modules.pytg.ModulesLoader import ModulesLoader

def text_message_handler(update, context):
    bot = context.bot

    message = update.message

    if not message or not message.chat:
        return

    chat_id = message.chat.id
    message_id = message.message_id

    username = message.from_user.username
    user_id = message.from_user.id

    text = message.text

    logging.info("Received text message update from {} ({}) in chat {}: {}".format(username, user_id, chat_id, text))

    data_manager = ModulesLoader.load_manager("data")

    # Check if the bot is waiting for a form input 
    if data_manager.has_data("forms", chat_id, module="forms"):
        current_user_form_id = chat_id

        forms_manager = ModulesLoader.load_manager("forms")

        form_data = data_manager.load_data("forms", current_user_form_id, module="forms")

        if form_data["digested"]:
            return

        form_name = form_data["form_name"]
        form_steps = forms_manager.load_form_steps(form_name)

        step_data = form_steps[form_data["current_step"]]

        if step_data["type"] == "text_field":
            input_data = {
                "text": text
            }

        elif step_data["type"] == "keyboard_reply":
            replies_map = step_data["map"] 

            if text not in replies_map.keys():
                return

            input_data = {
                "value": replies_map[text]
            }

        # elif step_data["type"] == "image_field":
        #     if not message.photo:
        #         return 

        #     photos = message.photo

        #     input_data = {
        #         "image_url": None 
        #     }
        else:
            return

        forms_manager.handle_input(bot, chat_id, message_id, form_name, form_data["current_step"], input_data)
