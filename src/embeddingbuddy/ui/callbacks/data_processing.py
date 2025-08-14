from dash import callback, Input, Output, State
from ...data.processor import DataProcessor


class DataProcessingCallbacks:
    def __init__(self):
        self.processor = DataProcessor()
        self._register_callbacks()

    def _register_callbacks(self):
        @callback(
            Output("processed-data", "data"),
            Input("upload-data", "contents"),
            State("upload-data", "filename"),
        )
        def process_uploaded_file(contents, filename):
            if contents is None:
                return None

            processed_data = self.processor.process_upload(contents, filename)

            if processed_data.error:
                return {"error": processed_data.error}

            return {
                "documents": [
                    self._document_to_dict(doc) for doc in processed_data.documents
                ],
                "embeddings": processed_data.embeddings.tolist(),
            }

        @callback(
            Output("processed-prompts", "data"),
            Input("upload-prompts", "contents"),
            State("upload-prompts", "filename"),
        )
        def process_uploaded_prompts(contents, filename):
            if contents is None:
                return None

            processed_data = self.processor.process_upload(contents, filename)

            if processed_data.error:
                return {"error": processed_data.error}

            return {
                "prompts": [
                    self._document_to_dict(doc) for doc in processed_data.documents
                ],
                "embeddings": processed_data.embeddings.tolist(),
            }

    @staticmethod
    def _document_to_dict(doc):
        return {
            "id": doc.id,
            "text": doc.text,
            "embedding": doc.embedding,
            "category": doc.category,
            "subcategory": doc.subcategory,
            "tags": doc.tags,
        }
