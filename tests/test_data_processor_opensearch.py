from unittest.mock import patch
from src.embeddingbuddy.data.processor import DataProcessor
from src.embeddingbuddy.models.field_mapper import FieldMapping


class TestDataProcessorOpenSearch:
    def test_process_opensearch_data_success(self):
        processor = DataProcessor()

        # Mock raw OpenSearch documents
        raw_documents = [
            {
                "vector": [0.1, 0.2, 0.3],
                "content": "Test document 1",
                "doc_id": "doc1",
                "type": "news",
            },
            {
                "vector": [0.4, 0.5, 0.6],
                "content": "Test document 2",
                "doc_id": "doc2",
                "type": "blog",
            },
        ]

        # Create field mapping
        field_mapping = FieldMapping(
            embedding_field="vector",
            text_field="content",
            id_field="doc_id",
            category_field="type",
        )

        # Process the data
        processed_data = processor.process_opensearch_data(raw_documents, field_mapping)

        # Assertions
        assert processed_data.error is None
        assert len(processed_data.documents) == 2
        assert processed_data.embeddings.shape == (2, 3)

        # Check first document
        doc1 = processed_data.documents[0]
        assert doc1.text == "Test document 1"
        assert doc1.embedding == [0.1, 0.2, 0.3]
        assert doc1.id == "doc1"
        assert doc1.category == "news"

        # Check second document
        doc2 = processed_data.documents[1]
        assert doc2.text == "Test document 2"
        assert doc2.embedding == [0.4, 0.5, 0.6]
        assert doc2.id == "doc2"
        assert doc2.category == "blog"

    def test_process_opensearch_data_with_tags(self):
        processor = DataProcessor()

        # Mock raw OpenSearch documents with tags
        raw_documents = [
            {
                "vector": [0.1, 0.2, 0.3],
                "content": "Test document with tags",
                "keywords": ["tag1", "tag2"],
            }
        ]

        # Create field mapping
        field_mapping = FieldMapping(
            embedding_field="vector", text_field="content", tags_field="keywords"
        )

        processed_data = processor.process_opensearch_data(raw_documents, field_mapping)

        assert processed_data.error is None
        assert len(processed_data.documents) == 1
        doc = processed_data.documents[0]
        assert doc.tags == ["tag1", "tag2"]

    def test_process_opensearch_data_invalid_documents(self):
        processor = DataProcessor()

        # Mock raw documents with missing required fields
        raw_documents = [
            {
                "vector": [0.1, 0.2, 0.3],
                # Missing text field
            }
        ]

        field_mapping = FieldMapping(embedding_field="vector", text_field="content")

        processed_data = processor.process_opensearch_data(raw_documents, field_mapping)

        # Should return error since no valid documents
        assert processed_data.error is not None
        assert "No valid documents" in processed_data.error
        assert len(processed_data.documents) == 0

    def test_process_opensearch_data_partial_success(self):
        processor = DataProcessor()

        # Mix of valid and invalid documents
        raw_documents = [
            {
                "vector": [0.1, 0.2, 0.3],
                "content": "Valid document",
            },
            {
                "vector": [0.4, 0.5, 0.6],
                # Missing content field - should be skipped
            },
            {
                "vector": [0.7, 0.8, 0.9],
                "content": "Another valid document",
            },
        ]

        field_mapping = FieldMapping(embedding_field="vector", text_field="content")

        processed_data = processor.process_opensearch_data(raw_documents, field_mapping)

        # Should process valid documents only
        assert processed_data.error is None
        assert len(processed_data.documents) == 2
        assert processed_data.documents[0].text == "Valid document"
        assert processed_data.documents[1].text == "Another valid document"

    @patch("src.embeddingbuddy.models.field_mapper.FieldMapper.transform_documents")
    def test_process_opensearch_data_transformation_error(self, mock_transform):
        processor = DataProcessor()

        # Mock transformation error
        mock_transform.side_effect = Exception("Transformation failed")

        raw_documents = [{"vector": [0.1], "content": "test"}]
        field_mapping = FieldMapping(embedding_field="vector", text_field="content")

        processed_data = processor.process_opensearch_data(raw_documents, field_mapping)

        assert processed_data.error is not None
        assert "Transformation failed" in processed_data.error
        assert len(processed_data.documents) == 0

    def test_process_opensearch_data_empty_input(self):
        processor = DataProcessor()

        raw_documents = []
        field_mapping = FieldMapping(embedding_field="vector", text_field="content")

        processed_data = processor.process_opensearch_data(raw_documents, field_mapping)

        assert processed_data.error is not None
        assert "No valid documents" in processed_data.error
        assert len(processed_data.documents) == 0
