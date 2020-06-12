import logging

from modules.data.DataManager import DataManager

def initialize():
    logging.info("Initializing data module...")

    DataManager.initialize()

def connect():
    pass

def load_manager():
    return DataManager.load()

def depends_on():
    return []