import json
import uuid
import base64
from typing import List
from ..models.schemas import Document


class NDJSONParser:
    @staticmethod
    def parse_upload_contents(contents: str) -> List[Document]:
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        text_content = decoded.decode("utf-8")
        return NDJSONParser.parse_text(text_content)

    @staticmethod
    def parse_text(text_content: str) -> List[Document]:
        documents = []
        for line_num, line in enumerate(text_content.strip().split("\n"), 1):
            if line.strip():
                try:
                    doc_dict = json.loads(line)
                    doc = NDJSONParser._dict_to_document(doc_dict)
                    documents.append(doc)
                except json.JSONDecodeError as e:
                    raise json.JSONDecodeError(
                        f"Invalid JSON on line {line_num}: {e.msg}", e.doc, e.pos
                    )
                except KeyError as e:
                    raise KeyError(f"Missing required field {e} on line {line_num}")
                except (TypeError, ValueError) as e:
                    raise ValueError(
                        f"Invalid data format on line {line_num}: {str(e)}"
                    )
        return documents

    @staticmethod
    def _dict_to_document(doc_dict: dict) -> Document:
        if "id" not in doc_dict:
            doc_dict["id"] = str(uuid.uuid4())

        # Validate required fields
        if "text" not in doc_dict:
            raise KeyError("'text'")
        if "embedding" not in doc_dict:
            raise KeyError("'embedding'")

        # Validate embedding format
        embedding = doc_dict["embedding"]
        if not isinstance(embedding, list):
            raise ValueError(
                f"Embedding must be a list, got {type(embedding).__name__}"
            )

        if not embedding:
            raise ValueError("Embedding cannot be empty")

        # Check that all embedding values are numbers
        for i, val in enumerate(embedding):
            if not isinstance(val, (int, float)) or val != val:  # NaN check
                raise ValueError(
                    f"Embedding contains invalid value at index {i}: {val}"
                )

        return Document(
            id=doc_dict["id"],
            text=doc_dict["text"],
            embedding=embedding,
            category=doc_dict.get("category"),
            subcategory=doc_dict.get("subcategory"),
            tags=doc_dict.get("tags"),
        )
