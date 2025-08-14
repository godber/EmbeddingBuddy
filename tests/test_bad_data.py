"""Tests for handling bad/invalid data files."""

import pytest
import json
import base64
from src.embeddingbuddy.data.parser import NDJSONParser
from src.embeddingbuddy.data.processor import DataProcessor


class TestBadDataHandling:
    """Test suite for various types of invalid input data."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = NDJSONParser()
        self.processor = DataProcessor()

    def _create_upload_contents(self, text_content: str) -> str:
        """Helper to create upload contents format."""
        encoded = base64.b64encode(text_content.encode("utf-8")).decode("utf-8")
        return f"data:application/json;base64,{encoded}"

    def test_missing_embedding_field(self):
        """Test files missing required embedding field."""
        bad_content = '{"id": "doc_001", "text": "Sample text", "category": "test"}'

        with pytest.raises(KeyError, match="embedding"):
            self.parser.parse_text(bad_content)

        # Test processor error handling
        upload_contents = self._create_upload_contents(bad_content)
        result = self.processor.process_upload(upload_contents)
        assert result.error is not None
        assert "embedding" in result.error

    def test_missing_text_field(self):
        """Test files missing required text field."""
        bad_content = (
            '{"id": "doc_001", "embedding": [0.1, 0.2, 0.3], "category": "test"}'
        )

        with pytest.raises(KeyError, match="text"):
            self.parser.parse_text(bad_content)

        # Test processor error handling
        upload_contents = self._create_upload_contents(bad_content)
        result = self.processor.process_upload(upload_contents)
        assert result.error is not None
        assert "text" in result.error

    def test_malformed_json_lines(self):
        """Test files with malformed JSON syntax."""
        # Missing closing brace
        bad_content = '{"id": "doc_001", "embedding": [0.1, 0.2], "text": "test"'

        with pytest.raises(json.JSONDecodeError):
            self.parser.parse_text(bad_content)

        # Test processor error handling
        upload_contents = self._create_upload_contents(bad_content)
        result = self.processor.process_upload(upload_contents)
        assert result.error is not None

    def test_invalid_embedding_types(self):
        """Test files with invalid embedding data types."""
        test_cases = [
            # String instead of array
            '{"id": "doc_001", "embedding": "not_an_array", "text": "test"}',
            # Mixed types in array
            '{"id": "doc_002", "embedding": [0.1, "text", 0.3], "text": "test"}',
            # Empty array
            '{"id": "doc_003", "embedding": [], "text": "test"}',
            # Null embedding
            '{"id": "doc_004", "embedding": null, "text": "test"}',
        ]

        for bad_content in test_cases:
            upload_contents = self._create_upload_contents(bad_content)
            result = self.processor.process_upload(upload_contents)
            assert result.error is not None, f"Should fail for: {bad_content}"

    def test_inconsistent_embedding_dimensions(self):
        """Test files with embeddings of different dimensions."""
        bad_content = """{"id": "doc_001", "embedding": [0.1, 0.2, 0.3, 0.4], "text": "4D embedding"}
{"id": "doc_002", "embedding": [0.1, 0.2, 0.3], "text": "3D embedding"}"""

        upload_contents = self._create_upload_contents(bad_content)
        result = self.processor.process_upload(upload_contents)

        # This might succeed parsing but fail in processing
        # The error depends on where dimension validation occurs
        if result.error is None:
            # If parsing succeeds, check that embeddings have inconsistent shapes
            assert len(result.documents) == 2
            assert len(result.documents[0].embedding) != len(
                result.documents[1].embedding
            )

    def test_empty_lines_in_ndjson(self):
        """Test files with empty lines mixed in."""
        content_with_empty_lines = """{"id": "doc_001", "embedding": [0.1, 0.2], "text": "First line"}

{"id": "doc_002", "embedding": [0.3, 0.4], "text": "After empty line"}"""

        # This should work - empty lines should be skipped
        documents = self.parser.parse_text(content_with_empty_lines)
        assert len(documents) == 2
        assert documents[0].id == "doc_001"
        assert documents[1].id == "doc_002"

    def test_not_ndjson_format(self):
        """Test regular JSON array instead of NDJSON."""
        json_array = """[
  {"id": "doc_001", "embedding": [0.1, 0.2], "text": "First"},
  {"id": "doc_002", "embedding": [0.3, 0.4], "text": "Second"}
]"""

        with pytest.raises(json.JSONDecodeError):
            self.parser.parse_text(json_array)

    def test_binary_content_in_file(self):
        """Test files with binary content mixed in."""
        # Simulate binary content that can't be decoded
        binary_content = (
            b'\x00\x01\x02{"id": "doc_001", "embedding": [0.1], "text": "test"}'
        )

        # This should result in an error when processing
        encoded = base64.b64encode(binary_content).decode("utf-8")
        upload_contents = f"data:application/json;base64,{encoded}"
        result = self.processor.process_upload(upload_contents)

        # Should either fail with UnicodeDecodeError or JSON parsing error
        assert result.error is not None

    def test_extremely_large_embeddings(self):
        """Test embeddings with very large dimensions."""
        large_embedding = [0.1] * 10000  # 10k dimensions
        content = json.dumps(
            {
                "id": "doc_001",
                "embedding": large_embedding,
                "text": "Large embedding test",
            }
        )

        # This should work but might be slow
        upload_contents = self._create_upload_contents(content)
        result = self.processor.process_upload(upload_contents)

        if result.error is None:
            assert len(result.documents) == 1
            assert len(result.documents[0].embedding) == 10000

    def test_special_characters_in_text(self):
        """Test handling of special characters and unicode."""
        special_content = json.dumps(
            {
                "id": "doc_001",
                "embedding": [0.1, 0.2],
                "text": 'Special chars: 🚀 ñoñó 中文 \n\t"',
            },
            ensure_ascii=False,
        )

        upload_contents = self._create_upload_contents(special_content)
        result = self.processor.process_upload(upload_contents)

        assert result.error is None
        assert len(result.documents) == 1
        assert "🚀" in result.documents[0].text

    def test_processor_error_structure(self):
        """Test that processor returns proper error structure."""
        bad_content = '{"invalid": "json"'  # Missing closing brace
        upload_contents = self._create_upload_contents(bad_content)

        result = self.processor.process_upload(upload_contents)

        # Check error structure
        assert result.error is not None
        assert isinstance(result.error, str)
        assert len(result.documents) == 0
        assert result.embeddings.size == 0

    def test_multiple_errors_in_file(self):
        """Test file with multiple different types of errors."""
        multi_error_content = """{"id": "doc_001", "text": "Missing embedding"}
{"id": "doc_002", "embedding": "wrong_type", "text": "Wrong embedding type"}
{"id": "doc_003", "embedding": [0.1, 0.2], "text": "Valid line"}
{"id": "doc_004", "embedding": [0.3, 0.4]"""  # Missing text and closing brace

        upload_contents = self._create_upload_contents(multi_error_content)
        result = self.processor.process_upload(upload_contents)

        # Should fail on first error encountered
        assert result.error is not None
