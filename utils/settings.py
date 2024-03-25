from utils.yaml_reader import YamlReader


class SettingsManager:
    @staticmethod
    def get_database():
        reader = YamlReader('config')

