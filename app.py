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

def apply_pca(embeddings, n_components=3):
    """Apply PCA to embeddings."""
    pca = PCA(n_components=n_components)
    reduced = pca.fit_transform(embeddings)
    return reduced, pca.explained_variance_ratio_

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

def create_plot(df, dimensions='3d', color_by='category'):
    """Create plotly scatter plot."""
    color_values = create_color_mapping(df.to_dict('records'), color_by)
    
    if dimensions == '3d':
        fig = px.scatter_3d(
            df, x='pca_1', y='pca_2', z='pca_3',
            color=color_values,
            hover_data=['id', 'text'],
            title=f'3D Embedding Visualization (colored by {color_by})'
        )
        fig.update_traces(marker=dict(size=5))
    else:
        fig = px.scatter(
            df, x='pca_1', y='pca_2',
            color=color_values,
            hover_data=['id', 'text'],
            title=f'2D Embedding Visualization (colored by {color_by})'
        )
        fig.update_traces(marker=dict(size=8))
    
    fig.update_layout(height=600)
    return fig

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("EmbeddingBuddy", className="text-center mb-4"),
            html.P("Upload NDJSON file with embeddings to visualize", className="text-center text-muted")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
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
                    'margin': '10px'
                },
                multiple=False
            )
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Label("Color by:"),
            dcc.Dropdown(
                id='color-dropdown',
                options=[
                    {'label': 'Category', 'value': 'category'},
                    {'label': 'Subcategory', 'value': 'subcategory'},
                    {'label': 'Tags', 'value': 'tags'}
                ],
                value='category',
                style={'margin-bottom': '10px'}
            )
        ], width=6),
        dbc.Col([
            dbc.Label("Dimensions:"),
            dcc.RadioItems(
                id='dimension-toggle',
                options=[
                    {'label': '2D', 'value': '2d'},
                    {'label': '3D', 'value': '3d'}
                ],
                value='3d',
                inline=True
            )
        ], width=6)
    ], className="mb-3"),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='embedding-plot')
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Div(id='point-details', style={'margin-top': '20px'})
        ])
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
        
        # Apply PCA
        pca_2d, var_2d = apply_pca(embeddings, n_components=2)
        pca_3d, var_3d = apply_pca(embeddings, n_components=3)
        
        # Create dataframe
        df_data = []
        for i, doc in enumerate(documents):
            df_data.append({
                'id': doc['id'],
                'text': doc['text'],
                'category': doc.get('category', 'Unknown'),
                'subcategory': doc.get('subcategory', 'Unknown'),
                'tags': doc.get('tags', []),
                'pca_1': pca_3d[i, 0],
                'pca_2': pca_3d[i, 1],
                'pca_3': pca_3d[i, 2],
                'pca_1_2d': pca_2d[i, 0],
                'pca_2_2d': pca_2d[i, 1]
            })
        
        return {
            'documents': df_data,
            'variance_explained_2d': var_2d.tolist(),
            'variance_explained_3d': var_3d.tolist()
        }
    except Exception as e:
        return {'error': str(e)}

@callback(
    Output('embedding-plot', 'figure'),
    [Input('processed-data', 'data'),
     Input('color-dropdown', 'value'),
     Input('dimension-toggle', 'value')]
)
def update_plot(data, color_by, dimensions):
    if not data or 'error' in data:
        return go.Figure().add_annotation(
            text="Upload a valid NDJSON file to see visualization",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
    
    df = pd.DataFrame(data['documents'])
    
    if dimensions == '2d':
        df['pca_1'] = df['pca_1_2d']
        df['pca_2'] = df['pca_2_2d']
    
    return create_plot(df, dimensions, color_by)

@callback(
    Output('point-details', 'children'),
    Input('embedding-plot', 'clickData'),
    State('processed-data', 'data')
)
def display_click_data(clickData, data):
    if not clickData or not data:
        return "Click on a point to see details"
    
    point_index = clickData['points'][0]['pointIndex']
    doc = data['documents'][point_index]
    
    return dbc.Card([
        dbc.CardBody([
            html.H5(f"Document: {doc['id']}", className="card-title"),
            html.P(f"Text: {doc['text']}", className="card-text"),
            html.P(f"Category: {doc['category']}", className="card-text"),
            html.P(f"Subcategory: {doc['subcategory']}", className="card-text"),
            html.P(f"Tags: {', '.join(doc['tags']) if doc['tags'] else 'None'}", className="card-text")
        ])
    ])

if __name__ == '__main__':
    app.run(debug=True)