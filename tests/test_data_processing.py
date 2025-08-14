import pytest
import numpy as np
from src.embeddingbuddy.data.parser import NDJSONParser
from src.embeddingbuddy.data.processor import DataProcessor
from src.embeddingbuddy.models.schemas import Document


class TestNDJSONParser:
    def test_parse_text_basic(self):
        text_content = (
            '{"id": "test1", "text": "Hello world", "embedding": [0.1, 0.2, 0.3]}'
        )
        documents = NDJSONParser.parse_text(text_content)

        assert len(documents) == 1
        assert documents[0].id == "test1"
        assert documents[0].text == "Hello world"
        assert documents[0].embedding == [0.1, 0.2, 0.3]

    def test_parse_text_with_metadata(self):
        text_content = '{"id": "test1", "text": "Hello", "embedding": [0.1, 0.2], "category": "greeting", "tags": ["test"]}'
        documents = NDJSONParser.parse_text(text_content)

        assert documents[0].category == "greeting"
        assert documents[0].tags == ["test"]

    def test_parse_text_missing_id(self):
        text_content = '{"text": "Hello", "embedding": [0.1, 0.2]}'
        documents = NDJSONParser.parse_text(text_content)

        assert len(documents) == 1
        assert documents[0].id is not None  # Should be auto-generated


class TestDataProcessor:
    def test_extract_embeddings(self):
        documents = [
            Document(id="1", text="test1", embedding=[0.1, 0.2]),
            Document(id="2", text="test2", embedding=[0.3, 0.4]),
        ]

        processor = DataProcessor()
        embeddings = processor._extract_embeddings(documents)

        assert embeddings.shape == (2, 2)
        assert np.allclose(embeddings[0], [0.1, 0.2])
        assert np.allclose(embeddings[1], [0.3, 0.4])

    def test_combine_data(self):
        from src.embeddingbuddy.models.schemas import ProcessedData

        doc_data = ProcessedData(
            documents=[Document(id="1", text="doc", embedding=[0.1, 0.2])],
            embeddings=np.array([[0.1, 0.2]]),
        )

        prompt_data = ProcessedData(
            documents=[Document(id="p1", text="prompt", embedding=[0.3, 0.4])],
            embeddings=np.array([[0.3, 0.4]]),
        )

        processor = DataProcessor()
        all_embeddings, documents, prompts = processor.combine_data(
            doc_data, prompt_data
        )

        assert all_embeddings.shape == (2, 2)
        assert len(documents) == 1
        assert len(prompts) == 1
        assert documents[0].id == "1"
        assert prompts[0].id == "p1"


if __name__ == "__main__":
    pytest.main([__file__])
