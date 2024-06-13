from abc import ABC, abstractmethod
from typing import List
from server.instance import ServerInstance


class InstanceCallController(ABC):
    __instances: List[ServerInstance]

    @abstractmethod
    def add_instance(self, instance: ServerInstance):
        pass

    @property
    def instances(self):
        return
