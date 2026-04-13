from abc import ABC, abstractmethod
from typing import Any

class IModalityExplanationCoordinator(ABC):
    @abstractmethod
    def load_model(self, model_path: str) -> Any:
        pass

    @abstractmethod
    def load_data(self, dataset_path: str) -> Any: 
        pass

    @abstractmethod
    def run_task_explainer(self, task: str, method: str, data_path: str) -> Any: 
        pass