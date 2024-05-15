from json import load, dump
from os.path import exists


class JsonReader:
    __file_name: str

    def __init__(self, file_name: str):
        if not exists(file_name):
            raise FileNotFoundError()

        self.__file_name = file_name

    def read(self) -> dict:
        with open(self.__file_name, 'r') as f:
            data = load(f)

            return data

    def write(self, data: dict):
        with open(self.__file_name, 'w') as f:
            dump(data, f, indent=4)
            f.close()
