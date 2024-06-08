from utils.repo_downloader import RepoDownloader
from settings.settings_creator import SettingsCreator
from os import mkdir
from os.path import isdir
from enum import Enum


class LoadState(Enum):
    SUCCESS = 0
    FOLDER_ALREADY_EXISTS = 1


class InstanceLoader:
    __name: str
    __instance_type: str
    __repo_url: str
    __instance_folder: str

    def __init__(self, instance_folder: str, name: str):
        self.__name = name
        self.__instance_folder = instance_folder

    def load(self) -> LoadState:
        path = f"{self.__instance_folder}{self.__name}/"

        try:
            mkdir(path)
        except FileExistsError:
            return LoadState.SUCCESS

        return LoadState.SUCCESS
