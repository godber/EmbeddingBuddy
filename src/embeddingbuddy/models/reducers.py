from abc import ABC, abstractmethod
import numpy as np
from sklearn.decomposition import PCA
import umap
from openTSNE import TSNE
from .schemas import ReducedData


class DimensionalityReducer(ABC):
    def __init__(self, n_components: int = 3, random_state: int = 42):
        self.n_components = n_components
        self.random_state = random_state
        self._reducer = None

    @abstractmethod
    def fit_transform(self, embeddings: np.ndarray) -> ReducedData:
        pass

    @abstractmethod
    def get_method_name(self) -> str:
        pass


class PCAReducer(DimensionalityReducer):
    def fit_transform(self, embeddings: np.ndarray) -> ReducedData:
        self._reducer = PCA(n_components=self.n_components)
        reduced = self._reducer.fit_transform(embeddings)
        variance_explained = self._reducer.explained_variance_ratio_

        return ReducedData(
            reduced_embeddings=reduced,
            variance_explained=variance_explained,
            method=self.get_method_name(),
            n_components=self.n_components,
        )

    def get_method_name(self) -> str:
        return "PCA"


class TSNEReducer(DimensionalityReducer):
    def fit_transform(self, embeddings: np.ndarray) -> ReducedData:
        self._reducer = TSNE(
            n_components=self.n_components, random_state=self.random_state
        )
        reduced = self._reducer.fit(embeddings)

        return ReducedData(
            reduced_embeddings=reduced,
            variance_explained=None,
            method=self.get_method_name(),
            n_components=self.n_components,
        )

    def get_method_name(self) -> str:
        return "t-SNE"


class UMAPReducer(DimensionalityReducer):
    def fit_transform(self, embeddings: np.ndarray) -> ReducedData:
        self._reducer = umap.UMAP(
            n_components=self.n_components, random_state=self.random_state
        )
        reduced = self._reducer.fit_transform(embeddings)

        return ReducedData(
            reduced_embeddings=reduced,
            variance_explained=None,
            method=self.get_method_name(),
            n_components=self.n_components,
        )

    def get_method_name(self) -> str:
        return "UMAP"


class ReducerFactory:
    @staticmethod
    def create_reducer(
        method: str, n_components: int = 3, random_state: int = 42
    ) -> DimensionalityReducer:
        method_lower = method.lower()

        if method_lower == "pca":
            return PCAReducer(n_components=n_components, random_state=random_state)
        elif method_lower == "tsne":
            return TSNEReducer(n_components=n_components, random_state=random_state)
        elif method_lower == "umap":
            return UMAPReducer(n_components=n_components, random_state=random_state)
        else:
            raise ValueError(f"Unknown reduction method: {method}")

    @staticmethod
    def get_available_methods() -> list:
        return ["pca", "tsne", "umap"]
