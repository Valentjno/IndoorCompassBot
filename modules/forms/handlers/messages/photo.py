import telegram, logging

from modules.pytg.ModulesLoader import ModulesLoader

def photo_message_handler(update, context):
    bot = context.bot

    message = update.message

    if not message or not message.chat or not message.photo:
        return

    chat_id = message.chat.id
    message_id = message.message_id

    username = message.from_user.username
    user_id = message.from_user.id

    logging.info("Received photo message update from {} ({}) in chat {}".format(username, user_id, chat_id))

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

        if step_data["type"] != "image_field":
            return

        photos = message.photo
        image_id = photos[-1].file_id
        image_url = bot.getFile(image_id).file_path

        input_data = {
            "image_id": image_id,
            "image_url": image_url 
        }

        forms_manager = ModulesLoader.load_manager("forms")
        forms_manager.handle_input(bot, chat_id, message_id, form_name, form_data["current_step"], input_data)

