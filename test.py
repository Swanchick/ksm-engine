from user import UserManager


user_manager = UserManager()
user_manager.start()

user = user_manager.get_users_by_id(1)

print(user.is_administrator)