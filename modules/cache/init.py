import logging

from modules.cache.CacheManager import CacheManager

def initialize():
    logging.info("Initializing cache module...")

    CacheManager.initialize()

def connect():
    pass

def load_manager():
    return CacheManager.load()

def depends_on():
    return []