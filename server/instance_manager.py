from typing import List, Dict, Optional
from user import PermissionManager
from .instance import ServerInstance
from api import Api
from database_utils import Database
from .instance_loader import InstanceLoader
from utils import ResponseBuilder

KSM_DATABASE = "ksm_database"


class InstanceManager(Database, Api):
    __instances: List[ServerInstance]
    __permission_manager: PermissionManager
    __instance_folder: str

    def __load_instance(self, instance_id: int, instance_name, instance_folder: str) -> ServerInstance:
        instance = ServerInstance(self.__permission_manager, instance_id, instance_name, instance_folder)
        self.__instances.append(instance)

        return instance

    def __generate_folder(self, instance_name: str) -> str:
        return f"{self.__instance_folder}{instance_name}/"

    def __get_instance_by_id(self, instance_id: int) -> Optional[ServerInstance]:
        for instance in self.__instances:
            if instance.instance_id == instance_id:
                return instance

    def start(self):
        self.__instances = []

        self._connector = self._connect(KSM_DATABASE)
        self._cursor = self._connector.cursor()

        self._cursor.execute("CREATE TABLE IF NOT EXISTS instances (id INT PRIMARY KEY AUTO_INCREMENT, "
                             "name CHAR(128) UNIQUE)")

    def create_instance(self, name: str, instance_type: str):
        if not (self._connector and self._cursor):
            return

        instance_loader = InstanceLoader(self.__instance_folder, name, instance_type)
        instance_loader.load()

        self._cursor.execute("INSERT INTO instances (name) VALUES (%s)", (name, ))
        self._connector.commit()
        self._cursor.execute("SELECT id FROM instances WHERE name = %s", (name, ))
        instance_id = self._cursor.fetchone()[0]
        instance_folder = self.__generate_folder(name)

        self.__load_instance(instance_id, name, instance_folder)

    def load_folder(self, instance_folder: str):
        self.__instance_folder = instance_folder

    def load_permission_manager(self, permission_manager: PermissionManager):
        self.__permission_manager = permission_manager

    def load_instances(self):
        if not (self._connector and self._cursor):
            return

        self._cursor.execute("SELECT * FROM instances")
        instances = self._cursor.fetchall()

        for instance_data in instances:
            instance_id = instance_data[0]
            instance_name = instance_data[1]
            instance_folder = self.__generate_folder(instance_name)

            self.__load_instance(instance_id, instance_name, instance_folder)

    def request(self, method_name: str, instance_data: Dict) -> Optional[Dict]:
        instance_id = int(instance_data["instance_id"])
        instance = self.__get_instance_by_id(instance_id)

        if not instance:
            return ResponseBuilder().status(500).message("Instance not found").build()

        args = instance_data["args"] if "args" in instance_data else []

        final_args = [instance_data["user_id"]] + args

        output_data = instance.call(method_name, *final_args)

        return output_data

    @property
    def instances(self) -> List[ServerInstance]:
        return self.__instances
