import telegram, logging

from modules.pytg.ModulesLoader import ModulesLoader

# Form digesters
from .digesters.forms.send_photo import send_photo_digester


def load_digesters():
    # Form digesters
    forms_manager = ModulesLoader.load_manager("forms")

    forms_manager.add_digester("send_photo", send_photo_digester)


def initialize():
    logging.info("Initializing indoor_compass_digesters module...")
    pass

def connect():
    logging.info("Connecting indoor_compass_digesters module...")

    load_digesters()

def load_manager():
    # There is no need for a manager in this package
    return None

def depends_on():
    return ["bot", "forms"]