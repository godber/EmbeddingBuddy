import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Optional
from ..models.schemas import Document, PlotData
from .colors import ColorMapper


class PlotFactory:
    def __init__(self):
        self.color_mapper = ColorMapper()

    def create_plot(
        self,
        plot_data: PlotData,
        dimensions: str = "3d",
        color_by: str = "category",
        method: str = "PCA",
        show_prompts: Optional[List[str]] = None,
    ) -> go.Figure:
        if plot_data.prompts and show_prompts and "show" in show_prompts:
            return self._create_dual_plot(plot_data, dimensions, color_by, method)
        else:
            return self._create_single_plot(plot_data, dimensions, color_by, method)

    def _create_single_plot(
        self, plot_data: PlotData, dimensions: str, color_by: str, method: str
    ) -> go.Figure:
        df = self._prepare_dataframe(
            plot_data.documents, plot_data.coordinates, dimensions
        )
        color_values = self.color_mapper.create_color_mapping(
            plot_data.documents, color_by
        )

        hover_fields = ["id", "text_preview", "category", "subcategory", "tags_str"]

        if dimensions == "3d":
            fig = px.scatter_3d(
                df,
                x="x",
                y="y",
                z="z",
                color=color_values,
                hover_data=hover_fields,
                title=f"3D Embedding Visualization - {method} (colored by {color_by})",
            )
            fig.update_traces(marker=dict(size=5))
        else:
            fig = px.scatter(
                df,
                x="x",
                y="y",
                color=color_values,
                hover_data=hover_fields,
                title=f"2D Embedding Visualization - {method} (colored by {color_by})",
            )
            fig.update_traces(marker=dict(size=8))

        fig.update_layout(height=None, autosize=True, margin=dict(l=0, r=0, t=50, b=0))
        return fig

    def _create_dual_plot(
        self, plot_data: PlotData, dimensions: str, color_by: str, method: str
    ) -> go.Figure:
        fig = go.Figure()

        doc_df = self._prepare_dataframe(
            plot_data.documents, plot_data.coordinates, dimensions
        )
        doc_color_values = self.color_mapper.create_color_mapping(
            plot_data.documents, color_by
        )

        hover_fields = ["id", "text_preview", "category", "subcategory", "tags_str"]

        if dimensions == "3d":
            doc_fig = px.scatter_3d(
                doc_df,
                x="x",
                y="y",
                z="z",
                color=doc_color_values,
                hover_data=hover_fields,
            )
        else:
            doc_fig = px.scatter(
                doc_df,
                x="x",
                y="y",
                color=doc_color_values,
                hover_data=hover_fields,
            )

        for trace in doc_fig.data:
            trace.name = f"Documents - {trace.name}"
            if dimensions == "3d":
                trace.marker.size = 5
                trace.marker.symbol = "circle"
            else:
                trace.marker.size = 8
                trace.marker.symbol = "circle"
            trace.marker.opacity = 1.0
            fig.add_trace(trace)

        if plot_data.prompts and plot_data.prompt_coordinates is not None:
            prompt_df = self._prepare_dataframe(
                plot_data.prompts, plot_data.prompt_coordinates, dimensions
            )
            prompt_color_values = self.color_mapper.create_color_mapping(
                plot_data.prompts, color_by
            )

            if dimensions == "3d":
                prompt_fig = px.scatter_3d(
                    prompt_df,
                    x="x",
                    y="y",
                    z="z",
                    color=prompt_color_values,
                    hover_data=hover_fields,
                )
            else:
                prompt_fig = px.scatter(
                    prompt_df,
                    x="x",
                    y="y",
                    color=prompt_color_values,
                    hover_data=hover_fields,
                )

            for trace in prompt_fig.data:
                if hasattr(trace.marker, "color") and isinstance(
                    trace.marker.color, str
                ):
                    trace.marker.color = self.color_mapper.to_grayscale_hex(
                        trace.marker.color
                    )

                trace.name = f"Prompts - {trace.name}"
                if dimensions == "3d":
                    trace.marker.size = 6
                    trace.marker.symbol = "diamond"
                else:
                    trace.marker.size = 10
                    trace.marker.symbol = "diamond"
                trace.marker.opacity = 0.8
                fig.add_trace(trace)

        title = f"{dimensions.upper()} Embedding Visualization - {method} (colored by {color_by})"
        fig.update_layout(
            title=title, height=None, autosize=True, margin=dict(l=0, r=0, t=50, b=0)
        )

        return fig

    def _prepare_dataframe(
        self, documents: List[Document], coordinates, dimensions: str
    ) -> pd.DataFrame:
        df_data = []
        for i, doc in enumerate(documents):
            row = {
                "id": doc.id,
                "text": doc.text,
                "text_preview": doc.text[:100] + "..."
                if len(doc.text) > 100
                else doc.text,
                "category": doc.category,
                "subcategory": doc.subcategory,
                "tags_str": ", ".join(doc.tags) if doc.tags else "None",
                "x": coordinates[i, 0],
                "y": coordinates[i, 1],
            }
            if dimensions == "3d":
                row["z"] = coordinates[i, 2]
            df_data.append(row)

        return pd.DataFrame(df_data)
