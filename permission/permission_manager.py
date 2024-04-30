from database_utils import Database
from user import UserManager, user_manager
from permission.permissions import Permissions
from typing import List, Optional, Dict
from .saved_permission import SavedPermission


class PermissionManager(Database):
    __user_manager: UserManager
    __saved_permissions: List[SavedPermission]

    def start(self):
        self.__saved_permissions = []

        self._connector = self._connect("ksm_database")
        self._cursor = self._connector.cursor()

        self._cursor.execute("CREATE TABLE IF NOT EXISTS permissions (user_id INTEGER,"
                             "instance_id INTEGER NOT NULL,"
                             "permission INTEGER DEFAULT 0)")

    def __row_exists(self, user_id: int, instance_id: int) -> bool:
        self._cursor.execute("SELECT COUNT(*) FROM permissions WHERE user_id = %s AND instance_id = %s",
                             (user_id, instance_id))

        result = self._cursor.fetchone()
        return result[0] > 0

    def __new_permission(self, user_id: int, instance_id: int):
        self._cursor.execute("INSERT INTO permissions (user_id, instance_id) VALUES (%s, %s)", (user_id, instance_id))

        self._connector.commit()

    def __update_permission(self, user_id: int, instance_id: int, permission: int):
        self._cursor.execute("UPDATE permissions SET permission = %s WHERE user_id = %s AND instance_id = %s",
                             (permission, user_id, instance_id))

        self._connector.commit()

    def __get_permission(self, user_id: int, instance_id: int):
        self._cursor.execute("SELECT permission FROM permissions WHERE user_id = %s AND instance_id = %s",
                             (user_id, instance_id))

        result = self._cursor.fetchone()
        if result is None:
            return

        return result[0]

    @classmethod
    def __break_into_permissions(cls, number) -> List[int]:
        out = []
        current_power = 1

        while number > 0:
            if number % 2 == 1:
                out.append(current_power)
            number //= 2
            current_power *= 2

        return out

    @classmethod
    def __get_permission_type(cls, value: int) -> Permissions:
        for permission in Permissions:
            if permission.value == value:
                return permission

    @classmethod
    def __permission_exists(cls, value: int):
        return cls.__get_permission_type(value) is not None

    def __check_permission(self, permission: int, permission_to_check: int) -> bool:
        permissions = self.__break_into_permissions(permission)

        print(permissions)

        return permission_to_check in permissions

    def load_user_manager(self, user_manager: UserManager):
        self.__user_manager = user_manager

    def __get_saved_permission(self, user_id: int, instance_id: int) -> Optional[SavedPermission]:
        for saved_permission in self.__saved_permissions:
            if saved_permission.user_id == user_id and saved_permission.instance_id == instance_id:
                return saved_permission

        return None

    def __is_saved_permission_exists(self, user_id: int, instance_id: int) -> bool:
        saved_permission = self.__get_saved_permission(user_id, instance_id)

        return saved_permission is not None

    def __delete_saved_permission(self, user_id: int, instance_id: int):
        if not self.__is_saved_permission_exists(user_id, instance_id):
            return

        for index, saved_permission in enumerate(self.__saved_permissions):
            if saved_permission.user_id == user_id and saved_permission.instance_id == instance_id:
                print(saved_permission)

                self.__saved_permissions.pop(index)

                break

    def check_permission(self, user_id: int, instance_id: int, permission_type: Permissions) -> bool:
        if self.__is_saved_permission_exists(user_id, instance_id):
            saved_permission = self.__get_saved_permission(user_id, instance_id)

            if saved_permission.is_administrator:
                return True

            if self.__check_permission(saved_permission.permission, permission_type.value):
                return True

            return False

        if not (self._connector and self._cursor):
            return False

        user = self.__user_manager.get_user_by_id(user_id)

        if user is None:
            return False

        if user.is_administrator:
            saved_permission = SavedPermission(user_id, instance_id, is_administrator=True)
            self.__saved_permissions.append(saved_permission)

            return True

        if not self.__row_exists(user_id, instance_id):
            return False

        permission = self.__get_permission(user_id, instance_id)
        if permission is None:
            return False

        if self.__check_permission(permission, permission_type.value):
            saved_permission = SavedPermission(user_id, instance_id, permission=permission)
            self.__saved_permissions.append(saved_permission)

            return True

        return False

    def get_all_permissions_from_instance(self, instance_id: int) -> Optional[List[Dict]]:
        if not (self._connector and self._cursor):
            return

        self._cursor.execute("SELECT * "
                             "FROM permissions "
                             "WHERE instance_id = %s",
                             (instance_id, ))

        data = self._cursor.fetchall()
        output_data = []

        for permissions in data:
            broken_permission = self.__break_into_permissions(permissions[2])
            user_id = permissions[0]
            user = self.__user_manager.get_user_by_id(user_id)
            permission_out = []

            for permission in broken_permission:
                permission_type = self.__get_permission_type(permission)
                if permission_type is None:
                    continue

                permission_out.append({permission_type.name: permission})

            output_data.append({'user': user.dict, "permissions": permission_out})

        return output_data

    def add_permission(self, user_id: int, instance_id: int, permission_to_check: int):
        if not self.__permission_exists(permission_to_check):
            return

        if not (self._connector and self._cursor):
            return

        print(self.__saved_permissions)

        self.__delete_saved_permission(user_id, instance_id)

        print(self.__saved_permissions)

        if not self.__row_exists(user_id, instance_id):
            self.__new_permission(user_id, instance_id)

        permission = self.__get_permission(user_id, instance_id)
        if permission is None:
            return

        if self.__check_permission(permission, permission_to_check):
            return

        permission += permission_to_check
        self.__update_permission(user_id, instance_id, permission)

    def remove_permission(self, user_id: int, instance_id: int, permission_to_check: int):
        if not self.__permission_exists(permission_to_check):
            return

        if not (self._connector and self._cursor):
            return

        print("User id " + user_id)
        print("Instance " + instance_id)

        print(self.__saved_permissions)

        self.__delete_saved_permission(user_id, instance_id)

        print(self.__saved_permissions)

        if not self.__row_exists(user_id, instance_id):
            self.__new_permission(user_id, instance_id)

        permission = self.__get_permission(user_id, instance_id)
        if permission is None:
            return

        if not self.__check_permission(permission, permission_to_check):
            return

        permission -= permission_to_check
        self.__update_permission(user_id, instance_id, permission)
