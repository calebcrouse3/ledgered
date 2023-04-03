from dash import dcc, html, dash_table, callback, Input, Output, Dash
import pandas as pd
import plotly.express as px
import os
from django_plotly_dash import DjangoDash

df = pd.read_csv(os.getcwd() + "/ledgered_app/resources/transactions/chase_categorized.csv")
df.columns = ["date", "type", "amount", "account", "original_description", "pretty_description", "category"]
df.drop(df.loc[df["category"] == "Ignore"].index, inplace=True)
df["description"] = df['pretty_description'].fillna(df['original_description'])

app = DjangoDash("Transactions")

def select_category(category):
    group_desc = df[df["category"] == category].groupby("description", as_index=False).agg(
        total_amount=("amount", "sum"),
        purchase_count=("date", "count")
    ).sort_values("total_amount", ascending=False)
    
    group_desc["total_amount"] = (
        group_desc["total_amount"]
        .astype("float").round(2)
        .apply(lambda x: '{:.2f}'.format(x))
    )
    
    return group_desc.to_dict("records")

pie_chart_figure =px.pie(df, names='category', values='amount')
pie_chart_figure.update_layout(legend=dict(yanchor="top", xanchor="left", x=-0.5, y=1.0))

app.layout = html.Div([
    html.Div(children='Transactions By Category', style={'font-weight': 'bold', 'font-size': '24px'}),
    html.Div([
        dcc.Graph(figure=pie_chart_figure, style={'width': '65%'}, id="chart"),
        dash_table.DataTable(data=[], page_size=20, page_action='native', style_table={'width': '35%'}, id="table")
    ], style={'display': 'flex'})
])


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
