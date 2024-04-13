from abc import ABC, abstractmethod
from typing import List, Optional, Dict


class Api(ABC):
    @abstractmethod
    def request(self, method_name: str, instance_data: Dict) -> Optional[Dict]:
        pass
