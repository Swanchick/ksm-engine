from abstract import AbstractUserManager
from typing import Dict


class InitProject:
    __user_manager: AbstractUserManager
    __settings_data: Dict

    def __init__(self, user_manager: AbstractUserManager):
        self.__user_manager = user_manager

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

    def start(self):
        self.__user()

