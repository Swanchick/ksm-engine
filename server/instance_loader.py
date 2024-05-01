from utils import RepoDownloader
from settings import SettingsCreator


INSTANCE_PACKAGES = "instance_packages"


class InstanceLoader:
    __name: str
    __instance_type: str
    __repo_url: str
    __instance_folder: str

    def __init__(self, instance_folder: str, name: str, instance_type: str):
        self.__name = name
        self.__instance_type = instance_type
        self.__instance_folder = instance_folder

    def start(self) -> bool:
        settings_creator = SettingsCreator()
        data = settings_creator.data()
        if INSTANCE_PACKAGES not in data:
            return False

        instance_packages = data[INSTANCE_PACKAGES]
        if self.__instance_type not in instance_packages:
            return False

        self.__repo_url = instance_packages[self.__instance_type]

        return True

    def load(self):
        path = f"{self.__instance_folder}{self.__name}/"

        repo_downloader = RepoDownloader(self.__repo_url, path)
        repo_downloader.download()
