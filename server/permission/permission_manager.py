from database_utils.database import Database
from user.user import User
from server.permission.permissions import Permissions
from typing import List, Optional, Dict
from .saved_permission import SavedPermission


class PermissionManager(Database):
    __saved_permissions: List[SavedPermission]

    def __init__(self):
        super().__init__()

        self.start()

    def start(self):
        self.__saved_permissions = []

        self._execute(
            "CREATE TABLE IF NOT EXISTS permissions ("
            "user_id INTEGER,"
            "instance_id INTEGER,"
            "permission INTEGER DEFAULT 0,"
            "FOREIGN KEY (user_id) REFERENCES users(user_id),"
            "FOREIGN KEY (instance_id) REFERENCES instances(instance_id)"
            ")"
        )

    def __row_exists(self, user_id: int, instance_id: int) -> bool:
        self._execute("SELECT COUNT(*) FROM permissions WHERE user_id = %s AND instance_id = %s",
                      (user_id, instance_id)
                      )

        result = self._fetchone()
        return result[0] > 0

    def __new_permission(self, user_id: int, instance_id: int):
        self._execute("INSERT INTO permissions (user_id, instance_id) VALUES (%s, %s)", (user_id, instance_id))

        self._commit()

    def __update_permission(self, user_id: int, instance_id: int, permission: int):
        self._execute(
            "UPDATE permissions SET permission = %s WHERE user_id = %s AND instance_id = %s",
            (permission, user_id, instance_id)
        )

        self._commit()

    def __get_permission(self, user_id: int, instance_id: int):
        self._execute("SELECT permission FROM permissions WHERE user_id = %s AND instance_id = %s",
                      (user_id, instance_id)
                      )

        result = self._fetchone()
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

        return permission_to_check in permissions

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
                self.__saved_permissions.pop(index)

                break

    def check_permission(self, user: User, instance_id: int, permission_type: Permissions) -> bool:
        if user is None:
            return False

        if self.__is_saved_permission_exists(user.user_id, instance_id):
            saved_permission = self.__get_saved_permission(user.user_id, instance_id)

            if saved_permission.is_administrator:
                return True

            if self.__check_permission(saved_permission.permission, permission_type.value):
                return True

            return False

        if not (self._connector and self._cursor):
            return False

        if user.is_administrator:
            saved_permission = SavedPermission(user.user_id, instance_id, is_administrator=True)
            self.__saved_permissions.append(saved_permission)

            return True

        if not self.__row_exists(user.user_id, instance_id):
            return False

        permission = self.__get_permission(user.user_id, instance_id)
        if permission is None:
            return False

        if self.__check_permission(permission, permission_type.value):
            saved_permission = SavedPermission(user.user_id, instance_id, permission=permission)
            self.__saved_permissions.append(saved_permission)

            return True

        return False

    def get_all_permissions_from_instance(self, instance_id: int) -> Optional[List[Dict]]:
        self._execute(
            "SELECT * "
            "FROM permissions "
            "WHERE instance_id = %s",
            (instance_id, )
        )

        data = self._fetchall()

        print(data)
        output_data = []

        for permissions in data:
            permission_number = permissions[2] if permissions[2] is not None else 0

            broken_permission = self.__break_into_permissions(permission_number)
            user_id = permissions[0]
            permission_out = []

            for permission in broken_permission:
                permission_type = self.__get_permission_type(permission)
                if permission_type is None:
                    continue

                permission_out.append({permission_type.name: permission})

            output_data.append({'user_id': user_id, "permissions": permission_out})

        return output_data

    def add_permission(self, user_id: int, instance_id: int, permission_to_check: int):
        if not self.__permission_exists(permission_to_check):
            return

        self.__delete_saved_permission(user_id, instance_id)

        if not self.__row_exists(user_id, instance_id):
            self.__new_permission(user_id, instance_id)

        permission = self.__get_permission(user_id, instance_id)
        if permission is None:
            permission = 0

        if self.__check_permission(permission, permission_to_check):
            return

        permission += permission_to_check
        self.__update_permission(user_id, instance_id, permission)

    def remove_permission(self, user_id: int, instance_id: int, permission_to_check: int):
        if not self.__permission_exists(permission_to_check):
            return

        self.__delete_saved_permission(user_id, instance_id)

        if not self.__row_exists(user_id, instance_id):
            self.__new_permission(user_id, instance_id)

        permission = self.__get_permission(user_id, instance_id)
        if permission is None:
            return

        if not self.__check_permission(permission, permission_to_check):
            return

        permission -= permission_to_check
        self.__update_permission(user_id, instance_id, permission)
