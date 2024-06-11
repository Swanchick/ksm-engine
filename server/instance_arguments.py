from database_utils.database import Database

KSM_DATABASE = "ksm_database"


class InstanceArguments(Database):
    def start(self):
        self._connect(KSM_DATABASE)

        self._execute(
            "CREATE TABLE IF NOT EXISTS instance_arguments("
            "argument_id INT PRIMARY KEY AUTO_INCREMENT,"
            "instance_id INT,"
            "argument CHAR(128) UNIQUE,"
            "FOREIGN KEY (instance_id) REFERENCES instances(instance_id)"
            ")"
        )

    def add_argument(self, instance_id: int, argument: str):
        self._connect(KSM_DATABASE)

        self._execute(
            "INSERT INTO instance_arguments ("
            "instance_id, "
            "argument) "
            "VALUES (%s, %s)",
            (instance_id, argument)
        )

        self._commit()

    def remove_argument(self, instance_id: int, argument: str):
        self._connect(KSM_DATABASE)

        self._execute(
            "DELETE FROM instance_arguments "
            "WHERE instance_id = %s AND argument = %s",
            (instance_id, argument)
        )

        self._commit()

    def get_arguments(self, instance_id: int):
        self._connect(KSM_DATABASE)

        self._execute(
            "SELECT argument "
            "FROM instance_arguments "
            "WHERE instance_id = %s",
            (instance_id,)
        )

        arguments = []
        for argument in self._cursor.fetchall():
            arguments.append(argument[0])

        return arguments
