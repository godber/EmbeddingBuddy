from unittest.mock import Mock, patch
from src.embeddingbuddy.data.sources.opensearch import OpenSearchClient
from src.embeddingbuddy.models.field_mapper import FieldMapper, FieldMapping


class TestOpenSearchClient:
    def test_init(self):
        client = OpenSearchClient()
        assert client.client is None
        assert client.connection_info is None

    @patch("src.embeddingbuddy.data.sources.opensearch.OpenSearch")
    def test_connect_success(self, mock_opensearch):
        # Mock the OpenSearch client
        mock_client_instance = Mock()
        mock_client_instance.info.return_value = {
            "cluster_name": "test-cluster",
            "version": {"number": "2.0.0"},
        }
        mock_opensearch.return_value = mock_client_instance

        client = OpenSearchClient()
        success, message = client.connect("https://localhost:9200")

        assert success is True
        assert "test-cluster" in message
        assert client.client is not None
        assert client.connection_info["cluster_name"] == "test-cluster"

    @patch("src.embeddingbuddy.data.sources.opensearch.OpenSearch")
    def test_connect_failure(self, mock_opensearch):
        # Mock connection failure
        mock_opensearch.side_effect = Exception("Connection failed")

        client = OpenSearchClient()
        success, message = client.connect("https://localhost:9200")

        assert success is False
        assert "Connection failed" in message
        assert client.client is None

    def test_analyze_fields(self):
        client = OpenSearchClient()
        client.client = Mock()

        # Mock mapping response
        mock_mapping = {
            "test-index": {
                "mappings": {
                    "properties": {
                        "embedding": {"type": "dense_vector", "dimension": 768},
                        "text": {"type": "text"},
                        "category": {"type": "keyword"},
                        "id": {"type": "keyword"},
                        "count": {"type": "integer"},
                    }
                }
            }
        }
        client.client.indices.get_mapping.return_value = mock_mapping

        success, analysis, message = client.analyze_fields("test-index")

        assert success is True
        assert len(analysis["vector_fields"]) == 1
        assert analysis["vector_fields"][0]["name"] == "embedding"
        assert analysis["vector_fields"][0]["dimension"] == 768
        assert "text" in analysis["text_fields"]
        assert "category" in analysis["keyword_fields"]
        assert "count" in analysis["numeric_fields"]

    def test_fetch_sample_data(self):
        client = OpenSearchClient()
        client.client = Mock()

        # Mock search response
        mock_response = {
            "hits": {
                "hits": [
                    {"_source": {"text": "doc1", "embedding": [0.1, 0.2]}},
                    {"_source": {"text": "doc2", "embedding": [0.3, 0.4]}},
                ]
            }
        }
        client.client.search.return_value = mock_response

        success, documents, message = client.fetch_sample_data("test-index", size=2)

        assert success is True
        assert len(documents) == 2
        assert documents[0]["text"] == "doc1"
        assert documents[1]["text"] == "doc2"


class TestFieldMapper:
    def test_suggest_mappings(self):
        field_analysis = {
            "vector_fields": [{"name": "embedding", "dimension": 768}],
            "text_fields": ["content", "description"],
            "keyword_fields": ["doc_id", "category", "type", "tags"],
            "numeric_fields": ["count"],
            "all_fields": [
                "embedding",
                "content",
                "description",
                "doc_id",
                "category",
                "type",
                "tags",
                "count",
            ],
        }

        suggestions = FieldMapper.suggest_mappings(field_analysis)

        # Check that all dropdowns contain all fields
        all_fields = [
            "embedding",
            "content",
            "description",
            "doc_id",
            "category",
            "type",
            "tags",
            "count",
        ]
        for field_type in [
            "embedding",
            "text",
            "id",
            "category",
            "subcategory",
            "tags",
        ]:
            for field in all_fields:
                assert field in suggestions[field_type], (
                    f"Field '{field}' missing from {field_type} suggestions"
                )

        # Check that best candidates are first
        assert (
            suggestions["embedding"][0] == "embedding"
        )  # vector field should be first
        assert suggestions["text"][0] in [
            "content",
            "description",
        ]  # text fields should be first
        assert suggestions["id"][0] == "doc_id"  # ID-like field should be first
        assert suggestions["category"][0] in [
            "category",
            "type",
        ]  # category-like field should be first
        assert suggestions["tags"][0] == "tags"  # tags field should be first

    def test_suggest_mappings_name_based_embedding(self):
        """Test that fields named 'embedding' are prioritized even without vector type."""
        field_analysis = {
            "vector_fields": [],  # No explicit vector fields detected
            "text_fields": ["content", "description"],
            "keyword_fields": ["doc_id", "category", "type", "tags"],
            "numeric_fields": ["count"],
            "all_fields": [
                "content",
                "description",
                "doc_id",
                "category",
                "embedding",
                "type",
                "tags",
                "count",
            ],
        }

        suggestions = FieldMapper.suggest_mappings(field_analysis)

        # Check that 'embedding' field is prioritized despite not being detected as vector type
        assert suggestions["embedding"][0] == "embedding", (
            "Field named 'embedding' should be first priority"
        )

        # Check that all fields are still available
        all_fields = [
            "content",
            "description",
            "doc_id",
            "category",
            "embedding",
            "type",
            "tags",
            "count",
        ]
        for field_type in [
            "embedding",
            "text",
            "id",
            "category",
            "subcategory",
            "tags",
        ]:
            for field in all_fields:
                assert field in suggestions[field_type], (
                    f"Field '{field}' missing from {field_type} suggestions"
                )

    def test_validate_mapping_success(self):
        mapping = FieldMapping(
            embedding_field="embedding", text_field="text", id_field="doc_id"
        )
        available_fields = ["embedding", "text", "doc_id", "category"]

        errors = FieldMapper.validate_mapping(mapping, available_fields)

        assert len(errors) == 0

    def test_validate_mapping_missing_required(self):
        mapping = FieldMapping(embedding_field="missing_field", text_field="text")
        available_fields = ["text", "category"]

        errors = FieldMapper.validate_mapping(mapping, available_fields)

        assert len(errors) == 1
        assert "missing_field" in errors[0]
        assert "not found" in errors[0]

    def test_validate_mapping_missing_optional(self):
        mapping = FieldMapping(
            embedding_field="embedding",
            text_field="text",
            category_field="missing_category",
        )
        available_fields = ["embedding", "text"]

        errors = FieldMapper.validate_mapping(mapping, available_fields)

        assert len(errors) == 1
        assert "missing_category" in errors[0]

    def test_transform_documents(self):
        mapping = FieldMapping(
            embedding_field="vector",
            text_field="content",
            id_field="doc_id",
            category_field="type",
        )

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

        transformed = FieldMapper.transform_documents(raw_documents, mapping)

        assert len(transformed) == 2
        assert transformed[0]["embedding"] == [0.1, 0.2, 0.3]
        assert transformed[0]["text"] == "Test document 1"
        assert transformed[0]["id"] == "doc1"
        assert transformed[0]["category"] == "news"

    def test_transform_documents_missing_required(self):
        mapping = FieldMapping(embedding_field="vector", text_field="content")

        raw_documents = [
            {
                "vector": [0.1, 0.2, 0.3],
                # Missing content field
            }
        ]

        transformed = FieldMapper.transform_documents(raw_documents, mapping)

        assert len(transformed) == 0  # Document should be skipped

    def test_create_mapping_from_dict(self):
        mapping_dict = {
            "embedding": "vector_field",
            "text": "text_field",
            "id": "doc_id",
            "category": "cat_field",
            "subcategory": "subcat_field",
            "tags": "tags_field",
        }

        mapping = FieldMapper.create_mapping_from_dict(mapping_dict)

        assert mapping.embedding_field == "vector_field"
        assert mapping.text_field == "text_field"
        assert mapping.id_field == "doc_id"
        assert mapping.category_field == "cat_field"
        assert mapping.subcategory_field == "subcat_field"
        assert mapping.tags_field == "tags_field"

    def test_create_mapping_from_dict_minimal(self):
        mapping_dict = {"embedding": "vector_field", "text": "text_field"}

        mapping = FieldMapper.create_mapping_from_dict(mapping_dict)

        assert mapping.embedding_field == "vector_field"
        assert mapping.text_field == "text_field"
        assert mapping.id_field is None
        assert mapping.category_field is None
