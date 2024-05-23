from abc import ABC, abstractmethod
from server.instance_arguments import InstanceArguments


class InstanceApiController(ABC):
    @abstractmethod
    def instance_arguments(self) -> InstanceArguments:
        pass
