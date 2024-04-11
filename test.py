from settings import SettingsCreator


settings = SettingsCreator("settings.json").settings("database")

print(settings)