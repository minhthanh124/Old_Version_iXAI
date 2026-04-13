from abc import ABC, abstractmethod
from typing import Any

class IGradcamExplainer(ABC):
    @abstractmethod
    def pre_processing(self, dataset) -> Any: 
        pass

    @abstractmethod
    def compute_cam(self, **kwargs) -> Any:
        pass

    @abstractmethod
    def apply_cam(self, **kwargs) -> bytes:
        pass

    @abstractmethod
    def explain(self, **kwargs): pass
