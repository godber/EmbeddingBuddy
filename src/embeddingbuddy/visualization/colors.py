from typing import List
import plotly.colors as pc
from ..models.schemas import Document


class ColorMapper:
    @staticmethod
    def create_color_mapping(documents: List[Document], color_by: str) -> List[str]:
        if color_by == "category":
            return [doc.category for doc in documents]
        elif color_by == "subcategory":
            return [doc.subcategory for doc in documents]
        elif color_by == "tags":
            return [", ".join(doc.tags) if doc.tags else "No tags" for doc in documents]
        else:
            return ["All"] * len(documents)

    @staticmethod
    def to_grayscale_hex(color_str: str) -> str:
        try:
            if color_str.startswith("#"):
                rgb = tuple(int(color_str[i : i + 2], 16) for i in (1, 3, 5))
            else:
                rgb = pc.hex_to_rgb(
                    pc.convert_colors_to_same_type([color_str], colortype="hex")[0][0]
                )

            gray_value = int(0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])
            gray_rgb = (
                gray_value * 0.7 + rgb[0] * 0.3,
                gray_value * 0.7 + rgb[1] * 0.3,
                gray_value * 0.7 + rgb[2] * 0.3,
            )
            return f"rgb({int(gray_rgb[0])},{int(gray_rgb[1])},{int(gray_rgb[2])})"
        except:  # noqa: E722
            return "rgb(128,128,128)"
