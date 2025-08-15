from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import logging


logger = logging.getLogger(__name__)


@dataclass
class FieldMapping:
    """Configuration for mapping OpenSearch fields to standard format."""

    embedding_field: str
    text_field: str
    id_field: Optional[str] = None
    category_field: Optional[str] = None
    subcategory_field: Optional[str] = None
    tags_field: Optional[str] = None


class FieldMapper:
    """Handles field mapping and data transformation from OpenSearch to standard format."""

    @staticmethod
    def suggest_mappings(field_analysis: Dict) -> Dict[str, List[str]]:
        """
        Suggest field mappings based on field analysis.

        Each dropdown will show ALL available fields, but ordered by relevance
        with the most likely candidates first.

        Args:
            field_analysis: Analysis results from OpenSearchClient.analyze_fields

        Returns:
            Dictionary with suggested fields for each mapping (ordered by relevance)
        """
        all_fields = field_analysis.get("all_fields", [])
        vector_fields = [vf["name"] for vf in field_analysis.get("vector_fields", [])]
        text_fields = field_analysis.get("text_fields", [])
        keyword_fields = field_analysis.get("keyword_fields", [])

        # Helper function to create ordered suggestions
        def create_ordered_suggestions(primary_candidates, all_available_fields):
            # Start with primary candidates, then add all other fields
            ordered = []
            # Add primary candidates first
            for field in primary_candidates:
                if field in all_available_fields and field not in ordered:
                    ordered.append(field)
            # Add remaining fields
            for field in all_available_fields:
                if field not in ordered:
                    ordered.append(field)
            return ordered

        suggestions = {}

        # Embedding field suggestions (vector fields first, then name-based candidates, then all fields)
        embedding_candidates = vector_fields.copy()
        # Add fields that likely contain embeddings based on name
        embedding_name_candidates = [
            f
            for f in all_fields
            if any(
                keyword in f.lower()
                for keyword in ["embedding", "embeddings", "vector", "vectors", "embed"]
            )
        ]
        # Add name-based candidates that aren't already in vector_fields
        for candidate in embedding_name_candidates:
            if candidate not in embedding_candidates:
                embedding_candidates.append(candidate)
        suggestions["embedding"] = create_ordered_suggestions(
            embedding_candidates, all_fields
        )

        # Text field suggestions (text fields first, then all fields)
        text_candidates = text_fields.copy()
        suggestions["text"] = create_ordered_suggestions(text_candidates, all_fields)

        # ID field suggestions (ID-like fields first, then all fields)
        id_candidates = [
            f
            for f in keyword_fields
            if any(keyword in f.lower() for keyword in ["id", "_id", "doc", "document"])
        ]
        id_candidates.append("_id")  # _id is always available
        suggestions["id"] = create_ordered_suggestions(id_candidates, all_fields)

        # Category field suggestions (category-like fields first, then all fields)
        category_candidates = [
            f
            for f in keyword_fields
            if any(
                keyword in f.lower()
                for keyword in ["category", "class", "type", "label"]
            )
        ]
        suggestions["category"] = create_ordered_suggestions(
            category_candidates, all_fields
        )

        # Subcategory field suggestions (subcategory-like fields first, then all fields)
        subcategory_candidates = [
            f
            for f in keyword_fields
            if any(
                keyword in f.lower()
                for keyword in ["subcategory", "subclass", "subtype", "subtopic"]
            )
        ]
        suggestions["subcategory"] = create_ordered_suggestions(
            subcategory_candidates, all_fields
        )

        # Tags field suggestions (tag-like fields first, then all fields)
        tags_candidates = [
            f
            for f in keyword_fields
            if any(
                keyword in f.lower()
                for keyword in ["tag", "tags", "keyword", "keywords"]
            )
        ]
        suggestions["tags"] = create_ordered_suggestions(tags_candidates, all_fields)

        return suggestions

    @staticmethod
    def validate_mapping(
        mapping: FieldMapping, available_fields: List[str]
    ) -> List[str]:
        """
        Validate that the field mapping is correct.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Required fields validation
        if not mapping.embedding_field:
            errors.append("Embedding field is required")
        elif mapping.embedding_field not in available_fields:
            errors.append(
                f"Embedding field '{mapping.embedding_field}' not found in index"
            )

        if not mapping.text_field:
            errors.append("Text field is required")
        elif mapping.text_field not in available_fields:
            errors.append(f"Text field '{mapping.text_field}' not found in index")

        # Optional fields validation
        optional_fields = {
            "id_field": mapping.id_field,
            "category_field": mapping.category_field,
            "subcategory_field": mapping.subcategory_field,
            "tags_field": mapping.tags_field,
        }

        for field_name, field_value in optional_fields.items():
            if field_value and field_value not in available_fields:
                errors.append(
                    f"Field '{field_value}' for {field_name} not found in index"
                )

        return errors

    @staticmethod
    def transform_documents(
        documents: List[Dict[str, Any]], mapping: FieldMapping
    ) -> List[Dict[str, Any]]:
        """
        Transform OpenSearch documents to standard format using field mapping.

        Args:
            documents: Raw documents from OpenSearch
            mapping: Field mapping configuration

        Returns:
            List of transformed documents in standard format
        """
        transformed = []

        for doc in documents:
            try:
                # Build standard format document
                standard_doc = {}

                # Required fields
                if mapping.embedding_field in doc:
                    standard_doc["embedding"] = doc[mapping.embedding_field]
                else:
                    logger.warning(
                        f"Missing embedding field '{mapping.embedding_field}' in document"
                    )
                    continue

                if mapping.text_field in doc:
                    standard_doc["text"] = str(doc[mapping.text_field])
                else:
                    logger.warning(
                        f"Missing text field '{mapping.text_field}' in document"
                    )
                    continue

                # Optional fields
                if mapping.id_field and mapping.id_field in doc:
                    standard_doc["id"] = str(doc[mapping.id_field])

                if mapping.category_field and mapping.category_field in doc:
                    standard_doc["category"] = str(doc[mapping.category_field])

                if mapping.subcategory_field and mapping.subcategory_field in doc:
                    standard_doc["subcategory"] = str(doc[mapping.subcategory_field])

                if mapping.tags_field and mapping.tags_field in doc:
                    tags = doc[mapping.tags_field]
                    # Handle both string and list tags
                    if isinstance(tags, list):
                        standard_doc["tags"] = [str(tag) for tag in tags]
                    else:
                        standard_doc["tags"] = [str(tags)]

                transformed.append(standard_doc)

            except Exception as e:
                logger.error(f"Error transforming document: {e}")
                continue

        logger.info(f"Transformed {len(transformed)} documents out of {len(documents)}")
        return transformed

    @staticmethod
    def create_mapping_from_dict(mapping_dict: Dict[str, str]) -> FieldMapping:
        """
        Create a FieldMapping from a dictionary.

        Args:
            mapping_dict: Dictionary with field mappings

        Returns:
            FieldMapping instance
        """
        return FieldMapping(
            embedding_field=mapping_dict.get("embedding", ""),
            text_field=mapping_dict.get("text", ""),
            id_field=mapping_dict.get("id") or None,
            category_field=mapping_dict.get("category") or None,
            subcategory_field=mapping_dict.get("subcategory") or None,
            tags_field=mapping_dict.get("tags") or None,
        )
