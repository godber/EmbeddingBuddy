"""Tests for client-side embedding processing functionality."""

import numpy as np

from src.embeddingbuddy.data.processor import DataProcessor
from src.embeddingbuddy.models.schemas import ProcessedData


class TestClientEmbeddingsProcessing:
    """Test client-side embeddings processing functionality."""

    def setup_method(self):
        """Set up test instances."""
        self.processor = DataProcessor()

    def test_process_client_embeddings_success(self):
        """Test successful processing of client-side embeddings data."""
        client_data = {
            "documents": [
                {
                    "id": "text_input_0",
                    "text": "First test document",
                    "category": "Text Input",
                    "subcategory": "Generated",
                    "tags": [],
                },
                {
                    "id": "text_input_1",
                    "text": "Second test document",
                    "category": "Text Input",
                    "subcategory": "Generated",
                    "tags": [],
                },
            ],
            "embeddings": [[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]],
        }

        result = self.processor.process_client_embeddings(client_data)

        assert isinstance(result, ProcessedData)
        assert result.error is None
        assert len(result.documents) == 2
        assert result.embeddings.shape == (2, 4)

        # Check document content
        assert result.documents[0].text == "First test document"
        assert result.documents[1].text == "Second test document"

        # Check embeddings match
        np.testing.assert_array_equal(result.embeddings[0], [0.1, 0.2, 0.3, 0.4])
        np.testing.assert_array_equal(result.embeddings[1], [0.5, 0.6, 0.7, 0.8])

    def test_process_client_embeddings_with_error(self):
        """Test processing client data with error."""
        client_data = {"error": "Transformers.js not loaded"}

        result = self.processor.process_client_embeddings(client_data)

        assert isinstance(result, ProcessedData)
        assert result.error == "Transformers.js not loaded"
        assert len(result.documents) == 0
        assert result.embeddings.size == 0

    def test_process_client_embeddings_missing_data(self):
        """Test processing with missing documents or embeddings."""
        client_data = {"documents": []}

        result = self.processor.process_client_embeddings(client_data)

        assert isinstance(result, ProcessedData)
        assert "No documents or embeddings in client data" in result.error
        assert len(result.documents) == 0

    def test_process_client_embeddings_mismatch_count(self):
        """Test processing with mismatched document and embedding counts."""
        client_data = {
            "documents": [
                {
                    "id": "test",
                    "text": "Test document",
                    "category": "Test",
                    "subcategory": "Test",
                    "tags": [],
                }
            ],
            "embeddings": [[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]],
        }

        result = self.processor.process_client_embeddings(client_data)

        assert isinstance(result, ProcessedData)
        assert "Mismatch between number of documents and embeddings" in result.error
        assert len(result.documents) == 0

    def test_process_client_embeddings_invalid_document(self):
        """Test processing with invalid document data."""
        client_data = {
            "documents": [
                {"text": ""},  # Empty text should be skipped
                {
                    "id": "test2",
                    "text": "Valid document",
                    "category": "Test",
                    "subcategory": "Test",
                    "tags": [],
                },
            ],
            "embeddings": [[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]],
        }

        result = self.processor.process_client_embeddings(client_data)

        assert isinstance(result, ProcessedData)
        assert result.error is None
        assert len(result.documents) == 1  # Only valid document should be processed
        assert result.documents[0].text == "Valid document"

    def test_process_client_embeddings_auto_id_generation(self):
        """Test automatic ID generation for documents without IDs."""
        client_data = {
            "documents": [
                {
                    "text": "Document without ID",
                    "category": "Test",
                    "subcategory": "Test",
                    "tags": [],
                }
            ],
            "embeddings": [[0.1, 0.2, 0.3, 0.4]],
        }

        result = self.processor.process_client_embeddings(client_data)

        assert isinstance(result, ProcessedData)
        assert result.error is None
        assert len(result.documents) == 1
        assert result.documents[0].id.startswith("text_input_")

    def test_process_client_embeddings_invalid_embedding_format(self):
        """Test processing with invalid embedding format."""
        client_data = {
            "documents": [
                {
                    "id": "test",
                    "text": "Test document",
                    "category": "Test",
                    "subcategory": "Test",
                    "tags": [],
                }
            ],
            "embeddings": 0.5,  # Scalar instead of array
        }

        result = self.processor.process_client_embeddings(client_data)

        assert isinstance(result, ProcessedData)
        assert result.error is not None  # Should have some error
        assert len(result.documents) == 0
