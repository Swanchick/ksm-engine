from typing import Tuple, Optional
from os.path import isfile, exists, isdir
from os import remove as os_remove
from base64 import b64decode, b64encode


class FileSystem:
    __instance_folder: str

    def __init__(self, folder: str):
        self.__instance_folder = folder

    def __build_path(self, file_name: str, path: Tuple[str, ...] = "") -> str:
        full_path = ""

        for f in path:
            if f == "":
                continue

            full_path += f"/{f}"

        return self.__instance_folder + full_path[1:] + "/" + file_name

    @staticmethod
    def __check_folders_access(path: Tuple[str, ...]) -> bool:
        for folder in path:
            if folder == ".." or folder == ".":
                return False

        return True

    def open_file(self, file_name: str, *folders: str) -> Optional[str]:
        if not self.__check_folders_access(folders):
            return

        path = self.__build_path(file_name, folders)
        print(path)

        if not isfile(path):
            return

        with open(path, "r") as f:
            return f.read()

    def read_bytes(self, file_name: str, *folders: str) -> Optional[bytes]:
        if not self.__check_folders_access(folders):
            return

        path = self.__build_path(file_name, folders)
        print(path)

        if not isfile(path):
            return

        with open(path, "rb") as f:
            return f.read()

    def write_file(self, file_name: str, data: str, *folders: str):
        if not self.__check_folders_access(folders):
            return

        path = self.__build_path(file_name, folders)
        if not isfile(path):
            return

        with open(path, "w") as f:
            f.write(data)
            f.close()

    def create_file(self, file_name: str, *folders: str):
        path = self.__build_path(file_name, folders)
        if exists(path):
            return

        with open(path, "w") as f:
            f.write("")
            f.close()

    def delete_file(self, file_name: str, *folders: str):
        if not self.__check_folders_access(folders):
            return

        path = self.__build_path(file_name, folders)
        if not exists(path):
            return

        if isdir(path):
            return

        os_remove(path)

    def receive_file_bs64(self, file_name: str, data: str, *folders: str):
        if not self.__check_folders_access(folders):
            return

        decode_data = b64decode(data)

        path = self.__build_path(file_name, folders)
        with open(path, "wb") as f:
            f.write(decode_data)
            f.close()

    def send_file_bs64(self, file_name: str, *folders: str) -> Optional[Tuple[str, str]]:
        data = self.read_bytes(file_name, *folders)
        if data is None:
            return

        encoded_data = b64encode(data).decode("utf-8")

        return file_name, encoded_data
