import dash
from dash import callback, Input, Output, State, html
import dash_bootstrap_components as dbc


class InteractionCallbacks:
    
    def __init__(self):
        self._register_callbacks()
    
    def _register_callbacks(self):
        
        @callback(
            Output('point-details', 'children'),
            Input('embedding-plot', 'clickData'),
            [State('processed-data', 'data'),
             State('processed-prompts', 'data')]
        )
        def display_click_data(clickData, data, prompts_data):
            if not clickData or not data:
                return "Click on a point to see details"
            
            point_data = clickData['points'][0]
            trace_name = point_data.get('fullData', {}).get('name', 'Documents')
            
            if 'pointIndex' in point_data:
                point_index = point_data['pointIndex']
            elif 'pointNumber' in point_data:
                point_index = point_data['pointNumber']
            else:
                return "Could not identify clicked point"
            
            if trace_name.startswith('Prompts') and prompts_data and 'prompts' in prompts_data:
                item = prompts_data['prompts'][point_index]
                item_type = 'Prompt'
            else:
                item = data['documents'][point_index]
                item_type = 'Document'
            
            return self._create_detail_card(item, item_type)
        
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
    
    @staticmethod
    def _create_detail_card(item, item_type):
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