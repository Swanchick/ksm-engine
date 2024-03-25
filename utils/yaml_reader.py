from yaml import safe_load
from os.path import exists


class YamlReader:
    __file_name: str

    def __init__(self, file_name: str):
        if not exists(file_name):
            raise FileNotFoundError()

        self.__file_name = file_name

    def read(self, type_of_settings: str) -> dict:
        with open(self.__file_name, 'r') as f:
            data = safe_load(f)
            if type_of_settings not in data:
                return {}

            return data[type_of_settings]
