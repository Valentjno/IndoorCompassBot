import yaml, os

import urllib.request

from modules.pytg.Manager import Manager
from modules.pytg.ModulesLoader import ModulesLoader

class CacheManager(Manager):
    @staticmethod
    def initialize():
        CacheManager.__instance = CacheManager()

        return

    @staticmethod
    def load():
        return CacheManager.__instance

    def load_cache(self):
        module_folder = ModulesLoader.get_module_content_folder("cache")

        return yaml.safe_load(open("{}/cache.yaml".format(module_folder), "r"))

    def save_cache(self, cache):
        module_folder = ModulesLoader.get_module_content_folder("cache")

        yaml.safe_dump(cache, open("{}/cache.yaml".format(module_folder), "w"))

    # Media (general)
    def download_media(self, media_id, media_url, folder="uncategorized"):
        module_folder = ModulesLoader.get_module_content_folder("cache")

        media_data = urllib.request.urlopen(media_url).read()

        with open("{}/{}/{}".format(module_folder, folder, media_id), "wb") as media_file:
            media_file.write(media_data)

        return media_data

    def load_media(self, media_id, folder="uncategorized"):
        module_folder = ModulesLoader.get_module_content_folder("cache")

        return open("{}/{}/{}".format(module_folder, folder, media_id), "rb")

    # Images
    def download_image(self, image_id, image_url):
        self.download_media(image_id, image_url, "images")

    def load_image(self, image_id):
        self.load_media(image_id, "images")

    # Videos
    def download_video(self, video_id, video_url):
        self.download_media(video_id, video_url, "videos")

    def load_video(self, video_id):
        self.load_media(video_id, "videos")

    # Animations
    def download_animation(self, animation_id, animation_url):
        self.download_media(animation_id, animation_url, "animations")

    def load_animation(self, animation_id):
        self.load_media(animation_id, "animations")