import telegram, yaml, logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from modules.pytg.Manager import Manager
from modules.pytg.ModulesLoader import ModulesLoader

class FormsManager(Manager):
    @staticmethod
    def initialize():
        FormsManager.__instance = FormsManager()

        return

    @staticmethod
    def load():
        return FormsManager.__instance

    def __init__(self):
        self.digesters = { }

    ###################
    # Forms interface #
    ###################

    def add_digester(self, key, func):
        self.digesters[key] = func

    def clear_user_form_data(self, bot, chat_id, delete_messages=True):
        logging.info("Clearing form data for user {}".format(chat_id))

        data_manager = ModulesLoader.load_manager("data")

        form_id = chat_id
        if not data_manager.has_data("forms", form_id, module="forms"):
            return

        form_data = data_manager.load_data("forms", form_id, module="forms")

        # Clear form messages
        if delete_messages: # (not form_data["digested"]) and delete_messages:
            for form_message_id in form_data["messages"]:
                try:
                    bot.deleteMessage(
                        chat_id = chat_id,
                        message_id = form_message_id
                    )
                except:
                    logging.info("Unable to delete message {}".format(form_message_id))

        # Update form data
        data_manager.delete_data("forms", form_id, module="forms")

    def start_form(self, bot, chat_id, form_name, form_meta={}):
        logging.info("Starting form {} for {}".format(form_name, chat_id))

        data_manager = ModulesLoader.load_manager("data")

        # Update user data
        self.clear_user_form_data(bot, chat_id)

        form_id = chat_id
        data_manager.create_data("forms", form_id, module="forms")

        # Show form to user
        steps = self.load_form_steps(form_name)

        first_step = steps["meta"]["first_step"]

        form_data = data_manager.load_data("forms", form_id, module="forms")

        form_data["form_name"] = form_name
        form_data["current_step"] = first_step
        form_data["form_meta"] = form_meta

        # Set default entries
        if "default_entries" in steps["meta"].keys():
            default_entries = steps["meta"]["default_entries"]

            for entry in default_entries.keys():
                form_data["form_entries"][entry] = default_entries[entry]

        data_manager.save_data("forms", form_id, form_data, module="forms")

        self.show_current_step(bot, chat_id)

    def set_next_step(self, bot, chat_id, message_id, next_step=None):
        data_manager = ModulesLoader.load_manager("data")

        form_id = chat_id

        form_data = data_manager.load_data("forms", form_id, module="forms")
        form_name = form_data["form_name"]
        form_steps = self.load_form_steps(form_name)

        current_step_data = form_steps[form_data["current_step"]]

        # Delete previous message if 'clear' is true
        if "clear" in current_step_data and current_step_data["clear"]:
            bot.deleteMessage(
                chat_id = chat_id,
                message_id = message_id
            )

        if next_step == None:
            next_step = current_step_data["next_step"]

        logging.info("Showing next step to {} ({} {})".format(chat_id, form_id, next_step))

        if next_step and next_step != "None":
            if next_step == "_RESET":
                self.clear_user_form_data(bot, chat_id, False)
                return 

            form_data["current_step"] = next_step
            data_manager.save_data("forms", form_id, form_data, module="forms")
            self.show_current_step(bot, chat_id)
        else:
            if "void" in form_steps["meta"] and form_steps["meta"]["void"]:
                return

            self.digest_form(bot, chat_id, form_id)

    def digest_form(self, bot, chat_id, form_id):
        logging.info("Digesting form for {}".format(chat_id))

        data_manager = ModulesLoader.load_manager("data")

        # Load form's data 
        form_data = data_manager.load_data("forms", form_id, module="forms")
        form_name = form_data["form_name"]

        # Update digestion flag
        form_data["digested"] = True
        data_manager.save_data("forms", form_id, form_data, module="forms")

        # Digest the form
        digester = self.digesters[form_name]
        digester(bot, chat_id, form_data["form_entries"], form_data["form_meta"])

    def format_step_text(self, step_text, form_entries):
        for key in form_entries.keys():
            key_expression = "[{}]".format(key)
            step_text = step_text.replace(key_expression, str(form_entries[key]).replace("_", "\\_"))

        return step_text

    def append_jump_button(self, menu_layout, text, step_id):
        menu_layout.append([InlineKeyboardButton(text, callback_data="forms,jump,{}".format(step_id))])

    def fixed_reply_reply_markup(self, options, form_data, current_step_data):
        form_name = form_data["form_name"]
        step_name = form_data["current_step"]

        menu_layout = []

        for options_row in options:
            row = []

            for option in options_row:
                action = ""

                if "action" in option.keys():
                    action = option["action"]

                button_data = "forms,fixed_reply,{},{}".format(action, option["output_data"])

                row.append(InlineKeyboardButton(option["text"], callback_data=button_data))

            menu_layout.append(row)

        if "previous_step" in current_step_data.keys():
            self.append_jump_button(menu_layout, "Back", current_step_data["previous_step"])

        reply_markup = InlineKeyboardMarkup(menu_layout)

        return reply_markup

    def keyboard_reply_reply_markup(self, options, form_data, current_step_data):
        form_name = form_data["form_name"]
        step_name = form_data["current_step"]

        menu_layout = []

        for options_row in options:
            row = []

            for option in options_row:
                row.append(KeyboardButton(option["text"]))

            menu_layout.append(row)

        reply_markup = ReplyKeyboardMarkup(menu_layout, resize_keyboard=True, one_time_keyboard=True)

        return reply_markup

    def checkbox_list_reply_markup(self, entries, form_data, current_step_data):
        form_name = form_data["form_name"]
        step_name = form_data["current_step"]
        step_output = current_step_data["output"]

        # Add entries
        menu_layout = []

        for entries_row in entries:
            row = []

            for entry in entries_row:
                text = entry["text"]
                data = entry["data"]

                checked = data in form_data["form_entries"][step_output]

                button_data = "forms,checkbox_click,{},{}".format(data, step_output)

                emoji = "✅" if checked else ""

                row.append(InlineKeyboardButton("{} {}".format(text, emoji), callback_data=button_data))

            menu_layout.append(row)

        # Check if the step requires a back button
        if "previous_step" in current_step_data.keys():
            self.append_jump_button(menu_layout, "Back", current_step_data["previous_step"])

        # Add 'Confirm' button
        self.append_jump_button(menu_layout, "Confirm", current_step_data["confirm_step"])

        reply_markup = InlineKeyboardMarkup(menu_layout)

        return reply_markup

    def show_current_step(self, bot, chat_id, message_id=None):
        data_manager = ModulesLoader.load_manager("data")

        form_id = chat_id

        form_data = data_manager.load_data("forms", form_id, module="forms")
        form_name = form_data["form_name"]
        form_steps = self.load_form_steps(form_name)

        step_name = form_data["current_step"]
        current_step_data = form_steps[step_name]


        if "externs" in current_step_data.keys():
            externs = current_step_data["externs"]

            for extern_key in externs.keys():
                extern_data = form_data["form_meta"][externs[extern_key]]

                current_step_data[extern_key] = extern_data

        reply_markup = None
        next_step = "__NULL"

        # Message 
        if current_step_data["type"] == "message":
            step_text = current_step_data["text"]

            if "format" in current_step_data.keys() and current_step_data["format"]:
                form_entries = form_data["form_entries"]
                step_text = self.format_step_text(step_text, form_entries)

            # Check if the step requires a back button
            if "previous_step" in current_step_data.keys():
                menu_layout = []
                self.append_jump_button(menu_layout, "Back", current_step_data["previous_step"])
                reply_markup = InlineKeyboardMarkup(menu_layout)

            next_step = current_step_data["next_step"]

        # Text or image field
        if (current_step_data["type"] == "text_field" or
            current_step_data["type"] == "image_field" or
            current_step_data["type"] == "video_field" or
            current_step_data["type"] == "animation_field"):
            step_text = current_step_data["text"]

            if "format" in current_step_data.keys() and current_step_data["format"]:
                form_entries = form_data["form_entries"]
                step_text = self.format_step_text(step_text, form_entries)

            reply_markup = None

            # Check if the step requires a back button
            if "previous_step" in current_step_data.keys():
                menu_layout = []
                self.append_jump_button(menu_layout, "Back", current_step_data["previous_step"])
                reply_markup = InlineKeyboardMarkup(menu_layout)

        # Fixed reply
        if current_step_data["type"] == "fixed_reply":
            # Format step text (if necessary)
            step_text = current_step_data["text"]

            if "format" in current_step_data.keys() and current_step_data["format"]:
                form_entries = form_data["form_entries"]
                step_text = self.format_step_text(step_text, form_entries)

            options = current_step_data["options"]
            reply_markup = self.fixed_reply_reply_markup(options, form_data, current_step_data)

        # Keyboard reply
        if current_step_data["type"] == "keyboard_reply":
            # Format step text (if necessary)
            step_text = current_step_data["text"]

            if "format" in current_step_data.keys() and current_step_data["format"]:
                form_entries = form_data["form_entries"]
                step_text = self.format_step_text(step_text, form_entries)

            options = current_step_data["options"]
            reply_markup = self.keyboard_reply_reply_markup(options, form_data, current_step_data)

        # Checkbox list 
        if current_step_data["type"] == "checkbox_list":
            step_text = current_step_data["text"]
            step_output = current_step_data["output"]

            if "format" in current_step_data.keys() and current_step_data["format"]:
                form_entries = form_data["form_entries"]
                step_text = self.format_step_text(step_text, form_entries)

            if step_output not in form_data["form_entries"].keys():
                form_data["form_entries"][step_output] = []
                data_manager.save_data("forms", form_id, form_data, module="forms")

            entries = current_step_data["entries"]
            reply_markup = self.checkbox_list_reply_markup(entries, form_data, current_step_data)

        # Replace macros in meta
        for meta in form_data["form_meta"].keys():
            macro = "[{}]".format(meta)

            step_text = step_text.replace(macro, str(form_data["form_meta"][meta]))

        # Disable web page preview option
        disable_web_page_preview = True
        if "disable_web_page_preview" in current_step_data.keys() and current_step_data["disable_web_page_preview"]:
            disable_web_page_preview = current_step_data["disable_web_page_preview"]

        # Send or edit message
        if message_id:
            bot.editMessageText(
                chat_id=chat_id,
                message_id=message_id,
                text=step_text,
                parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup = reply_markup,
                disable_web_page_preview = disable_web_page_preview
            )
        else:
            # Load media data (if any)
            media_data = None
            if "media" in current_step_data.keys() and current_step_data["media"]:
                media_data = current_step_data["media"]

                for meta in form_data["form_meta"].keys():
                    macro = "[{}]".format(meta)

                    media_data["type"] = media_data["type"].replace(macro, str(form_data["form_meta"][meta]))
                    media_data["path"] = media_data["path"].replace(macro, str(form_data["form_meta"][meta]))

                if "format" in current_step_data.keys() and current_step_data["format"]:
                    for key in form_data["form_entries"].keys():
                        macro = "[{}]".format(key)

                        media_data["type"] = media_data["type"].replace(macro, str(form_data["form_entries"][key]))
                        media_data["path"] = media_data["path"].replace(macro, str(form_data["form_entries"][key]))

            # Send complete message
            if not media_data:
                sent_message = bot.sendMessage(
                    chat_id=chat_id,
                    text=step_text,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    reply_markup = reply_markup,
                    disable_web_page_preview = disable_web_page_preview
                )
            else:
                if media_data["type"] == "photo":
                    sent_message = bot.sendPhoto(
                        chat_id=chat_id,
                        caption=step_text,
                        photo=media_data["path"],
                        parse_mode=telegram.ParseMode.MARKDOWN,
                        reply_markup = reply_markup,
                        disable_web_page_preview = disable_web_page_preview
                    )
                elif media_data["type"] == "video":
                    sent_message = bot.sendVideo(
                        chat_id=chat_id,
                        caption=step_text,
                        video=media_data["path"],
                        parse_mode=telegram.ParseMode.MARKDOWN,
                        reply_markup = reply_markup,
                        disable_web_page_preview = disable_web_page_preview
                    )
                else:
                    logging.exception("Unknown media type")

            # Add new message IDs
            if data_manager.has_data("forms",form_id):
                form_data = data_manager.load_data("forms", form_id, module="forms")
                form_data["messages"].append(sent_message.message_id)
                data_manager.save_data("forms", form_id, form_data, module="forms")

        if next_step is not "__NULL":
            self.set_next_step(bot, chat_id, sent_message.message_id, next_step = next_step)

    def handle_input(self, bot, chat_id, message_id, form_name, step_name, input_data):
        logging.info("Handling input of {} on form {} (step name = {}, input data = {})".format(chat_id, form_name, step_name, input_data))

        data_manager = ModulesLoader.load_manager("data")

        next_step_name = None

        # Check if it's an action input
        if "action" in input_data.keys() and len(input_data["action"]) > 0:
            actions = input_data["action"].split(";")

            if actions[0] == "jump":
                next_step_name = actions[1]

        form_steps = self.load_form_steps(form_name)
        step_data = form_steps[step_name]

        if "output" in step_data.keys():
            if step_data["type"] == "text_field":
                step_output = input_data["text"]

            elif step_data["type"] == "fixed_reply":
                step_output = input_data["output_data"]

            elif step_data["type"] == "keyboard_reply":
                step_output = input_data["value"]

            elif step_data["type"] == "image_field":
                step_output = input_data["image_id"]

                if step_data["save_in_cache"]:
                    cache_manager = ModulesLoader.load_manager("cache")
                    cache_manager.download_image(input_data["image_id"], input_data["image_url"])

            elif step_data["type"] == "video_field":
                step_output = input_data["video_id"]

                if step_data["save_in_cache"]:
                    cache_manager = ModulesLoader.load_manager("cache")
                    cache_manager.download_video(input_data["video_id"], input_data["video_url"])

            elif step_data["type"] == "animation_field":
                step_output = input_data["animation_id"]

                if step_data["save_in_cache"]:
                    cache_manager = ModulesLoader.load_manager("cache")
                    cache_manager.download_animation(input_data["animation_id"], input_data["animation_url"])

            current_user_form_id = chat_id
            form_data = data_manager.load_data("forms", current_user_form_id, module="forms")
            form_data["form_entries"][step_data["output"]] = step_output
            data_manager.save_data("forms", current_user_form_id, form_data, module="forms")

        self.set_next_step(bot, chat_id, message_id, next_step=next_step_name)

    def load_form_steps(self, form_name, lang=None):
        module_folder = ModulesLoader.get_module_content_folder("forms")

        if not lang:
            config_manager = ModulesLoader.load_manager("config")
            lang_settings = config_manager.load_settings_file("forms", "lang")
            lang = lang_settings["default"]

        return yaml.safe_load(open("{}/formats/{}/{}/steps.yaml".format(module_folder, lang, form_name), "r", encoding="utf8"))
