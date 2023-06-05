import math
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc
from sklearn.datasets import make_blobs

# new: more than one plot in a callback
# new: one plot as an input for another plot
# new: plotly go object

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

df = pd.DataFrame({'y': np.random.normal(loc=0, scale=10, size=1000),
                   'x': np.random.normal(loc=10, scale=2, size=1000)})

COLORS = {'0': "red", '1': "blue", '2': "grey", '3': '#80bdc9', '4': "yellow", '5': "green",'6': "orange", '7': "black", '8': "purple", '9':"#9eccb9"}

app.layout = html.Div([html.Div([html.H1("Dashboard 4")], className="header"), html.Div([dcc.Tabs(id="tabs", children=[
                 dcc.Tab(label='Tab One', id="tab_1_graphs", children=[html.Div([
                      dbc.Row([dbc.Col([dcc.Dropdown(options=['red','green','blue'], value='red', id='color', multi=False)], width=6),
                               dbc.Col([dcc.Slider(min=math.floor(df['y'].min()), max=math.ceil(df['y'].max()), id="min_value")], width=6)]),
                      dbc.Row([dbc.Col([dcc.Graph(id="graph_1")], width=6),
                               dbc.Col([dcc.Graph(id="graph_2")], width=6)])], className="tab_content"),]),
                 dcc.Tab(label='Tab Two', id="tab_2_graphs", children=[html.Div([
                      dbc.Row([dbc.Col([dcc.Slider(1, 10, 1, value= 3, id= "slider_cluster")], className='mt-4', width = {'size': 6,'offset':3})]),
                     dbc.Row([dbc.Col([dcc.Graph(id="graph_3")], width=8),
                              dbc.Col([dcc.Graph(id="graph_4")], width=4)])], className="tab_content")]),])], className="content")])

@app.callback(Output("graph_1", "figure"), Input("color", "value"))

def update_graph_1(dropdown_value_color):
    fig = px.histogram(df, x="y", color_discrete_sequence=[dropdown_value_color])
    fig.update_layout(template="plotly_white")
    return fig

@app.callback(Output("graph_2", "figure"), Input("min_value", "value"))

def update_graph_2(min_value):
    if min_value:
        dff = df[df['y'] > min_value]
    else:
        dff = df
    fig = px.scatter(dff, x='x', y='y')
    fig.update_layout(template="plotly_white")
    return fig

@app.callback(Output("graph_3", "figure"), Output("graph_4", "figure"), Input("graph_3", "relayoutData"), Input("slider_cluster", "value"))

def update_graph_3_and_4(selected_data, num_clusters):
    X, y = make_blobs(n_samples=100, centers=num_clusters, n_features=2, random_state=0)

    cluster_df = pd.DataFrame(data=X, columns=["X", "Y"])
    cluster_df['cluster'] = [str(i) for i in y]


    if selected_data is None or (isinstance(selected_data, dict) and 'xaxis.range[0]' not in selected_data):
        cluster_dff = cluster_df
    else:
        cluster_dff = cluster_df[(cluster_df['X'] >= selected_data.get('xaxis.range[0]')) &
                                 (cluster_df['X'] <= selected_data.get('xaxis.range[1]')) &
                                 (cluster_df['Y'] >= selected_data.get('yaxis.range[0]')) &
                                 (cluster_df['Y'] <= selected_data.get('yaxis.range[1]'))]

    fig3 = px.scatter(cluster_dff, x="X", y="Y", color="cluster",color_discrete_map=COLORS, category_orders= {"cluster": ["0","1","2","3","4","5","6","7","8","9"]}, height=750)
    fig3.update_layout(template="plotly_white",  coloraxis_showscale=False)
    fig3.update_traces(marker=dict(size=8))

    group_counts = cluster_dff[['cluster', 'X']].groupby('cluster').count()
    group_counts = group_counts.sort_values(by='X')

    fig4 = go.Figure(data=[go.Bar(x=group_counts.index, y=group_counts['X'], marker_color= [COLORS.get(i) for i in group_counts.index])])
    fig4.update_layout(height=750, template="plotly_white", title="<b>Counts per cluster</b>", xaxis_title="cluster", title_font_size= 25)
    return fig3, fig4

if __name__ == '__main__':
    app.run_server(debug=True, port=8012)
