from dash import callback, Input, Output, State, no_update, html
from ...data.processor import DataProcessor
from ...data.sources.opensearch import OpenSearchClient
from ...models.field_mapper import FieldMapper
from ...config.settings import AppSettings


class DataProcessingCallbacks:
    def __init__(self):
        self.processor = DataProcessor()
        self.opensearch_client_data = OpenSearchClient()  # For data/documents
        self.opensearch_client_prompts = OpenSearchClient()  # For prompts
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
            from ...config.settings import AppSettings

            datasource = DataSourceComponent()

            if active_tab == "opensearch-tab" and AppSettings.OPENSEARCH_ENABLED:
                return [datasource.create_opensearch_tab()]
            elif active_tab == "text-input-tab":
                return [datasource.create_text_input_tab()]
            else:
                return [datasource.create_file_upload_tab()]

        # Register callbacks for both data and prompts sections (only if OpenSearch is enabled)
        if AppSettings.OPENSEARCH_ENABLED:
            self._register_opensearch_callbacks("data", self.opensearch_client_data)
            self._register_opensearch_callbacks(
                "prompts", self.opensearch_client_prompts
            )

        # Register collapsible section callbacks
        self._register_collapse_callbacks()

        # Register text input callbacks
        self._register_text_input_callbacks()

    def _register_opensearch_callbacks(self, section_type, opensearch_client):
        """Register callbacks for a specific section (data or prompts)."""

        @callback(
            Output(f"{section_type}-auth-collapse", "is_open"),
            [Input(f"{section_type}-auth-toggle", "n_clicks")],
            [State(f"{section_type}-auth-collapse", "is_open")],
            prevent_initial_call=True,
        )
        def toggle_auth(n_clicks, is_open):
            if n_clicks:
                return not is_open
            return is_open

        @callback(
            Output(f"{section_type}-auth-toggle", "children"),
            [Input(f"{section_type}-auth-collapse", "is_open")],
            prevent_initial_call=False,
        )
        def update_auth_button_text(is_open):
            return "Hide Authentication" if is_open else "Show Authentication"

        @callback(
            [
                Output(f"{section_type}-connection-status", "children"),
                Output(f"{section_type}-field-mapping-section", "children"),
                Output(f"{section_type}-field-mapping-section", "style"),
                Output(f"{section_type}-load-data-section", "style"),
                Output(f"{section_type}-load-opensearch-data-btn", "disabled"),
                Output(f"{section_type}-embedding-field-dropdown", "options"),
                Output(f"{section_type}-text-field-dropdown", "options"),
                Output(f"{section_type}-id-field-dropdown", "options"),
                Output(f"{section_type}-category-field-dropdown", "options"),
                Output(f"{section_type}-subcategory-field-dropdown", "options"),
                Output(f"{section_type}-tags-field-dropdown", "options"),
            ],
            [Input(f"{section_type}-test-connection-btn", "n_clicks")],
            [
                State(f"{section_type}-opensearch-url", "value"),
                State(f"{section_type}-opensearch-index", "value"),
                State(f"{section_type}-opensearch-username", "value"),
                State(f"{section_type}-opensearch-password", "value"),
                State(f"{section_type}-opensearch-api-key", "value"),
            ],
            prevent_initial_call=True,
        )
        def test_opensearch_connection(
            n_clicks, url, index_name, username, password, api_key
        ):
            if not n_clicks or not url or not index_name:
                return (
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                )

            # Test connection
            success, message = opensearch_client.connect(
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
                opensearch_client.analyze_fields(index_name)
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
                field_suggestions, section_type
            )

            return (
                self._create_status_alert(f"✅ {message}", "success"),
                field_mapping_ui,
                {"display": "block"},
                {"display": "block"},
                False,
                [
                    {"label": field, "value": field}
                    for field in field_suggestions.get("embedding", [])
                ],
                [
                    {"label": field, "value": field}
                    for field in field_suggestions.get("text", [])
                ],
                [
                    {"label": field, "value": field}
                    for field in field_suggestions.get("id", [])
                ],
                [
                    {"label": field, "value": field}
                    for field in field_suggestions.get("category", [])
                ],
                [
                    {"label": field, "value": field}
                    for field in field_suggestions.get("subcategory", [])
                ],
                [
                    {"label": field, "value": field}
                    for field in field_suggestions.get("tags", [])
                ],
            )

        # Determine output target based on section type
        output_target = (
            "processed-data" if section_type == "data" else "processed-prompts"
        )

        @callback(
            [
                Output(output_target, "data", allow_duplicate=True),
                Output("opensearch-success-alert", "children", allow_duplicate=True),
                Output("opensearch-success-alert", "is_open", allow_duplicate=True),
                Output("opensearch-error-alert", "children", allow_duplicate=True),
                Output("opensearch-error-alert", "is_open", allow_duplicate=True),
            ],
            [Input(f"{section_type}-load-opensearch-data-btn", "n_clicks")],
            [
                State(f"{section_type}-opensearch-index", "value"),
                State(f"{section_type}-opensearch-query-size", "value"),
                State(f"{section_type}-embedding-field-dropdown-ui", "value"),
                State(f"{section_type}-text-field-dropdown-ui", "value"),
                State(f"{section_type}-id-field-dropdown-ui", "value"),
                State(f"{section_type}-category-field-dropdown-ui", "value"),
                State(f"{section_type}-subcategory-field-dropdown-ui", "value"),
                State(f"{section_type}-tags-field-dropdown-ui", "value"),
            ],
            prevent_initial_call=True,
        )
        def load_opensearch_data(
            n_clicks,
            index_name,
            query_size,
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
                # Validate and set query size
                if not query_size or query_size < 1:
                    query_size = AppSettings.OPENSEARCH_DEFAULT_SIZE
                elif query_size > 1000:
                    query_size = 1000  # Cap at reasonable maximum

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
                success, raw_documents, message = opensearch_client.fetch_data(
                    index_name, size=query_size
                )

                if not success:
                    return (
                        no_update,
                        "",
                        False,
                        f"❌ Failed to fetch {section_type}: {message}",
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
                        f"❌ {section_type.title()} processing error: {processed_data.error}",
                        True,
                    )

                success_message = f"✅ Successfully loaded {len(processed_data.documents)} {section_type} from OpenSearch"

                # Format for appropriate target (data vs prompts)
                if section_type == "data":
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
                else:  # prompts
                    return (
                        {
                            "prompts": [
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
            Output(f"{section_type}-embedding-field-dropdown", "value"),
            Input(f"{section_type}-embedding-field-dropdown-ui", "value"),
            prevent_initial_call=True,
        )
        def sync_embedding_dropdown(value):
            return value

        @callback(
            Output(f"{section_type}-text-field-dropdown", "value"),
            Input(f"{section_type}-text-field-dropdown-ui", "value"),
            prevent_initial_call=True,
        )
        def sync_text_dropdown(value):
            return value

        @callback(
            Output(f"{section_type}-id-field-dropdown", "value"),
            Input(f"{section_type}-id-field-dropdown-ui", "value"),
            prevent_initial_call=True,
        )
        def sync_id_dropdown(value):
            return value

        @callback(
            Output(f"{section_type}-category-field-dropdown", "value"),
            Input(f"{section_type}-category-field-dropdown-ui", "value"),
            prevent_initial_call=True,
        )
        def sync_category_dropdown(value):
            return value

        @callback(
            Output(f"{section_type}-subcategory-field-dropdown", "value"),
            Input(f"{section_type}-subcategory-field-dropdown-ui", "value"),
            prevent_initial_call=True,
        )
        def sync_subcategory_dropdown(value):
            return value

        @callback(
            Output(f"{section_type}-tags-field-dropdown", "value"),
            Input(f"{section_type}-tags-field-dropdown-ui", "value"),
            prevent_initial_call=True,
        )
        def sync_tags_dropdown(value):
            return value

    def _register_collapse_callbacks(self):
        """Register callbacks for collapsible sections."""

        # Data section collapse callback
        @callback(
            [
                Output("data-collapse", "is_open"),
                Output("data-collapse-icon", "className"),
            ],
            [Input("data-collapse-toggle", "n_clicks")],
            [State("data-collapse", "is_open")],
            prevent_initial_call=True,
        )
        def toggle_data_collapse(n_clicks, is_open):
            if n_clicks:
                new_state = not is_open
                icon_class = (
                    "fas fa-chevron-down me-2"
                    if new_state
                    else "fas fa-chevron-right me-2"
                )
                return new_state, icon_class
            return is_open, "fas fa-chevron-down me-2"

        # Prompts section collapse callback
        @callback(
            [
                Output("prompts-collapse", "is_open"),
                Output("prompts-collapse-icon", "className"),
            ],
            [Input("prompts-collapse-toggle", "n_clicks")],
            [State("prompts-collapse", "is_open")],
            prevent_initial_call=True,
        )
        def toggle_prompts_collapse(n_clicks, is_open):
            if n_clicks:
                new_state = not is_open
                icon_class = (
                    "fas fa-chevron-down me-2"
                    if new_state
                    else "fas fa-chevron-right me-2"
                )
                return new_state, icon_class
            return is_open, "fas fa-chevron-down me-2"

    def _register_text_input_callbacks(self):
        """Register callbacks for text input functionality."""

        # Text length counter callback
        @callback(
            Output("text-length-counter", "children"),
            Input("text-input-area", "value"),
            prevent_initial_call=False,
        )
        def update_text_length_counter(text_value):
            if not text_value:
                return "0"
            return f"{len(text_value):,}"

        # Generate button enable/disable callback
        @callback(
            [
                Output("generate-embeddings-btn", "disabled"),
                Output("generation-help", "children"),
                Output("generation-help", "color"),
            ],
            [
                Input("text-input-area", "value"),
                Input("model-selection", "value"),
            ],
            prevent_initial_call=False,
        )
        def toggle_generate_button(text_value, model_name):
            import dash_bootstrap_components as dbc

            if not text_value or not text_value.strip():
                return (
                    True,
                    dbc.Alert(
                        [
                            html.I(className="fas fa-info-circle me-2"),
                            "Enter some text above to enable embedding generation.",
                        ],
                        color="light",
                    ),
                    "light",
                )

            if not model_name:
                return (
                    True,
                    dbc.Alert(
                        [
                            html.I(className="fas fa-exclamation-triangle me-2"),
                            "Select an embedding model to continue.",
                        ],
                        color="warning",
                    ),
                    "warning",
                )

            text_length = len(text_value.strip())
            if text_length > AppSettings.MAX_TEXT_LENGTH:
                return (
                    True,
                    dbc.Alert(
                        [
                            html.I(className="fas fa-exclamation-triangle me-2"),
                            f"Text too long ({text_length:,} characters). Maximum allowed: {AppSettings.MAX_TEXT_LENGTH:,} characters.",
                        ],
                        color="danger",
                    ),
                    "danger",
                )

            return (
                False,
                dbc.Alert(
                    [
                        html.I(className="fas fa-check-circle me-2"),
                        f"Ready to generate embeddings for {text_length:,} characters using {model_name}.",
                    ],
                    color="success",
                ),
                "success",
            )

        # Clear text callback
        @callback(
            Output("text-input-area", "value"),
            [Input("clear-text-btn", "n_clicks"), Input("load-sample-btn", "n_clicks")],
            prevent_initial_call=True,
        )
        def handle_text_input_actions(clear_clicks, load_clicks):
            from dash import ctx

            if not ctx.triggered:
                return no_update

            button_id = ctx.triggered[0]["prop_id"].split(".")[0]

            if button_id == "clear-text-btn" and clear_clicks:
                return ""
            elif button_id == "load-sample-btn" and load_clicks:
                return self._load_sample_text()

            return no_update

        # Model info callback
        @callback(
            Output("model-info", "children"),
            Input("model-selection", "value"),
            prevent_initial_call=False,
        )
        def update_model_info(model_name):
            if not model_name:
                return html.Span("Please select a model", className="text-muted")

            from ...config.settings import AppSettings

            settings = AppSettings()

            for model in settings.AVAILABLE_MODELS:
                if model["name"] == model_name:
                    return html.Div(
                        [
                            html.Strong(
                                f"Dimensions: {model['dimensions']} | Context Length: {model['context_length']}"
                            ),
                            html.Br(),
                            html.Span(model["description"]),
                            html.Br(),
                            html.Small(
                                f"Multilingual: {'Yes' if model.get('multilingual', False) else 'No'} | Size: {model['size']}",
                                className="text-muted",
                            ),
                        ]
                    )

            return html.Span("Model information not available", className="text-muted")

        # Process client-side embeddings result callback
        @callback(
            [
                Output("processed-data", "data", allow_duplicate=True),
                Output("text-input-status", "children"),
                Output("text-input-status", "color"),
                Output("text-input-status", "style"),
                Output("generate-embeddings-btn", "disabled", allow_duplicate=True),
            ],
            [Input("embeddings-generated-trigger", "data")],
            prevent_initial_call=True,
        )
        def process_embeddings_result(embeddings_data):
            """Process embeddings generated client-side."""
            if not embeddings_data:
                return no_update, no_update, no_update, no_update, no_update

            # Check if this is a request trigger (contains textContent) vs actual embeddings data
            if isinstance(embeddings_data, dict) and "textContent" in embeddings_data:
                # This is a processing request trigger, not the actual results
                # The JavaScript will handle the async processing and update the UI directly
                return no_update, no_update, no_update, no_update, no_update

            processed_data = self.processor.process_client_embeddings(embeddings_data)

            if processed_data.error:
                return (
                    {"error": processed_data.error},
                    f"❌ Error: {processed_data.error}",
                    "danger",
                    {"display": "block"},
                    False,
                )

            return (
                {
                    "documents": [
                        self._document_to_dict(doc) for doc in processed_data.documents
                    ],
                    "embeddings": processed_data.embeddings.tolist(),
                },
                f"✅ Generated embeddings for {len(processed_data.documents)} text chunks",
                "success",
                {"display": "block"},
                False,
            )

    def _load_sample_text(self):
        """Load sample text from assets/sample-txt.md file."""
        import os

        try:
            # Get the project root directory (four levels up from this file)
            current_file = os.path.abspath(__file__)
            project_root = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
                )
            )
            sample_file_path = os.path.join(project_root, "assets", "sample-txt.md")

            if os.path.exists(sample_file_path):
                with open(sample_file_path, "r", encoding="utf-8") as file:
                    return file.read()
            else:
                # Fallback sample text if file doesn't exist
                return """The sun peeked through the clouds after a drizzly morning.
A gentle breeze rustled the leaves as we walked along the shoreline.
Heavy rains caused flooding in several low-lying neighborhoods.
It was so hot that even the birds sought shade under the palm trees.
By midnight, the temperature had dropped below freezing.

The new smartphone features a foldable display and 5G connectivity.
In the world of AI, transformers have revolutionized natural language processing.
Quantum computing promises to solve problems beyond classical computers' reach.
Blockchain technology is being explored for secure voting systems.
Virtual reality headsets are becoming more affordable and accessible.

Preheat the oven to 375°F before you start mixing the batter.
She finely chopped the garlic and sautéed it in two tablespoons of olive oil.
A pinch of saffron adds a beautiful color and aroma to traditional paella.
If the soup is too salty, add a peeled potato to absorb excess sodium.
Let the bread dough rise for at least an hour in a warm, draft-free spot."""

        except Exception:
            # Return a simple fallback if there's any error
            return "This is sample text for testing embedding generation. You can replace this with your own text."

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
