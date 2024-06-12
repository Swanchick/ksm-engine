from typing import Dict, List, Optional
from .base_caller import BaseCaller
from .base_api import BaseApi


class Api(BaseApi):
    _require_user: bool = True
    _caller: BaseCaller = None

    def request(self, routes: List[str], *args, **kwargs) -> Optional[Dict]:
        if self._caller is None:
            return

        response = self._caller.request(routes, *args, **kwargs)

        return response

    @property
    def require_user(self) -> bool:
        return self._require_user
