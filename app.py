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
    
    dcc.Store(id='processed-data')
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
    Output('embedding-plot', 'figure'),
    [Input('processed-data', 'data'),
     Input('method-dropdown', 'value'),
     Input('color-dropdown', 'value'),
     Input('dimension-toggle', 'value')]
)
def update_plot(data, method, color_by, dimensions):
    if not data or 'error' in data:
        return go.Figure().add_annotation(
            text="Upload a valid NDJSON file to see visualization",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
    
    # Get embeddings and apply selected method
    embeddings = np.array(data['embeddings'])
    n_components = 3 if dimensions == '3d' else 2
    
    reduced, variance_explained = apply_dimensionality_reduction(
        embeddings, method=method, n_components=n_components
    )
    
    # Create dataframe with reduced dimensions
    df_data = []
    for i, doc in enumerate(data['documents']):
        row = {
            'id': doc['id'],
            'text': doc['text'],
            'category': doc.get('category', 'Unknown'),
            'subcategory': doc.get('subcategory', 'Unknown'),
            'tags': doc.get('tags', []),
            'dim_1': reduced[i, 0],
            'dim_2': reduced[i, 1]
        }
        if dimensions == '3d':
            row['dim_3'] = reduced[i, 2]
        df_data.append(row)
    
    df = pd.DataFrame(df_data)
    
    return create_plot(df, dimensions, color_by, method.upper())

@callback(
    Output('point-details', 'children'),
    Input('embedding-plot', 'clickData'),
    State('processed-data', 'data')
)
def display_click_data(clickData, data):
    if not clickData or not data:
        return "Click on a point to see details"
    
    # Get point index - try different possible keys
    point_data = clickData['points'][0]
    if 'pointIndex' in point_data:
        point_index = point_data['pointIndex']
    elif 'pointNumber' in point_data:
        point_index = point_data['pointNumber']
    else:
        return "Could not identify clicked point"
    
    doc = data['documents'][point_index]
    
    return dbc.Card([
        dbc.CardBody([
            html.H5(f"Document: {doc['id']}", className="card-title"),
            html.P(f"Text: {doc['text']}", className="card-text"),
            html.P(f"Category: {doc.get('category', 'Unknown')}", className="card-text"),
            html.P(f"Subcategory: {doc.get('subcategory', 'Unknown')}", className="card-text"),
            html.P(f"Tags: {', '.join(doc.get('tags', [])) if doc.get('tags') else 'None'}", className="card-text")
        ])
    ])

if __name__ == '__main__':
    app.run(debug=True)