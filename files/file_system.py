from typing import Tuple, Optional
from os.path import isfile, exists, isdir
from os import remove as os_remove


class FileSystem:
    __instance_folder: str

    def __init__(self, folder: str):
        self.__instance_folder = folder

    def __build_path(self, file_name: str, path: Tuple[str, ...] = "") -> str:
        return self.__instance_folder + "/".join(path) + "/" + file_name

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
        if not isfile(path):
            return

        with open(path, "r") as f:
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
