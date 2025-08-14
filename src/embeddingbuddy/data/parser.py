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
        for line in text_content.strip().split("\n"):
            if line.strip():
                doc_dict = json.loads(line)
                doc = NDJSONParser._dict_to_document(doc_dict)
                documents.append(doc)
        return documents

    @staticmethod
    def _dict_to_document(doc_dict: dict) -> Document:
        if "id" not in doc_dict:
            doc_dict["id"] = str(uuid.uuid4())

        return Document(
            id=doc_dict["id"],
            text=doc_dict["text"],
            embedding=doc_dict["embedding"],
            category=doc_dict.get("category"),
            subcategory=doc_dict.get("subcategory"),
            tags=doc_dict.get("tags"),
        )
