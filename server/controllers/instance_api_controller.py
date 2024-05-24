from abc import ABC, abstractmethod
from server.instance_arguments import InstanceArguments
from typing import Optional


class InstanceApiController(ABC):
    @property
    def instance_arguments(self) -> Optional[InstanceArguments]:
        return
