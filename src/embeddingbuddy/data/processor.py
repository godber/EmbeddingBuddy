import numpy as np
from typing import List, Optional, Tuple
from ..models.schemas import Document, ProcessedData
from ..models.field_mapper import FieldMapper
from .parser import NDJSONParser


class DataProcessor:
    def __init__(self):
        self.parser = NDJSONParser()

    def process_upload(
        self, contents: str, filename: Optional[str] = None
    ) -> ProcessedData:
        try:
            documents = self.parser.parse_upload_contents(contents)
            embeddings = self._extract_embeddings(documents)
            return ProcessedData(documents=documents, embeddings=embeddings)
        except Exception as e:
            return ProcessedData(documents=[], embeddings=np.array([]), error=str(e))

    def process_text(self, text_content: str) -> ProcessedData:
        try:
            documents = self.parser.parse_text(text_content)
            embeddings = self._extract_embeddings(documents)
            return ProcessedData(documents=documents, embeddings=embeddings)
        except Exception as e:
            return ProcessedData(documents=[], embeddings=np.array([]), error=str(e))

    def process_opensearch_data(
        self, raw_documents: List[dict], field_mapping
    ) -> ProcessedData:
        """Process raw OpenSearch documents using field mapping."""
        try:
            # Transform documents using field mapping
            transformed_docs = FieldMapper.transform_documents(
                raw_documents, field_mapping
            )

            # Parse transformed documents
            documents = []
            for doc_dict in transformed_docs:
                try:
                    # Ensure required fields are present with defaults if needed
                    if "id" not in doc_dict or not doc_dict["id"]:
                        doc_dict["id"] = f"doc_{len(documents)}"

                    doc = Document(**doc_dict)
                    documents.append(doc)
                except Exception:
                    continue  # Skip invalid documents

            if not documents:
                return ProcessedData(
                    documents=[],
                    embeddings=np.array([]),
                    error="No valid documents after transformation",
                )

            embeddings = self._extract_embeddings(documents)
            return ProcessedData(documents=documents, embeddings=embeddings)

        except Exception as e:
            return ProcessedData(documents=[], embeddings=np.array([]), error=str(e))

    def _extract_embeddings(self, documents: List[Document]) -> np.ndarray:
        if not documents:
            return np.array([])
        return np.array([doc.embedding for doc in documents])

    def combine_data(
        self, doc_data: ProcessedData, prompt_data: Optional[ProcessedData] = None
    ) -> Tuple[np.ndarray, List[Document], Optional[List[Document]]]:
        if not doc_data or doc_data.error:
            raise ValueError("Invalid document data")

        all_embeddings = doc_data.embeddings
        documents = doc_data.documents
        prompts = None

        if prompt_data and not prompt_data.error and prompt_data.documents:
            all_embeddings = np.vstack([doc_data.embeddings, prompt_data.embeddings])
            prompts = prompt_data.documents

        return all_embeddings, documents, prompts

    def split_reduced_data(
        self, reduced_embeddings: np.ndarray, n_documents: int, n_prompts: int = 0
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        doc_reduced = reduced_embeddings[:n_documents]
        prompt_reduced = None

        if n_prompts > 0:
            prompt_reduced = reduced_embeddings[n_documents : n_documents + n_prompts]

        return doc_reduced, prompt_reduced
