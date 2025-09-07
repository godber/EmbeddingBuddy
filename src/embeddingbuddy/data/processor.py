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

    def process_client_embeddings(self, embeddings_data: dict) -> ProcessedData:
        """Process embeddings data received from client-side JavaScript."""
        try:
            if "error" in embeddings_data:
                return ProcessedData(
                    documents=[],
                    embeddings=np.array([]),
                    error=embeddings_data["error"],
                )

            # Extract documents and embeddings from client data
            documents_data = embeddings_data.get("documents", [])
            embeddings_list = embeddings_data.get("embeddings", [])

            if not documents_data or not embeddings_list:
                return ProcessedData(
                    documents=[],
                    embeddings=np.array([]),
                    error="No documents or embeddings in client data",
                )

            if len(documents_data) != len(embeddings_list):
                return ProcessedData(
                    documents=[],
                    embeddings=np.array([]),
                    error="Mismatch between number of documents and embeddings",
                )

            # Convert embeddings to numpy array first
            try:
                embeddings = np.array(embeddings_list)

                if embeddings.ndim != 2:
                    return ProcessedData(
                        documents=[],
                        embeddings=np.array([]),
                        error="Invalid embedding dimensions",
                    )

            except Exception as e:
                return ProcessedData(
                    documents=[],
                    embeddings=np.array([]),
                    error=f"Error processing embeddings: {str(e)}",
                )

            # Convert to Document objects with embeddings
            documents = []
            for i, doc_data in enumerate(documents_data):
                try:
                    # Skip if we don't have a corresponding embedding
                    if i >= len(embeddings):
                        continue

                    # Ensure required fields are present
                    if "id" not in doc_data or not doc_data["id"]:
                        doc_data["id"] = f"text_input_{i}"
                    if "text" not in doc_data or not doc_data["text"].strip():
                        continue  # Skip documents without text

                    # Add the embedding to doc_data
                    doc_data["embedding"] = embeddings[i].tolist()

                    doc = Document(**doc_data)
                    documents.append(doc)
                except Exception:
                    # Skip invalid documents but continue processing
                    continue

            if not documents:
                return ProcessedData(
                    documents=[],
                    embeddings=np.array([]),
                    error="No valid documents found in client data",
                )

            # Only keep embeddings for valid documents
            valid_embeddings = embeddings[: len(documents)]

            return ProcessedData(documents=documents, embeddings=valid_embeddings)

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
