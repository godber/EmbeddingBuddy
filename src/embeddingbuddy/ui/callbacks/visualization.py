import numpy as np
from dash import callback, Input, Output
import plotly.graph_objects as go
from ...models.reducers import ReducerFactory
from ...models.schemas import Document, PlotData
from ...visualization.plots import PlotFactory


class VisualizationCallbacks:
    def __init__(self):
        self.plot_factory = PlotFactory()
        self._register_callbacks()

    def _register_callbacks(self):
        @callback(
            Output("embedding-plot", "figure"),
            [
                Input("processed-data", "data"),
                Input("processed-prompts", "data"),
                Input("method-dropdown", "value"),
                Input("color-dropdown", "value"),
                Input("dimension-toggle", "value"),
                Input("show-prompts-toggle", "value"),
            ],
        )
        def update_plot(data, prompts_data, method, color_by, dimensions, show_prompts):
            if not data or "error" in data:
                return go.Figure().add_annotation(
                    text="Upload a valid NDJSON file to see visualization",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    xanchor="center",
                    yanchor="middle",
                    showarrow=False,
                    font=dict(size=16),
                )

            try:
                doc_embeddings = np.array(data["embeddings"])
                all_embeddings = doc_embeddings
                has_prompts = (
                    prompts_data
                    and "error" not in prompts_data
                    and prompts_data.get("prompts")
                )

                if has_prompts:
                    prompt_embeddings = np.array(prompts_data["embeddings"])
                    all_embeddings = np.vstack([doc_embeddings, prompt_embeddings])

                n_components = 3 if dimensions == "3d" else 2

                reducer = ReducerFactory.create_reducer(
                    method, n_components=n_components
                )
                reduced_data = reducer.fit_transform(all_embeddings)

                doc_reduced = reduced_data.reduced_embeddings[: len(doc_embeddings)]
                prompt_reduced = None
                if has_prompts:
                    prompt_reduced = reduced_data.reduced_embeddings[
                        len(doc_embeddings) :
                    ]

                documents = [self._dict_to_document(doc) for doc in data["documents"]]
                prompts = None
                if has_prompts:
                    prompts = [
                        self._dict_to_document(prompt)
                        for prompt in prompts_data["prompts"]
                    ]

                plot_data = PlotData(
                    documents=documents,
                    coordinates=doc_reduced,
                    prompts=prompts,
                    prompt_coordinates=prompt_reduced,
                )

                return self.plot_factory.create_plot(
                    plot_data, dimensions, color_by, reduced_data.method, show_prompts
                )

            except Exception as e:
                return go.Figure().add_annotation(
                    text=f"Error creating visualization: {str(e)}",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    xanchor="center",
                    yanchor="middle",
                    showarrow=False,
                    font=dict(size=16),
                )

    @staticmethod
    def _dict_to_document(doc_dict):
        return Document(
            id=doc_dict["id"],
            text=doc_dict["text"],
            embedding=doc_dict["embedding"],
            category=doc_dict.get("category"),
            subcategory=doc_dict.get("subcategory"),
            tags=doc_dict.get("tags", []),
        )
