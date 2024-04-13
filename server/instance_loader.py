from utils import RepoDownloader
from settings import SettingsCreator


INSTANCE_LOADER = "instance_packages"


class InstanceLoader:
    __name: str
    __repo_url: str
    __instance_folder: str

    def __init__(self, instance_folder: str, name: str, instance_type: str):
        self.__name = name
        self.__instance_folder = instance_folder

        settings_creator = SettingsCreator()
        data = settings_creator.data()
        if INSTANCE_LOADER not in data:
            return

        data = data[INSTANCE_LOADER]
        if instance_type not in data:
            return

        self.__repo_url = data[instance_type]

    def load(self):
        path = f"{self.__instance_folder}{self.__name}/"

        repo_downloader = RepoDownloader(self.__repo_url, path)
        repo_downloader.download()
