from dash import dcc, html, dash_table, callback, Input, Output, Dash
import pandas as pd
import plotly.express as px
import os

df = pd.read_csv("../../ledgered/ledgered_app/resources/transactions/chase_categorized.csv")
df.columns = ["date", "type", "amount", "account", "original_description", "pretty_description", "category"]
df.drop(df.loc[df["category"] == "Ignore"].index, inplace=True)
df["description"] = df['pretty_description'].fillna(df['original_description'])

app = Dash(__name__)


def select_category(category):
    return df.loc[df["category"] == category, ["date", "amount", "description"]].sort_values("amount", ascending=False).to_dict("records")

pie_chart_figure =px.pie(df, names='category', values='amount')
pie_chart_figure.update_layout(legend=dict(yanchor="top", xanchor="left", x=-0.5, y=1.0))

app.layout = html.Div([
    html.Div(children='Transactions By Category', style={'font-weight': 'bold', 'font-size': '24px'}),
    html.Div([
        dcc.Graph(figure=pie_chart_figure, style={'width': '65%'}, id="chart"),
        dash_table.DataTable(data=[], page_size=20, page_action='native', style_table={'width': '35%'}, id="table")
    ], style={'display': 'flex'})
])


#app.layout = html.Div([
#    html.Div(children='Transactions By Category', style={'font-weight': 'bold', 'font-size': '24px'}),
#    html.Div([
#        dcc.Graph(
#            figure=px.pie(df, names='category', values='amount', hole=.4, width=800, height=400), 
#            style={'width': '50%', 'float': 'left'}, id="chart"),
#        dash_table.DataTable(
#            data=[], 
#            columns=[{'name': i, 'id': i, 'type': 'text'} for i in ['date', 'amount', 'description']], 
#            style_table={'width': '50%', 'float': 'right', 'margin-left': '10px', 'text-align': 'left'}, 
#            id="table",
#        )
#    ], style={'display': 'flex', 'height': 'calc(100vh - 100px)'})
#], style={'height': '100vh'})




@callback(
    Output(component_id='table', component_property='data'),
    Input(component_id='chart', component_property='clickData')
)
def update_table(click_data):
    if click_data is not None:
        category = click_data['points'][0]['label']
    else:
        category = df['category'].values[0]
    outputDf = select_category(category)
    return outputDf


if __name__ == '__main__':
    app.run_server(debug=True)