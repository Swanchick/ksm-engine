from utils import RepoDownloader
from settings import SettingsCreator
from engine import EngineSettings


INSTANCE_LOADER = "instance_packages"


class InstanceLoader:
    __name: str
    __repo_url: str
    __engine_settings: EngineSettings

    def __init__(self, name: str, type_of_server: str):
        self.__name = name

        settings_creator = SettingsCreator()
        data = settings_creator.data()
        if INSTANCE_LOADER not in data:
            return

        data = data[INSTANCE_LOADER]
        if type_of_server not in data:
            return

        self.__repo_url = data[type_of_server]

        self.__engine_settings = SettingsCreator().settings("engine")

    def load(self):
        print(self.__repo_url)
        path = f"{self.__engine_settings.instance_folder}{self.__name}/"
        print(path)
        repo_downloader = RepoDownloader(self.__repo_url, path)
        repo_downloader.download()
