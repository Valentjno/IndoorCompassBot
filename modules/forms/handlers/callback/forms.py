import telegram, logging

from modules.pytg.ModulesLoader import ModulesLoader

def forms_callback_handler(update, context):
    bot = context.bot

    forms_manager = ModulesLoader.load_manager("forms")

    query = update.callback_query
    query_data = query.data.split(",")
    user_id = query.from_user.id

    username = query.message.chat.username
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    logging.info("Handling forms callback data from {}: {}".format(chat_id, query_data))

    if query_data[1] == "fixed_reply":
        data_manager = ModulesLoader.load_manager("data")

        form_data = data_manager.load_data("forms", chat_id, module="forms")

        step_name = form_data["current_step"]
        form_name = form_data["form_name"]

        # step_name = query_data[2]
        # form_name = query_data[3]

        input_data = {
            "action": query_data[2],
            "output_data": query_data[3]
        }

        bot.editMessageReplyMarkup(
            chat_id = chat_id,
            message_id = message_id,
            reply_markup = None
        )

        forms_manager.handle_input(bot, chat_id, message_id, form_name, step_name, input_data)
        return

    if query_data[1] == "jump":
        next_step_name = query_data[2]

        bot.editMessageReplyMarkup(
            chat_id = chat_id,
            message_id = message_id,
            reply_markup = None
        )

        forms_manager.set_next_step(bot, chat_id, message_id, next_step=next_step_name)
        return

    if query_data[1] == "show":
        form_name = query_data[2]

        forms_manager.start_form(bot, chat_id, form_name)

    if query_data[1] == "checkbox_click":
        entry = query_data[2]
        step_output = query_data[3]

        form_id = chat_id

        data_manager = ModulesLoader.load_manager("data")
        form_data = data_manager.load_data("forms", form_id, module="forms")

        if entry in form_data["form_entries"][step_output]:
            form_data["form_entries"][step_output].remove(entry)
        else:
            form_data["form_entries"][step_output].append(entry)

        data_manager.save_data("forms", form_id, form_data, module="forms")

        forms_manager.show_current_step(bot, chat_id, message_id)