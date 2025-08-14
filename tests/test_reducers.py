import pytest
import numpy as np
from src.embeddingbuddy.models.reducers import (
    ReducerFactory,
    PCAReducer,
    TSNEReducer,
    UMAPReducer,
)


class TestReducerFactory:
    def test_create_pca_reducer(self):
        reducer = ReducerFactory.create_reducer("pca", n_components=2)
        assert isinstance(reducer, PCAReducer)
        assert reducer.n_components == 2

    def test_create_tsne_reducer(self):
        reducer = ReducerFactory.create_reducer("tsne", n_components=3)
        assert isinstance(reducer, TSNEReducer)
        assert reducer.n_components == 3

    def test_create_umap_reducer(self):
        reducer = ReducerFactory.create_reducer("umap", n_components=2)
        assert isinstance(reducer, UMAPReducer)
        assert reducer.n_components == 2

    def test_invalid_method(self):
        with pytest.raises(ValueError, match="Unknown reduction method"):
            ReducerFactory.create_reducer("invalid_method")

    def test_available_methods(self):
        methods = ReducerFactory.get_available_methods()
        assert "pca" in methods
        assert "tsne" in methods
        assert "umap" in methods


class TestPCAReducer:
    def test_fit_transform(self):
        embeddings = np.random.rand(100, 512)
        reducer = PCAReducer(n_components=2)

        result = reducer.fit_transform(embeddings)

        assert result.reduced_embeddings.shape == (100, 2)
        assert result.variance_explained is not None
        assert result.method == "PCA"
        assert result.n_components == 2

    def test_method_name(self):
        reducer = PCAReducer()
        assert reducer.get_method_name() == "PCA"


class TestTSNEReducer:
    def test_fit_transform_small_dataset(self):
        embeddings = np.random.rand(30, 10)  # Small dataset for faster testing
        reducer = TSNEReducer(n_components=2)

        result = reducer.fit_transform(embeddings)

        assert result.reduced_embeddings.shape == (30, 2)
        assert result.variance_explained is None  # t-SNE doesn't provide this
        assert result.method == "t-SNE"
        assert result.n_components == 2

    def test_method_name(self):
        reducer = TSNEReducer()
        assert reducer.get_method_name() == "t-SNE"


class TestUMAPReducer:
    def test_fit_transform(self):
        embeddings = np.random.rand(50, 10)
        reducer = UMAPReducer(n_components=2)

        result = reducer.fit_transform(embeddings)

        assert result.reduced_embeddings.shape == (50, 2)
        assert result.variance_explained is None  # UMAP doesn't provide this
        assert result.method == "UMAP"
        assert result.n_components == 2

    def test_method_name(self):
        reducer = UMAPReducer()
        assert reducer.get_method_name() == "UMAP"


if __name__ == "__main__":
    pytest.main([__file__])
