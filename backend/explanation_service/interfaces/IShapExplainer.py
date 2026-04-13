from abc import ABC, abstractmethod
from typing import Any
import shap

class IShapExplainer(ABC):
    @abstractmethod
    def pre_processing(self, dataset) -> Any:
        pass

    @abstractmethod
    def build_shap_explainer(self) -> shap.Explainer: 
        pass

    @abstractmethod
    def compute_shap_values(self, explainer: shap.Explainer, dataset) -> Any: 
        pass

    @abstractmethod
    def explain(self, **kwargs) -> Any: 
        pass