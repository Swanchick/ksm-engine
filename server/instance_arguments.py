from typing import List, Optional, Dict
from database_utils.database import Database
from utils.response_builder import ResponseBuilder
from utils.http_status import HttpStatus


class InstanceArguments(Database):
    def __init__(self):
        super().__init__()

        self.start()

    def start(self):
        self._execute(
            "CREATE TABLE IF NOT EXISTS instance_arguments("
            "argument_id INT PRIMARY KEY AUTO_INCREMENT, "
            "instance_id INT, "
            "argument CHAR(128), "
            "FOREIGN KEY (instance_id) REFERENCES instances(instance_id)"
            ")"
        )

    def add_argument(self, instance_id: int, argument: str):
        if instance_id is None and argument is None:
            return ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad request!").build()

        self._execute(
            "INSERT INTO instance_arguments ("
            "instance_id, "
            "argument) "
            "VALUES (%s, %s)",
            (instance_id, argument)
        )

        self._commit()

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("Arguments added!").build()

    def remove_argument(self, instance_id: int, argument_id: int):
        self._execute(
            "DELETE FROM instance_arguments "
            "WHERE instance_id = %s AND argument_id = %s",
            (instance_id, argument_id)
        )

        self._commit()

        return ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("Argument removed!").build()

    def get_arguments(self, instance_id: int):
        self._execute(
            "SELECT argument, argument_id "
            "FROM instance_arguments "
            "WHERE instance_id = %s",
            (instance_id,)
        )

        arguments = []
        for argument in self._cursor.fetchall():
            arguments.append({"argument": argument[0], "argument_id": argument[1]})

        return arguments

    def get_arguments_list(self, instance_id: int):
        dict_arguments = self.get_arguments(instance_id)
        arguments = []
        for argument in dict_arguments:
            arguments.append(argument["argument"])

        return arguments
