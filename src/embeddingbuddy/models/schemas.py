from typing import List, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class Document:
    id: str
    text: str
    embedding: List[float]
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tags: Optional[List[str]] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.category is None:
            self.category = "Unknown"
        if self.subcategory is None:
            self.subcategory = "Unknown"


@dataclass
class ProcessedData:
    documents: List[Document]
    embeddings: np.ndarray
    error: Optional[str] = None

    def __post_init__(self):
        if self.embeddings is not None and not isinstance(self.embeddings, np.ndarray):
            self.embeddings = np.array(self.embeddings)


@dataclass
class ReducedData:
    reduced_embeddings: np.ndarray
    variance_explained: Optional[np.ndarray] = None
    method: str = "unknown"
    n_components: int = 2

    def __post_init__(self):
        if not isinstance(self.reduced_embeddings, np.ndarray):
            self.reduced_embeddings = np.array(self.reduced_embeddings)


@dataclass
class PlotData:
    documents: List[Document]
    coordinates: np.ndarray
    prompts: Optional[List[Document]] = None
    prompt_coordinates: Optional[np.ndarray] = None

    def __post_init__(self):
        if not isinstance(self.coordinates, np.ndarray):
            self.coordinates = np.array(self.coordinates)
        if self.prompt_coordinates is not None and not isinstance(
            self.prompt_coordinates, np.ndarray
        ):
            self.prompt_coordinates = np.array(self.prompt_coordinates)
