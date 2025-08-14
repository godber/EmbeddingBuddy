from dash import callback, Input, Output, State, no_update
from ...data.processor import DataProcessor
from ...data.sources.opensearch import OpenSearchClient
from ...models.field_mapper import FieldMapper
from ...config.settings import AppSettings


class DataProcessingCallbacks:
    def __init__(self):
        self.processor = DataProcessor()
        self.opensearch_client = OpenSearchClient()
        self._register_callbacks()

    def _register_callbacks(self):
        @callback(
            [
                Output("processed-data", "data", allow_duplicate=True),
                Output("upload-error-alert", "children", allow_duplicate=True),
                Output("upload-error-alert", "is_open", allow_duplicate=True),
            ],
            Input("upload-data", "contents"),
            State("upload-data", "filename"),
            prevent_initial_call=True,
        )
        def process_uploaded_file(contents, filename):
            if contents is None:
                return None, "", False

            processed_data = self.processor.process_upload(contents, filename)

            if processed_data.error:
                error_message = self._format_error_message(
                    processed_data.error, filename
                )
                return (
                    {"error": processed_data.error},
                    error_message,
                    True,  # Show error alert
                )

            return (
                {
                    "documents": [
                        self._document_to_dict(doc) for doc in processed_data.documents
                    ],
                    "embeddings": processed_data.embeddings.tolist(),
                },
                "",
                False,  # Hide error alert
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

        # OpenSearch callbacks
        @callback(
            [
                Output("tab-content", "children"),
            ],
            [Input("data-source-tabs", "active_tab")],
            prevent_initial_call=False,
        )
        def render_tab_content(active_tab):
            from ...ui.components.datasource import DataSourceComponent

            datasource = DataSourceComponent()

            if active_tab == "opensearch-tab":
                return [datasource.create_opensearch_tab()]
            else:
                return [datasource.create_file_upload_tab()]

        @callback(
            Output("auth-collapse", "is_open"),
            [Input("auth-toggle", "n_clicks")],
            [State("auth-collapse", "is_open")],
            prevent_initial_call=True,
        )
        def toggle_auth(n_clicks, is_open):
            if n_clicks:
                return not is_open
            return is_open

        @callback(
            Output("auth-toggle", "children"),
            [Input("auth-collapse", "is_open")],
            prevent_initial_call=False,
        )
        def update_auth_button_text(is_open):
            return "Hide Authentication" if is_open else "Show Authentication"

        @callback(
            [
                Output("connection-status", "children"),
                Output("field-mapping-section", "children"),
                Output("field-mapping-section", "style"),
                Output("load-data-section", "style"),
                Output("load-opensearch-data-btn", "disabled"),
                Output("embedding-field-dropdown", "options"),
                Output("text-field-dropdown", "options"),
                Output("id-field-dropdown", "options"),
                Output("category-field-dropdown", "options"),
                Output("subcategory-field-dropdown", "options"),
                Output("tags-field-dropdown", "options"),
            ],
            [Input("test-connection-btn", "n_clicks")],
            [
                State("opensearch-url", "value"),
                State("opensearch-index", "value"),
                State("opensearch-username", "value"),
                State("opensearch-password", "value"),
                State("opensearch-api-key", "value"),
            ],
            prevent_initial_call=True,
        )
        def test_opensearch_connection(
            n_clicks, url, index_name, username, password, api_key
        ):
            if not n_clicks or not url or not index_name:
                return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update

            # Test connection
            success, message = self.opensearch_client.connect(
                url=url,
                username=username,
                password=password,
                api_key=api_key,
                verify_certs=AppSettings.OPENSEARCH_VERIFY_CERTS,
            )

            if not success:
                return (
                    self._create_status_alert(f"❌ {message}", "danger"),
                    [],
                    {"display": "none"},
                    {"display": "none"},
                    True,
                    [],  # empty options for hidden dropdowns
                    [],
                    [],
                    [],
                    [],
                    [],
                )

            # Analyze fields
            success, field_analysis, analysis_message = (
                self.opensearch_client.analyze_fields(index_name)
            )

            if not success:
                return (
                    self._create_status_alert(f"❌ {analysis_message}", "danger"),
                    [],
                    {"display": "none"},
                    {"display": "none"},
                    True,
                    [],  # empty options for hidden dropdowns
                    [],
                    [],
                    [],
                    [],
                    [],
                )

            # Generate field suggestions
            field_suggestions = FieldMapper.suggest_mappings(field_analysis)

            from ...ui.components.datasource import DataSourceComponent

            datasource = DataSourceComponent()
            field_mapping_ui = datasource.create_field_mapping_interface(
                field_suggestions
            )

            return (
                self._create_status_alert(f"✅ {message}", "success"),
                field_mapping_ui,
                {"display": "block"},
                {"display": "block"},
                False,
                [{"label": field, "value": field} for field in field_suggestions.get("embedding", [])],
                [{"label": field, "value": field} for field in field_suggestions.get("text", [])],
                [{"label": field, "value": field} for field in field_suggestions.get("id", [])],
                [{"label": field, "value": field} for field in field_suggestions.get("category", [])],
                [{"label": field, "value": field} for field in field_suggestions.get("subcategory", [])],
                [{"label": field, "value": field} for field in field_suggestions.get("tags", [])],
            )

        @callback(
            [
                Output("processed-data", "data", allow_duplicate=True),
                Output("opensearch-success-alert", "children", allow_duplicate=True),
                Output("opensearch-success-alert", "is_open", allow_duplicate=True),
                Output("opensearch-error-alert", "children", allow_duplicate=True),
                Output("opensearch-error-alert", "is_open", allow_duplicate=True),
            ],
            [Input("load-opensearch-data-btn", "n_clicks")],
            [
                State("opensearch-index", "value"),
                State("embedding-field-dropdown", "value"),
                State("text-field-dropdown", "value"),
                State("id-field-dropdown", "value"),
                State("category-field-dropdown", "value"),
                State("subcategory-field-dropdown", "value"),
                State("tags-field-dropdown", "value"),
            ],
            prevent_initial_call=True,
        )
        def load_opensearch_data(
            n_clicks,
            index_name,
            embedding_field,
            text_field,
            id_field,
            category_field,
            subcategory_field,
            tags_field,
        ):
            if not n_clicks or not index_name or not embedding_field or not text_field:
                return no_update, no_update, no_update, no_update, no_update

            try:
                # Create field mapping
                field_mapping = FieldMapper.create_mapping_from_dict(
                    {
                        "embedding": embedding_field,
                        "text": text_field,
                        "id": id_field,
                        "category": category_field,
                        "subcategory": subcategory_field,
                        "tags": tags_field,
                    }
                )

                # Fetch data from OpenSearch
                success, raw_documents, message = self.opensearch_client.fetch_data(
                    index_name, size=AppSettings.OPENSEARCH_DEFAULT_SIZE
                )

                if not success:
                    return (
                        no_update,
                        "",
                        False,
                        f"❌ Failed to fetch data: {message}",
                        True,
                    )

                # Process the data
                processed_data = self.processor.process_opensearch_data(
                    raw_documents, field_mapping
                )

                if processed_data.error:
                    return (
                        {"error": processed_data.error},
                        "",
                        False,
                        f"❌ Data processing error: {processed_data.error}",
                        True,
                    )

                success_message = f"✅ Successfully loaded {len(processed_data.documents)} documents from OpenSearch"

                return (
                    {
                        "documents": [
                            self._document_to_dict(doc)
                            for doc in processed_data.documents
                        ],
                        "embeddings": processed_data.embeddings.tolist(),
                    },
                    success_message,
                    True,
                    "",
                    False,
                )

            except Exception as e:
                return (no_update, "", False, f"❌ Unexpected error: {str(e)}", True)

        # Sync callbacks to update hidden dropdowns from UI dropdowns
        @callback(
            Output("embedding-field-dropdown", "value"),
            Input("embedding-field-dropdown-ui", "value"),
            prevent_initial_call=True,
        )
        def sync_embedding_dropdown(value):
            return value

        @callback(
            Output("text-field-dropdown", "value"),
            Input("text-field-dropdown-ui", "value"),
            prevent_initial_call=True,
        )
        def sync_text_dropdown(value):
            return value

        @callback(
            Output("id-field-dropdown", "value"),
            Input("id-field-dropdown-ui", "value"),
            prevent_initial_call=True,
        )
        def sync_id_dropdown(value):
            return value

        @callback(
            Output("category-field-dropdown", "value"),
            Input("category-field-dropdown-ui", "value"),
            prevent_initial_call=True,
        )
        def sync_category_dropdown(value):
            return value

        @callback(
            Output("subcategory-field-dropdown", "value"),
            Input("subcategory-field-dropdown-ui", "value"),
            prevent_initial_call=True,
        )
        def sync_subcategory_dropdown(value):
            return value

        @callback(
            Output("tags-field-dropdown", "value"),
            Input("tags-field-dropdown-ui", "value"),
            prevent_initial_call=True,
        )
        def sync_tags_dropdown(value):
            return value

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
        if "embedding" in error.lower() and (
            "key" in error.lower() or "required field" in error.lower()
        ):
            return (
                f"❌ Missing 'embedding' field{file_part}. "
                "Each line must contain an 'embedding' field with a list of numbers."
            )
        elif "text" in error.lower() and (
            "key" in error.lower() or "required field" in error.lower()
        ):
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

    @staticmethod
    def _create_status_alert(message: str, color: str):
        """Create a status alert component."""
        import dash_bootstrap_components as dbc

        return dbc.Alert(message, color=color, className="mb-2")
