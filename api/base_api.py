from abc import ABC, abstractmethod
from typing import Dict, Optional, List


class BaseApi(ABC):
    @abstractmethod
    def request(self, routes: List[str], *args, **kwargs) -> Optional[Dict]:
        pass
