from utils import Database


class PermissionManager(Database):
    def start(self):
        self._connector = self._connect("ksm_database")
        self._cursor = self._connector.cursor()

        self._cursor.execute("CREATE TABLE IF NOT EXISTS permissions ("
                             "user_id INT, "
                             "instance_id INT,"
                             "PRIMARY KEY (user_id, instance_id),"
                             "permission_console BOOLEAN DEFAULT FALSE,"
                             "permission_start_stop BOOLEAN DEFAULT FALSE)")

    def __row_exists(self, user_id: int, instance_id: int) -> bool:
        self._cursor.execute("SELECT COUNT(*) FROM permissions WHERE user_id = %s AND instance_id = %s",
                             (user_id, instance_id))

        result = self._cursor.fetchone()
        return result[0] > 0

    def __new_permission(self, user_id: int, instance_id: int):
        self._cursor.execute("INSERT INTO permissions (user_id, instance_id) VALUES (%s, %s)", (user_id, instance_id))
        self._connector.commit()

    def check_permission(self, user_id: int, instance_id: int, permission_type: str) -> bool:
        if not (self._connector and self._cursor and self.__row_exists(user_id, instance_id)):
            return False

        self._cursor.execute(f"SELECT {permission_type} FROM permissions WHERE user_id = %s AND instance_id = %s",
                             (user_id, instance_id))

        return self._cursor.fetchone()[0]

    def add_permission(self, user_id: int, instance_id: int, permission_type: str, state: bool):
        if not (self._connector and self._cursor):
            return

        if not self.__row_exists(user_id, instance_id):
            self.__new_permission(user_id, instance_id)

        self._cursor.execute(f"UPDATE permissions SET {permission_type} = %s WHERE user_id = %s AND instance_id = %s",
                             (state,
                              user_id,
                              instance_id
                              ))

        self._connector.commit()
