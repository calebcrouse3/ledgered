from plotly.offline import plot
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd

def get_plot(df):
    df.drop(df.loc[df["category"] == "Ignore"].index, inplace=True)
    df["description"] = df['pretty_description'].fillna(df['original_description'])
    df["week_id"] = df["date"].apply(lambda x: (x.isocalendar().year * 100) + x.isocalendar().week)
    
    groupByWeek = df.groupby(["week_id", "category"], as_index=False).agg(
        sum=("amount", "sum"),
        count=("date", "count")
    )
    
    # for now just assume the oldest week is not complete and so remove it so it doesnt skew the stats
    removeMinWeek = groupByWeek[groupByWeek["week_id"] != groupByWeek["week_id"].min()]
    
    weeklyStats = removeMinWeek.groupby("category", as_index=False).agg(
        avg_amount=("sum", "mean"),
        avg_count=("count", "mean")
    )
    
    weeklyStats["avg_amount"] = weeklyStats["avg_amount"].round(2)
    weeklyStats["avg_count"] = weeklyStats["avg_count"].round(1)
    
    pie1 = px.pie(weeklyStats, names='category', values='avg_amount')
    pie1.update_traces(textinfo='value', title="Weekly Average Amount")
    
    pie2 = px.pie(weeklyStats, names='category', values='avg_count')
    pie2.update_traces(textinfo='value', title="Weekly Average Count")
    
    pie3 = px.pie(df, names='category', values='amount')
    pie3.update_traces(textinfo='value', title="Total Amount All Time")
    
    fig = make_subplots(rows=2, cols=3, specs=[[{"type": "pie"}, {"type": "pie"}, {"type": "pie"}], [{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]])
    
    fig.add_trace(pie1.data[0], row=1, col=1)
    fig.add_trace(pie2.data[0], row=1, col=2)
    fig.add_trace(pie3.data[0], row=1, col=3)

    chart = plot(fig, output_type='div')
    
    return chart