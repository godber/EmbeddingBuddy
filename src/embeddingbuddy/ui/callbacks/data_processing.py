from dash import callback, Input, Output, State
from ...data.processor import DataProcessor


class DataProcessingCallbacks:
    def __init__(self):
        self.processor = DataProcessor()
        self._register_callbacks()

    def _register_callbacks(self):
        @callback(
            [
                Output("processed-data", "data", allow_duplicate=True),
                Output("upload-error-alert", "children", allow_duplicate=True),
                Output("upload-error-alert", "is_open", allow_duplicate=True),
                Output("upload-success-alert", "children", allow_duplicate=True),
                Output("upload-success-alert", "is_open", allow_duplicate=True),
            ],
            Input("upload-data", "contents"),
            State("upload-data", "filename"),
            prevent_initial_call=True,
        )
        def process_uploaded_file(contents, filename):
            if contents is None:
                return None, "", False, "", False

            processed_data = self.processor.process_upload(contents, filename)

            if processed_data.error:
                error_message = self._format_error_message(processed_data.error, filename)
                return (
                    {"error": processed_data.error},
                    error_message,
                    True,  # Show error alert
                    "",
                    False,  # Hide success alert
                )

            success_message = f"Successfully loaded {len(processed_data.documents)} documents from {filename or 'file'}"
            return (
                {
                    "documents": [
                        self._document_to_dict(doc) for doc in processed_data.documents
                    ],
                    "embeddings": processed_data.embeddings.tolist(),
                },
                "",
                False,  # Hide error alert
                success_message,
                True,   # Show success alert
            )

        @callback(
            Output("processed-prompts", "data", allow_duplicate=True),
            Input("upload-prompts", "contents"),
            State("upload-prompts", "filename"),
            prevent_initial_call=True,
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

    @staticmethod
    def _format_error_message(error: str, filename: str | None = None) -> str:
        """Format error message with helpful guidance for users."""
        file_part = f" in file '{filename}'" if filename else ""
        
        # Check for common error patterns and provide helpful messages
        if "embedding" in error.lower() and ("key" in error.lower() or "required field" in error.lower()):
            return (
                f"❌ Missing 'embedding' field{file_part}. "
                "Each line must contain an 'embedding' field with a list of numbers."
            )
        elif "text" in error.lower() and ("key" in error.lower() or "required field" in error.lower()):
            return (
                f"❌ Missing 'text' field{file_part}. "
                "Each line must contain a 'text' field with the document content."
            )
        elif "json" in error.lower() and "decode" in error.lower():
            return (
                f"❌ Invalid JSON format{file_part}. "
                "Please check that each line is valid JSON with proper syntax (quotes, braces, etc.)."
            )
        elif "unicode" in error.lower() or "decode" in error.lower():
            return (
                f"❌ File encoding issue{file_part}. "
                "Please ensure the file is saved in UTF-8 format and contains no binary data."
            )
        elif "array" in error.lower() or "list" in error.lower():
            return (
                f"❌ Invalid embedding format{file_part}. "
                "Embeddings must be arrays/lists of numbers, not strings or other types."
            )
        else:
            return (
                f"❌ Error processing file{file_part}: {error}. "
                "Please check that your file is valid NDJSON with required 'text' and 'embedding' fields."
            )
