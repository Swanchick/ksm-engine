from abc import ABC, abstractmethod


class InstanceManagerController(ABC):
    @abstractmethod
    def pin_port_to_instance(self, instance_id: int, port: int, current_port: int):
        pass

    @abstractmethod
    def unpin_port_from_instance(self, port: int):
        pass

    @property
    def instances(self):
        return
