import yaml, os

from modules.pytg.Manager import Manager

from modules.pytg.ModulesLoader import ModulesLoader

class DataManager(Manager):
    @staticmethod
    def initialize():
        DataManager.__instance = DataManager()

        return

    @staticmethod
    def load():
        return DataManager.__instance

    ######################
    # Database interface #
    ######################

    def create_data(self, table, object_id, module="data"):
        return self.save_data(table, object_id, self.load_data(table, "__default", module=module), module)

    def load_data(self, table, object_id, module="data"):
        module_folder = ModulesLoader.get_module_content_folder(module)

        return yaml.safe_load(open("{}/data/{}/{}.yaml".format(module_folder, table, object_id), "r"))

    def save_data(self, table, object_id, data, module="data"):
        module_folder = ModulesLoader.get_module_content_folder(module)

        yaml.safe_dump(data, open("{}/data/{}/{}.yaml".format(module_folder, table, object_id), "w"))

        return data

    def delete_data(self, table, object_id, module="data"):
        module_folder = ModulesLoader.get_module_content_folder(module)

        os.remove("{}/data/{}/{}.yaml".format(module_folder, table, object_id))

    def has_data(self, table, object_id, module="data"):
        module_folder = ModulesLoader.get_module_content_folder(module)

        return os.path.exists("{}/data/{}/{}.yaml".format(module_folder, table, object_id))

    def load_table_entries(self, table, module="data"):
        module_folder = ModulesLoader.get_module_content_folder(module)

        entries = []

        files = os.listdir("{}/data/{}".format(module_folder, table))
        files.remove("__default.yaml")

        for f in files:
            entry_id = f.replace(".yaml", "")

            data = self.load_data(table, entry_id)

            entries.append(data)

        return entries

    def find_entry_by_field(self, table, field, value, module="data"):
        module_folder = ModulesLoader.get_module_content_folder(module)

        files = os.listdir("{}/data/{}".format(module_folder, table))
        files.remove("__default.yaml")

        for f in files:
            entry_id = f.replace(".yaml", "")

            data = self.load_data(table, entry_id)

            if data[field] == value:
                return data

        return None

