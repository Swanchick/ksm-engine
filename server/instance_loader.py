from utils import RepoDownloader
from settings import SettingsCreator
from engine import EngineSettings


INSTANCE_LOADER = "instance_packages"


class InstanceLoader:
    __name: str
    __repo_url: str
    __engine_settings: EngineSettings

    def __init__(self, name: str, instance_type: str):
        self.__name = name

        settings_creator = SettingsCreator()
        data = settings_creator.data()
        if INSTANCE_LOADER not in data:
            return

        data = data[INSTANCE_LOADER]
        if instance_type not in data:
            return

        self.__repo_url = data[instance_type]

        self.__engine_settings = SettingsCreator().settings("engine")

    def load(self):
        path = f"{self.__engine_settings.instance_folder}{self.__name}/"

        repo_downloader = RepoDownloader(self.__repo_url, path)
        repo_downloader.download()
