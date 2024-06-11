from user.user_manager_abstract import AbstractUserManager
from settings.settings_creator import SettingsCreator
from cryptography.fernet import Fernet


class InitProject:
    __user_manager: AbstractUserManager
    __settings: SettingsCreator

    def __init__(self, user_manager: AbstractUserManager):
        self.__user_manager = user_manager
        self.__setting = SettingsCreator()

    def __user(self):
        print("Creating new user")
        username = input("Username: ")
        password = input("Password: ")
        administrator_str = input("Administrator (y/n) by default (n): ")
        administrator = True if administrator_str == "y" else False

        user = self.__user_manager.create_user(username, password, administrator)
        if user is None:
            print("Something went wrong!")

        print("User created successfully")

    def __engine(self):
        settings_data = self.__setting.data()

        print("Setting up engine")
        engine_name = input("Engine engine name (By default \"Engine\"): ")
        if engine_name == "":
            engine_name = "Engine"

        engine_password = input("Password (by default \"12345678_S3cure_p4$$w0rD\"): ")
        if engine_password == "":
            engine_password = "12345678_S3cure_p4$$w0rD"

        engine_host = input("Engine host (By default \"127.0.0.1\"): ")
        if engine_host == "":
            engine_host = "127.0.0.1"

        engine_port = input("Engine port (By default 52146): ")
        if engine_port == "":
            engine_port = 52146
        else:
            engine_port = int(engine_port)

        engine_instance_folder = input("Engine instance folder (By default \"/home/root/ksm-instances/\"): ")
        if engine_instance_folder == "":
            engine_instance_folder = "/home/root/ksm-instances/"

        settings_data["engine"]["name"] = engine_name
        settings_data["engine"]["password"] = engine_password
        settings_data["engine"]["ip"] = engine_host
        settings_data["engine"]["port"] = engine_port
        settings_data["engine"]["server_instances_folder"] = engine_instance_folder
        settings_data["engine"]["secret_key"] = Fernet.generate_key().decode("utf-8")

        self.__setting.save(settings_data)

        print("All settings you can change in ksm-engine/settings.json")

    def start(self):
        while True:
            print("Choose an option:")
            print("1. Create a new user")
            print("2. Setup an engine")
            print("3. Setup a database")
            print("Press enter if you want exit")

            option = input("Option: ")

            if option == "1":
                self.__user()
            elif option == "2":
                self.__engine()
            else:
                break
