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
        self._cursor.execute("SELECT COUNT(*) FROM permissions WHERE user_id = %s AND instance_id = %S",
                             (user_id, instance_id))

        result = self._cursor.fetchone()
        return result[0] > 0

    def __new_permission(self, user_id: int, instance_id: int):
        self._cursor.execute("INSERT INTO permissions (user_id, instance_id) VALUES (%s, %s)", (user_id, instance_id))
        self._connector.commit()

    def check_permission(self, user_id: int, instance_id: int, permission_type: str) -> bool:
        if not (self._connector and self._cursor and self.__row_exists(user_id, instance_id)):
            return False

        self._cursor.execute("SELECT %s FROM permissions WHERE user_id = %s AND instance_id = %s", (permission_type, user_id, instance_id))

        return self._cursor.fetchone()[0]

    def add_permission(self, user_id: int, instance_id: int, permission_type: str, state: bool):
        if not (self._connector and self._cursor):
            return

        if not self.__row_exists(user_id, instance_id):
            self.__new_permission(user_id, instance_id)

        self._cursor.execute("UPDATE permissions SET %s = %s WHERE user_id = %s AND instance_id = %s", (permission_type,
                                                                                                        state, user_id,
                                                                                                        instance_id))
        self._connector.commit()
