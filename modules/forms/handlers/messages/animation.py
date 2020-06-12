import telegram, logging

from modules.pytg.ModulesLoader import ModulesLoader

def animation_message_handler(update, context):
    bot = context.bot

    message = update.message

    if not message or not message.chat or not message.animation:
        return

    chat_id = message.chat.id
    message_id = message.message_id

    username = message.from_user.username
    user_id = message.from_user.id

    logging.info("Received animation message update from {} ({}) in chat {}".format(username, user_id, chat_id))

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

        if step_data["type"] != "animation_field":
            return

        animation = message.animation
        animation_id = animation.file_id
        animation_url = bot.getFile(animation_id).file_path

        input_data = {
            "animation_id": animation_id,
            "animation_url": animation_url 
        }

        forms_manager = ModulesLoader.load_manager("forms")
        forms_manager.handle_input(bot, chat_id, message_id, form_name, form_data["current_step"], input_data)

