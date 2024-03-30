from utils import Database
from typing import List
from .instance import ServerInstance
from utils import SettingsBuilder, EngineSettings


class InstanceManager(Database):
    __instances: List[ServerInstance]
    __settings: EngineSettings

    def __load_instance(self, name):
        pass

    def __load_settings(self):
        self.__settings = (SettingsBuilder()
                           .get_settings("engine")
                           .get())

    def __generate_folder(self, instance_name: str) -> str:
        return f"{self.__settings.instance_folder}{instance_name}/"

    def start(self):
        self.__load_settings()
        self.__instances = []

        self._connector = self._connect("ksm_database")
        self._cursor = self._connector.cursor()

        self._cursor.execute("CREATE TABLE IF NOT EXISTS instances (id INT PRIMARY KEY AUTO_INCREMENT, "
                             "name CHAR(128) UNIQUE)")

    def create_instance(self, name):
        if not (self._connector and self._cursor):
            return

        self._cursor.execute("INSERT INTO instances (name) VALUES (%s)", (name, ))
        self._connector.commit()
        self._cursor.execute("SELECT id FROM instances WHERE name = %s", (name, ))
        instance_id = self._cursor.fetchone()[0]
        instance_folder = self.__generate_folder(name)

        instance = ServerInstance(instance_id, name, instance_folder)

        self.__instances.append(instance)

    def load_instances(self):
        if not (self._connector and self._cursor):
            return

        self._cursor.execute("SELECT * FROM instances")
        instances = self._cursor.fetchall()

        for instance_data in instances:
            instance_id = instance_data[0]
            instance_name = instance_data[1]
            instance_folder = self.__generate_folder(instance_name)

            instance = ServerInstance(instance_id, instance_name, instance_folder)

            self.__instances.append(instance)

    @property
    def instances(self) -> List[ServerInstance]:
        return self.__instances