import math

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc
from sklearn.datasets import make_blobs

# New: Density heatmap (2 columns) as third plot on tab 2
# with color and resolution options
# New: Everything with inline style and bootstrap (no CSS)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# generate random normal distributed data for x and y
# and store it in a Pandas DataFrame (for plot 1,2, and 5)

np.random.seed(seed=8)

df = pd.DataFrame({'y': np.random.normal(loc=0, scale=10, size=1000),
                   'x': np.random.normal(loc=10, scale=2, size=1000)})

# define cluster colors

COLORS = {'0': "red", '1': "blue", '2': "grey"}

# generic cluster data (for plot 3 and 4)

X, y = make_blobs(n_samples=7500, centers=3, n_features=2, random_state=0, cluster_std=0.75)

cluster_df = pd.DataFrame(data=X, columns=["X", "Y"])
cluster_df['cluster'] = [str(i) for i in y]

app.layout = html.Div([html.Div([html.H1("Dashboard 6")], style={'margin': '10px 25px 25px 25px'}), html.Div([dcc.Tabs(id="tabs", children=[
    dcc.Tab(label='Tab One', children=[html.Div([
        dbc.Row([dbc.Col([dcc.Dropdown(options=['red', 'green', 'blue'], value='red', id='color', multi=False)], width=6),
                 dbc.Col([dcc.Slider(min=math.floor(df['y'].min()), max=math.ceil(df['y'].max()), id="min_value")], width=6)]),
        dbc.Row([dbc.Col([dcc.Graph(id="graph_1")],width=6),
                 dbc.Col([dcc.Graph(id="graph_2")],width=6)])], style={"margin": "100px 25px 25px 25px"}),]),
    dcc.Tab(label='Tab Two', id="tab_2_graphs", children=[html.Div([
        dbc.Row([dbc.Col([dcc.Graph(id="graph_3")], width=7),
                 dbc.Col([dcc.Graph(id="graph_4")], width=3),
                 dbc.Col(html.Div(id="cluster-info"),width=2 ,style={"margin-top": "20px"})
                 ]),
        dbc.Row([dbc.Col(html.Div([dbc.Label("Number of bins:", html_for="graph_5_nbins"),
                                   dcc.Dropdown(options= [str(i) for i in range(5, 100, 5)], value='40', id='graph_5_nbins', multi=False)]),width={"size": 3},),
                 dbc.Col(html.Div([dbc.Label("Color:", html_for="graph_5_color"),
                                   dcc.Dropdown(options=["Viridis", "Magma", "Hot", "GnBu", "Greys"], value='Viridis', id='graph_5_color', multi=False)]),width={"size": 3,"offset": 1},),
                 dbc.Col(html.Div([dbc.Label("Separated for Cluster:", html_for="graph_5_separated"),
                                   dcc.RadioItems(options=["Yes","No"], value='No', id='graph_5_separated')]),width={"size": 3,"offset": 1},)]),
        dbc.Row([dbc.Col([dcc.Graph(id="graph_5")], width=12),])
    ], style={"margin": "10px 25px 25px 25px"})
    ])])])])

def update_selected_data(selected_data):
    if selected_data is None or (isinstance(selected_data, dict) and 'xaxis.range[0]' not in selected_data): cluster_dff = cluster_df
    else:
        cluster_dff =\
            cluster_df[
          (cluster_df['X'] >=
              selected_data.get('xaxis.range[0]')) &
          (cluster_df['X'] <=
              selected_data.get('xaxis.range[1]')) &
          (cluster_df['Y'] >=
              selected_data.get('yaxis.range[0]')) &
          (cluster_df['Y'] <=
              selected_data.get('yaxis.range[1]'))]
    return cluster_dff

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

@app.callback(Output("graph_3", "figure"), Output("graph_4", "figure"), Input("graph_3", "relayoutData"))

def update_graph_3_and_4(selected_data):

    PLOT_HEIGHT = 400

    cluster_dff = update_selected_data(selected_data=selected_data)

    fig3 = px.scatter(cluster_dff, x="X", y="Y", color="cluster", color_discrete_map=COLORS, category_orders={"cluster": ["0", "1", "2"]})

    fig3.update_layout(height=PLOT_HEIGHT, template="plotly_white", coloraxis_showscale=False)
    fig3.update_traces(marker=dict(size=8))

    group_counts = cluster_dff[['cluster', 'X']].groupby('cluster').count()

    fig4 = go.Figure(data=[go.Bar(x=group_counts.index, y=group_counts['X'], marker_color=[COLORS.get(i) for i in group_counts.index])])

    fig4.update_layout(height=PLOT_HEIGHT, template="plotly_white", title="<b>Counts per cluster</b>", xaxis_title="cluster", title_font_size=25)

    return fig3, fig4

@app.callback(Output("graph_5", "figure"), Input("graph_5_nbins", "value"), Input("graph_5_color", "value"), Input("graph_5_separated", "value"), Input("graph_3", "relayoutData"),)

def update_graph_5(nbins, color, separated, selected_data):
    cluster_dff = update_selected_data(selected_data=selected_data)

    fig = px.density_heatmap(cluster_dff, x="X", y="Y", nbinsx=int(nbins), nbinsy=int(nbins), color_continuous_scale=color, facet_col=None if separated == "No" else "cluster",
        category_orders={"cluster": ["0", "1", "2"]})
    fig.update_layout(template="plotly_white")
    return fig

@app.callback(Output("cluster-info", "children"), Input("graph_3", "relayoutData"))
def update_cluster_info(selected_data):
    cluster_dff = update_selected_data(selected_data=selected_data)
    cluster_counts = cluster_dff['cluster'].value_counts().reset_index()
    cluster_counts.columns = ['Cluster', 'Count']
    return dbc.Table.from_dataframe(cluster_counts, striped=True, bordered=True, hover=True)

if __name__ == '__main__':
    app.run_server(debug=True, port=8014)