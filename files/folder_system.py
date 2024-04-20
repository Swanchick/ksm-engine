from typing import Tuple, Optional, List, Dict
from os import listdir as os_listdir
from os.path import isfile, isdir
from .file_unit import FileUnit
from .file_type import FileType
from os import remove as os_remove
from os import mkdir as os_mkdir


class FolderSystem:
    __start_folder: str

    def __init__(self, start_folder: str):
        self.__start_folder = start_folder

    def __build_path(self, folder_path: Tuple[str, ...]) -> str:
        return self.__start_folder + "/".join(folder_path) + "/"

    def __is_dir_exist(self, folder_path: Tuple[str, ...]) -> bool:
        return isdir(self.__build_path(folder_path))

    @staticmethod
    def __check_folders_access(folder_path: Tuple[str, ...]) -> bool:
        for folder in folder_path:
            if folder == ".." or folder == ".":
                return False

        return True

    def open_folder(self, *folder_path: str) -> Optional[List[Dict]]:
        if not self.__check_folders_access(folder_path):
            return

        if not self.__is_dir_exist(folder_path):
            return

        path = self.__build_path(folder_path)

        files = os_listdir(path)
        files_out = []

        for file in files:
            current_path = path + file

            if isfile(current_path):
                files_out.append(FileUnit(current_path, FileType.FILE).dict)
            elif isdir(current_path):
                files_out.append(FileUnit(current_path, FileType.FOLDER).dict)

        files_out.sort(key=lambda x: x["file_type"] == FileType.FOLDER.value)

        return files_out

    def create_folder(self, *folder_path: str) -> None:
        if not self.__check_folders_access(folder_path):
            return

        if self.__is_dir_exist(folder_path):
            return

        path = self.__build_path(folder_path)
        os_mkdir(path)

    def delete_folder(self, *folder_path: str):
        if not self.__check_folders_access(folder_path):
            return

        if not self.__is_dir_exist(folder_path):
            return

        path = self.__build_path(folder_path)
        if isfile(path):
            return

        os_remove(path)
