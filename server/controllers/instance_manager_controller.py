from abc import ABC, abstractmethod


class InstanceManagerController(ABC):
    @abstractmethod
    def pin_port_to_instance(self, port: int, instance_id: int):
        pass

    @abstractmethod
    def unpin_port_from_instance(self, port: int):
        pass
