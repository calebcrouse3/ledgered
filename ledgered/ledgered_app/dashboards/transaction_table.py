from dash import dcc, html, dash_table, callback, Input, Output
from django_plotly_dash import DjangoDash
import pandas as pd
import plotly.express as px

# Initialize the app
def get_app(df):
    app = DjangoDash("TransactionTable")
    
    app.layout = html.Div([
        html.Div(children='Table with user transactions'),
        dcc.Graph(figure=px.histogram(df, x='category', y='amount', histfunc='sum'), style={'display':'inline-block', 'width':1000, 'height':1000})
    ])
    
    return app