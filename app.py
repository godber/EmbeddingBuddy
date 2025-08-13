import json
import uuid
from io import StringIO
import base64

import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import umap
from openTSNE import TSNE


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def parse_ndjson(contents):
    """Parse NDJSON content and return list of documents."""
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    text_content = decoded.decode('utf-8')
    
    documents = []
    for line in text_content.strip().split('\n'):
        if line.strip():
            doc = json.loads(line)
            if 'id' not in doc:
                doc['id'] = str(uuid.uuid4())
            documents.append(doc)
    return documents

def apply_dimensionality_reduction(embeddings, method='pca', n_components=3):
    """Apply dimensionality reduction to embeddings."""
    if method == 'pca':
        reducer = PCA(n_components=n_components)
        reduced = reducer.fit_transform(embeddings)
        variance_explained = reducer.explained_variance_ratio_
        return reduced, variance_explained
    elif method == 'tsne':
        reducer = TSNE(n_components=n_components, random_state=42)
        reduced = reducer.fit(embeddings)
        return reduced, None
    elif method == 'umap':
        reducer = umap.UMAP(n_components=n_components, random_state=42)
        reduced = reducer.fit_transform(embeddings)
        return reduced, None
    else:
        raise ValueError(f"Unknown method: {method}")

def create_color_mapping(documents, color_by):
    """Create color mapping for documents based on specified field."""
    if color_by == 'category':
        values = [doc.get('category', 'Unknown') for doc in documents]
    elif color_by == 'subcategory':
        values = [doc.get('subcategory', 'Unknown') for doc in documents]
    elif color_by == 'tags':
        values = [', '.join(doc.get('tags', [])) if doc.get('tags') else 'No tags' for doc in documents]
    else:
        values = ['All'] * len(documents)
    
    return values

def create_plot(df, dimensions='3d', color_by='category', method='PCA'):
    """Create plotly scatter plot."""
    color_values = create_color_mapping(df.to_dict('records'), color_by)
    
    # Truncate text for hover display
    df_display = df.copy()
    df_display['text_preview'] = df_display['text'].apply(lambda x: x[:100] + "..." if len(x) > 100 else x)
    
    # Include all metadata fields in hover
    hover_fields = ['id', 'text_preview', 'category', 'subcategory']
    # Add tags as a string for hover
    df_display['tags_str'] = df_display['tags'].apply(lambda x: ', '.join(x) if x else 'None')
    hover_fields.append('tags_str')
    
    if dimensions == '3d':
        fig = px.scatter_3d(
            df_display, x='dim_1', y='dim_2', z='dim_3',
            color=color_values,
            hover_data=hover_fields,
            title=f'3D Embedding Visualization - {method} (colored by {color_by})'
        )
        fig.update_traces(marker=dict(size=5))
    else:
        fig = px.scatter(
            df_display, x='dim_1', y='dim_2',
            color=color_values,
            hover_data=hover_fields,
            title=f'2D Embedding Visualization - {method} (colored by {color_by})'
        )
        fig.update_traces(marker=dict(size=8))
    
    fig.update_layout(
        height=None,  # Let CSS height control this
        autosize=True,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    return fig

def create_dual_plot(doc_df, prompt_df, dimensions='3d', color_by='category', method='PCA', show_prompts=None):
    """Create plotly scatter plot with separate traces for documents and prompts."""
    
    # Create the base figure
    fig = go.Figure()
    
    # Helper function to convert colors to grayscale
    def to_grayscale_hex(color_str):
        """Convert a color to grayscale while maintaining some distinction."""
        import plotly.colors as pc
        # Try to get RGB values from the color
        try:
            if color_str.startswith('#'):
                # Hex color
                rgb = tuple(int(color_str[i:i+2], 16) for i in (1, 3, 5))
            else:
                # Named color or other format - convert through plotly
                rgb = pc.hex_to_rgb(pc.convert_colors_to_same_type([color_str], colortype='hex')[0][0])
            
            # Convert to grayscale using luminance formula, but keep some color
            gray_value = int(0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])
            # Make it a bit more gray but not completely
            gray_rgb = (gray_value * 0.7 + rgb[0] * 0.3, 
                       gray_value * 0.7 + rgb[1] * 0.3, 
                       gray_value * 0.7 + rgb[2] * 0.3)
            return f'rgb({int(gray_rgb[0])},{int(gray_rgb[1])},{int(gray_rgb[2])})'
        except:
            return 'rgb(128,128,128)'  # fallback gray
    
    # Create document plot using plotly express for consistent colors
    doc_color_values = create_color_mapping(doc_df.to_dict('records'), color_by)
    doc_df_display = doc_df.copy()
    doc_df_display['text_preview'] = doc_df_display['text'].apply(lambda x: x[:100] + "..." if len(x) > 100 else x)
    doc_df_display['tags_str'] = doc_df_display['tags'].apply(lambda x: ', '.join(x) if x else 'None')
    
    hover_fields = ['id', 'text_preview', 'category', 'subcategory', 'tags_str']
    
    # Create documents plot to get the color mapping
    if dimensions == '3d':
        doc_fig = px.scatter_3d(
            doc_df_display, x='dim_1', y='dim_2', z='dim_3',
            color=doc_color_values,
            hover_data=hover_fields
        )
    else:
        doc_fig = px.scatter(
            doc_df_display, x='dim_1', y='dim_2',
            color=doc_color_values,
            hover_data=hover_fields
        )
    
    # Add document traces to main figure
    for trace in doc_fig.data:
        trace.name = f'Documents - {trace.name}'
        if dimensions == '3d':
            trace.marker.size = 5
            trace.marker.symbol = 'circle'
        else:
            trace.marker.size = 8
            trace.marker.symbol = 'circle'
        trace.marker.opacity = 1.0
        fig.add_trace(trace)
    
    # Add prompt traces if they exist
    if prompt_df is not None and show_prompts and 'show' in show_prompts:
        prompt_color_values = create_color_mapping(prompt_df.to_dict('records'), color_by)
        prompt_df_display = prompt_df.copy()
        prompt_df_display['text_preview'] = prompt_df_display['text'].apply(lambda x: x[:100] + "..." if len(x) > 100 else x)
        prompt_df_display['tags_str'] = prompt_df_display['tags'].apply(lambda x: ', '.join(x) if x else 'None')
        
        # Create prompts plot to get consistent color grouping
        if dimensions == '3d':
            prompt_fig = px.scatter_3d(
                prompt_df_display, x='dim_1', y='dim_2', z='dim_3',
                color=prompt_color_values,
                hover_data=hover_fields
            )
        else:
            prompt_fig = px.scatter(
                prompt_df_display, x='dim_1', y='dim_2',
                color=prompt_color_values,
                hover_data=hover_fields
            )
        
        # Add prompt traces with grayed colors
        for trace in prompt_fig.data:
            # Convert the color to grayscale
            original_color = trace.marker.color
            if hasattr(trace.marker, 'color') and isinstance(trace.marker.color, str):
                trace.marker.color = to_grayscale_hex(trace.marker.color)
            
            trace.name = f'Prompts - {trace.name}'
            if dimensions == '3d':
                trace.marker.size = 6
                trace.marker.symbol = 'diamond'
            else:
                trace.marker.size = 10
                trace.marker.symbol = 'diamond'
            trace.marker.opacity = 0.8
            fig.add_trace(trace)
    
    title = f'{dimensions.upper()} Embedding Visualization - {method} (colored by {color_by})'
    fig.update_layout(
        title=title,
        height=None,
        autosize=True,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    return fig

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("EmbeddingBuddy", className="text-center mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        # Left sidebar with controls
        dbc.Col([
            html.H5("Upload Data", className="mb-3"),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin-bottom': '20px'
                },
                multiple=False
            ),
            
            dcc.Upload(
                id='upload-prompts',
                children=html.Div([
                    'Drag and Drop Prompts or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin-bottom': '20px',
                    'borderColor': '#28a745'
                },
                multiple=False
            ),
            
            dbc.Button(
                "Reset All Data",
                id='reset-button',
                color='danger',
                outline=True,
                size='sm',
                className='mb-3',
                style={'width': '100%'}
            ),
            
            html.H5("Visualization Controls", className="mb-3"),
            
            dbc.Label("Method:"),
            dcc.Dropdown(
                id='method-dropdown',
                options=[
                    {'label': 'PCA', 'value': 'pca'},
                    {'label': 't-SNE', 'value': 'tsne'},
                    {'label': 'UMAP', 'value': 'umap'}
                ],
                value='pca',
                style={'margin-bottom': '15px'}
            ),
            
            dbc.Label("Color by:"),
            dcc.Dropdown(
                id='color-dropdown',
                options=[
                    {'label': 'Category', 'value': 'category'},
                    {'label': 'Subcategory', 'value': 'subcategory'},
                    {'label': 'Tags', 'value': 'tags'}
                ],
                value='category',
                style={'margin-bottom': '15px'}
            ),
            
            dbc.Label("Dimensions:"),
            dcc.RadioItems(
                id='dimension-toggle',
                options=[
                    {'label': '2D', 'value': '2d'},
                    {'label': '3D', 'value': '3d'}
                ],
                value='3d',
                style={'margin-bottom': '20px'}
            ),
            
            dbc.Label("Show Prompts:"),
            dcc.Checklist(
                id='show-prompts-toggle',
                options=[{'label': 'Show prompts on plot', 'value': 'show'}],
                value=['show'],
                style={'margin-bottom': '20px'}
            ),
            
            html.H5("Point Details", className="mb-3"),
            html.Div(id='point-details', children="Click on a point to see details")
            
        ], width=3, style={'padding-right': '20px'}),
        
        # Main visualization area
        dbc.Col([
            dcc.Graph(
                id='embedding-plot',
                style={'height': '85vh', 'width': '100%'},
                config={'responsive': True, 'displayModeBar': True}
            )
        ], width=9)
    ]),
    
    dcc.Store(id='processed-data'),
    dcc.Store(id='processed-prompts')
], fluid=True)

@callback(
    Output('processed-data', 'data'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def process_uploaded_file(contents, filename):
    if contents is None:
        return None
    
    try:
        documents = parse_ndjson(contents)
        embeddings = np.array([doc['embedding'] for doc in documents])
        
        # Store original embeddings and documents
        return {
            'documents': documents,
            'embeddings': embeddings.tolist()
        }
    except Exception as e:
        return {'error': str(e)}

@callback(
    Output('processed-prompts', 'data'),
    Input('upload-prompts', 'contents'),
    State('upload-prompts', 'filename')
)
def process_uploaded_prompts(contents, filename):
    if contents is None:
        return None
    
    try:
        prompts = parse_ndjson(contents)
        embeddings = np.array([prompt['embedding'] for prompt in prompts])
        
        # Store original embeddings and prompts
        return {
            'prompts': prompts,
            'embeddings': embeddings.tolist()
        }
    except Exception as e:
        return {'error': str(e)}

@callback(
    Output('embedding-plot', 'figure'),
    [Input('processed-data', 'data'),
     Input('processed-prompts', 'data'),
     Input('method-dropdown', 'value'),
     Input('color-dropdown', 'value'),
     Input('dimension-toggle', 'value'),
     Input('show-prompts-toggle', 'value')]
)
def update_plot(data, prompts_data, method, color_by, dimensions, show_prompts):
    if not data or 'error' in data:
        return go.Figure().add_annotation(
            text="Upload a valid NDJSON file to see visualization",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
    
    # Prepare embeddings for dimensionality reduction
    doc_embeddings = np.array(data['embeddings'])
    all_embeddings = doc_embeddings
    has_prompts = prompts_data and 'error' not in prompts_data and prompts_data.get('prompts')
    
    if has_prompts:
        prompt_embeddings = np.array(prompts_data['embeddings'])
        all_embeddings = np.vstack([doc_embeddings, prompt_embeddings])
    
    n_components = 3 if dimensions == '3d' else 2
    
    # Apply dimensionality reduction to combined data
    reduced, variance_explained = apply_dimensionality_reduction(
        all_embeddings, method=method, n_components=n_components
    )
    
    # Split reduced embeddings back
    doc_reduced = reduced[:len(doc_embeddings)]
    prompt_reduced = reduced[len(doc_embeddings):] if has_prompts else None
    
    # Create dataframes
    doc_df_data = []
    for i, doc in enumerate(data['documents']):
        row = {
            'id': doc['id'],
            'text': doc['text'],
            'category': doc.get('category', 'Unknown'),
            'subcategory': doc.get('subcategory', 'Unknown'),
            'tags': doc.get('tags', []),
            'dim_1': doc_reduced[i, 0],
            'dim_2': doc_reduced[i, 1],
            'type': 'document'
        }
        if dimensions == '3d':
            row['dim_3'] = doc_reduced[i, 2]
        doc_df_data.append(row)
    
    doc_df = pd.DataFrame(doc_df_data)
    
    prompt_df = None
    if has_prompts and prompt_reduced is not None:
        prompt_df_data = []
        for i, prompt in enumerate(prompts_data['prompts']):
            row = {
                'id': prompt['id'],
                'text': prompt['text'],
                'category': prompt.get('category', 'Unknown'),
                'subcategory': prompt.get('subcategory', 'Unknown'),
                'tags': prompt.get('tags', []),
                'dim_1': prompt_reduced[i, 0],
                'dim_2': prompt_reduced[i, 1],
                'type': 'prompt'
            }
            if dimensions == '3d':
                row['dim_3'] = prompt_reduced[i, 2]
            prompt_df_data.append(row)
        
        prompt_df = pd.DataFrame(prompt_df_data)
    
    return create_dual_plot(doc_df, prompt_df, dimensions, color_by, method.upper(), show_prompts)

@callback(
    Output('point-details', 'children'),
    Input('embedding-plot', 'clickData'),
    [State('processed-data', 'data'),
     State('processed-prompts', 'data')]
)
def display_click_data(clickData, data, prompts_data):
    if not clickData or not data:
        return "Click on a point to see details"
    
    # Get point info from click
    point_data = clickData['points'][0]
    trace_name = point_data.get('fullData', {}).get('name', 'Documents')
    
    if 'pointIndex' in point_data:
        point_index = point_data['pointIndex']
    elif 'pointNumber' in point_data:
        point_index = point_data['pointNumber']
    else:
        return "Could not identify clicked point"
    
    # Determine which dataset this point belongs to
    if trace_name == 'Prompts' and prompts_data and 'prompts' in prompts_data:
        item = prompts_data['prompts'][point_index]
        item_type = 'Prompt'
    else:
        item = data['documents'][point_index]
        item_type = 'Document'
    
    return dbc.Card([
        dbc.CardBody([
            html.H5(f"{item_type}: {item['id']}", className="card-title"),
            html.P(f"Text: {item['text']}", className="card-text"),
            html.P(f"Category: {item.get('category', 'Unknown')}", className="card-text"),
            html.P(f"Subcategory: {item.get('subcategory', 'Unknown')}", className="card-text"),
            html.P(f"Tags: {', '.join(item.get('tags', [])) if item.get('tags') else 'None'}", className="card-text"),
            html.P(f"Type: {item_type}", className="card-text text-muted")
        ])
    ])

@callback(
    [Output('processed-data', 'data', allow_duplicate=True),
     Output('processed-prompts', 'data', allow_duplicate=True),
     Output('point-details', 'children', allow_duplicate=True)],
    Input('reset-button', 'n_clicks'),
    prevent_initial_call=True
)
def reset_data(n_clicks):
    if n_clicks is None or n_clicks == 0:
        return dash.no_update, dash.no_update, dash.no_update
    
    return None, None, "Click on a point to see details"

if __name__ == '__main__':
    app.run(debug=True)