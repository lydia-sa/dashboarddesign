# HELP AND CHEATSHEETS
#-------------------------------------------------------------------
#https://hackerthemes.com/bootstrap-cheatsheet/#mt-1
#Bootstrap Themes: https://bootswatch.com/flatly/

# IMPORT LIBRARIES
#-------------------------------------------------------------------
import pandas as pd
from dash import Dash, dcc, html, Input, Output, callback, dash_table, State
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import dash

# FUNKTIONEN
#-------------------------------------------------------------------
def stacked_bar_chart_plotly(main_filter, dataset):
    # extract and copy date from df
    df_bar = dataset[[main_filter,'North America', 'Europe', 'Japan', 'Others', 'Global']]

    # group by filter and sort by global sales
    df_bar_grouped = df_bar.groupby([main_filter]).sum()
    df_bar_grouped = df_bar_grouped.sort_values(by=['Global'], ascending=False)

    #main filter as column in data frame
    df_bar_grouped.reset_index(inplace=True)
    df_bar_grouped = df_bar_grouped.rename(columns = {'index':main_filter})

    # dropout Global Sales
    df_bar_grouped = df_bar_grouped [[main_filter, 'North America', 'Europe', 'Japan', 'Others']]
    fig = px.bar(df_bar_grouped, x=main_filter, y=['North America', 'Europe', 'Japan', 'Others'], color_discrete_sequence= ['#006276','#1a889d','#80bdc9','#b3d7de'])

    fig.update_xaxes(showline=True, linewidth=1, linecolor='black', title = None)
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black', title = 'number of sales (in million)')

    # legend within the graph (not beside)
    fig.update_layout(plot_bgcolor='white',paper_bgcolor='white',
                      legend=dict(
                          title = '  Area',
                          yanchor="top",
                          y=0.99,
                          xanchor="right",
                          x=0.99
))
    return fig

def line_diagram(main_filter, dataset):
    df_l = dataset.groupby(['Year', main_filter], as_index=False)['Global'].sum()
    dfl_unique = df_l['Year'].unique()

    line_fig = px.line(df_l, x='Year', y='Global', color=main_filter, color_discrete_sequence= ['#006276', '#015666', '#1a889d', '#4da3b3', '#80bdc9', '#b3d7de', '#cce5e9',  '#2b6b51', '#317a5c','#378a68','#50a381', '#77b89d', '#9eccb9' ])
    line_fig.update_layout(plot_bgcolor='white',paper_bgcolor='white')
    line_fig.update_xaxes( showline=True, linewidth=1, linecolor='black', range=[1980, 2020])
    if len(dfl_unique) == 1:
        star_year = dfl_unique[0]
        line_fig.add_annotation(
            x=star_year,
            y=df_l[df_l['Year'] == star_year]['Global'].values[0],
            text='*',
            showarrow=False,
            font=dict(size=15),
        )
    line_fig.update_yaxes(showline=True, linewidth=1, linecolor='black')
    return line_fig

def calculate_global_share(main_filter, dataset, data_time):
    df_global = dataset[[main_filter, "Global"]]
    global_share = round(df_global["Global"].sum() / data_time["Global"].sum() * 100, 1)
    return f'Global: {global_share}%'

def gauge_chart(main_filter, dataset, region, data_time):
    df_gauge = dataset[[main_filter, region]]

    # calculate the market share
    marktanteil_sales = round(df_gauge[region].sum() / data_time[region].sum() * 100, 1)

    # Gauge Chart
    fig_gaug = go.Figure(go.Indicator(
        domain={'x': [0, 1], 'y': [0, 1]},
        value=marktanteil_sales,
        number={'suffix': '%', 'font': {'size': 15}},
        mode='gauge+number',
        title={'text': region, 'font': {'size': 13}},
        gauge={'axis': {'range': [None, 100]},
               'bar': {'color': '#378a68'},
               'steps': [
                   {'range': [0, 100], 'color': '#b3d7de'},
               ],
               }
    ))
    fig_gaug.update_layout(
        margin=dict(l=55, r=55, t=0, b=0),
        height=140
    )
    return fig_gaug

alert = dbc.Alert('Please choose another period of time to avoid further disappointment!',
                  color='danger',
                  duration=5000,
                  className='text-center')


# IMPORT DATA
#-------------------------------------------------------------------
# import clean data
df = pd.read_csv("../dataframe_videogames_clean.csv")

# make a list for the list
df_liste = df[['Name', 'Platform', 'Genre', 'Global']]


# START APP
#-------------------------------------------------------------------
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],

                # should make it mobile-friendly
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )

# LAYOUT SECTION: BOOTSTRAP
#--------------------------------------------------------------------
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H3('Video Games',
                        className='text-left'),
                width={'size':2} ),

        dbc.Col(dcc.Dropdown(id='dd_platform',
                             options=sorted([{'label': i, 'value': i} for i in df['Platform'].unique()], key = lambda x: x['label']),
                             placeholder='select a platform',
                             value= [],
                             multi= True),
                width={'size':2},
                style={'font-size': '14px'}
                ),

        dbc.Col(dcc.Dropdown(id='dd_company',
                             options=sorted([{'label': i, 'value': i} for i in df['Company'].unique()], key = lambda x: x['label']),
                             placeholder='select a company',
                             value= [],
                             multi= True
                             ),
                width={'size':2},
                style={'font-size': '14px'}
                ),

        dbc.Col(dcc.Dropdown(id='dd_publisher',
                             options=sorted([{'label': i, 'value': i} for i in df['Publisher'].unique()], key = lambda x: x['label']),
                             placeholder='select a publisher',
                             value= [],
                             multi= True
                             ),
                width={'size': 2},
                style = {'font-size': '14px'}
                ),

        dbc.Col(dcc.Dropdown(id='dd_genre',
                             options=sorted([{'label': i, 'value': i} for i in df['Genre'].unique()], key = lambda x: x['label']),
                             placeholder='select a genre',
                             value= [],
                             multi= True
                             ),
                width={'size': 2},
                style={'font-size': '14px'}
                ),

        dbc.Col(dcc.Dropdown(id='dd_console',
                             options=sorted([{'label': i, 'value': i} for i in df['Console'].unique()], key = lambda x: x['label']),
                             placeholder='select a console',
                             value= [],
                             multi=True
                             ),
                width={'size': 2},
                style={'font-size': '14px'}
                ),

        ], className='mt-3',
    ),
    dbc.Row(
        dbc.Col(dcc.RangeSlider(id='slider_year',
                            min=df['Year'].min(),
                            max=df['Year'].max(),
                            marks ={1980: '1980',
                                    1990: '1990',
                                    2000: '2000',
                                    2010: '2010',
                                    2020: '2020'},

                            value=[df['Year'].min(), df['Year'].max()],
                            updatemode = 'mouseup',
                            ),
        className='mt-1',
        width = {'size': 4,'offset':4})),
    dbc.Row(html.Div(id='wrong_time_alert', children=[])),
    dbc.Row([
        dbc.Col([
            dbc.Row(html.H5('Ranking',
                        className='text-left')),
            dbc.Row(dash_table.DataTable(
                id='datatable_1',
                columns=[{'name': i, 'id': i, 'deletable': False, 'selectable': True} for i in df_liste.columns],
                data = df_liste.to_dict('records'),
                sort_action='native',
                page_action='native',
                page_current= 0,
                page_size= 15,
                style_cell={'textAlign': 'left',
                            'fontSize': '75%',
                            'fontFamily': 'Arial, sans-serif',
                            'whiteSpace': 'normal',
                            'height': 'auto'},
                style_table={'overflowX': 'auto', 'fontFamily': '-apple-system'},
                style_header={
                    'fontWeight': 'bold', },
                style_as_list_view=True,
                style_data_conditional=[
                    {'if': {'row_index': 'odd'},'backgroundColor': '#F9FCFD'}],
    ),

            ),

            ],
            width={'size': 3},
        ),
        dbc.Col([
            dbc.Row(dcc.Graph(id='stable_diagram', figure={}),
                 style={'height': '300px', 'margin-top': '0px',}),
            dbc.Row(dcc.RadioItems(
                id='check_choice',
                options=['Platform','Company','Publisher','Genre','Console'],
                value='Platform',
                labelStyle = {'display': 'inline-block', 'margin-left': '20px', 'margin-right': '10px'},
                inline=True
            ),
            style={'margin-left': '150px', 'height': '20px',},
            ),
            dbc.Row(dcc.Graph(id='line_diagram', figure={}),
                    style={'height': '305px',}
                    ),
            ],
            width={'size':7},
        ),
        dbc.Col([
            dbc.Row(html.H5('Market Share by Region',
                        className='text-left')),
            dbc.Row(html.H6(id = 'share_global',
                            style={'text-align': 'center', 'marigin-top': '5px', 'margin-bottom': '15px'}
                            )),
            dbc.Row(dcc.Graph(id='gauge_diagram_AM', figure={})),
            dbc.Row(dcc.Graph(id='gauge_diagram_EUR', figure={})),
            dbc.Row(dcc.Graph(id='gauge_diagram_JAP', figure={})),
            dbc.Row(dcc.Graph(id='gauge_diagram_OTH', figure={}))],
            width={'size':2},
        ),
    ])

# close the column and no space to the left or the right of the whole dashboard
], fluid=True)

# CALLBACK FUNCTION
#--------------------------------------------------------------------
# the following callbacks are only to filter the dropdown menu options,
# so that the options are depending on the selection of other dropdown filters.
@app.callback(
    Output('dd_platform', 'options'),
    Input('dd_company', 'value'),
    Input('dd_publisher', 'value'),
    Input('dd_genre', 'value'),
    Input('dd_console', 'value'),
    Input('slider_year', 'value'),
)
def update_platform_options(company, publisher, genre, console, year):
    filtered_data = df
    min_year, max_year = year
    filtered_data = filtered_data[filtered_data['Year'].between(min_year, max_year)]

    if console:
        filtered_data = filtered_data[filtered_data['Console'].isin(console)]
    if company:
        filtered_data = filtered_data[filtered_data['Company'].isin(company)]
    if publisher:
        filtered_data = filtered_data[filtered_data['Publisher'].isin(publisher)]
    if genre:
        filtered_data = filtered_data[filtered_data['Genre'].isin(genre)]

    options = sorted([{'label': i, 'value': i} for i in filtered_data['Platform'].unique()], key=lambda x: x['label'])
    return options

@app.callback(
    Output('dd_company', 'options'),
    Input('dd_platform', 'value'),
    Input('dd_publisher', 'value'),
    Input('dd_genre', 'value'),
    Input('dd_console', 'value'),
    Input('slider_year', 'value'),
)
def update_company_options(platform, publisher, genre, console, year):
    filtered_data = df
    min_year, max_year = year
    filtered_data = filtered_data[filtered_data['Year'].between(min_year, max_year)]

    if console:
        filtered_data = filtered_data[filtered_data['Console'].isin(console)]
    if platform:
        filtered_data = filtered_data[filtered_data['Platform'].isin(platform)]
    if publisher:
        filtered_data = filtered_data[filtered_data['Publisher'].isin(publisher)]
    if genre:
        filtered_data = filtered_data[filtered_data['Genre'].isin(genre)]

    options = sorted([{'label': i, 'value': i} for i in filtered_data['Company'].unique()], key=lambda x: x['label'])
    return options

@app.callback(
    Output('dd_publisher', 'options'),
    Input('dd_platform', 'value'),
    Input('dd_company', 'value'),
    Input('dd_genre', 'value'),
    Input('dd_console', 'value'),
    Input('slider_year', 'value'),
)
def update_publisher_options(platform, company, genre, console, year):
    filtered_data = df
    min_year, max_year = year
    filtered_data = filtered_data[filtered_data['Year'].between(min_year, max_year)]

    if console:
        filtered_data = filtered_data[filtered_data['Console'].isin(console)]
    if platform:
        filtered_data = filtered_data[filtered_data['Platform'].isin(platform)]
    if company:
        filtered_data = filtered_data[filtered_data['Company'].isin(company)]
    if genre:
        filtered_data = filtered_data[filtered_data['Genre'].isin(genre)]

    options = sorted([{'label': i, 'value': i} for i in filtered_data['Publisher'].unique()], key=lambda x: x['label'])
    return options

@app.callback(
    Output('dd_genre', 'options'),
    Input('dd_platform', 'value'),
    Input('dd_company', 'value'),
    Input('dd_publisher', 'value'),
    Input('dd_console', 'value'),
    Input('slider_year', 'value')
)
def update_genre_options(platform, company, publisher, console, year):
    filtered_data = df
    min_year, max_year = year
    filtered_data = filtered_data[filtered_data['Year'].between(min_year, max_year)]

    if console:
        filtered_data = filtered_data[filtered_data['Console'].isin(console)]
    if platform:
        filtered_data = filtered_data[filtered_data['Platform'].isin(platform)]
    if company:
        filtered_data = filtered_data[filtered_data['Company'].isin(company)]
    if publisher:
        filtered_data = filtered_data[filtered_data['Publisher'].isin(publisher)]

    options = sorted([{'label': i, 'value': i} for i in filtered_data['Genre'].unique()], key=lambda x: x['label'])
    return options

@app.callback(
    Output('dd_console', 'options'),
    Input('dd_platform', 'value'),
    Input('dd_company', 'value'),
    Input('dd_publisher', 'value'),
    Input('dd_genre', 'value'),
    Input('slider_year', 'value'),
)
def update_console_options(platform, company, publisher, genre, year):
    filtered_data = df
    min_year, max_year = year
    filtered_data = filtered_data[filtered_data['Year'].between(min_year, max_year)]

    if publisher:
        filtered_data = filtered_data[filtered_data['Publisher'].isin(publisher)]
    if platform:
        filtered_data = filtered_data[filtered_data['Platform'].isin(platform)]
    if company:
        filtered_data = filtered_data[filtered_data['Company'].isin(company)]
    if genre:
        filtered_data = filtered_data[filtered_data['Genre'].isin(genre)]

    options = sorted([{'label': i, 'value': i} for i in filtered_data['Console'].unique()], key=lambda x: x['label'])
    return options


# now the callback for the diagramm updates
@app.callback(
    [Output('datatable_1', 'data'),
    Output('stable_diagram', 'figure'),
    Output('line_diagram', 'figure'),
    Output('share_global', 'children'),
    Output('gauge_diagram_AM', 'figure'),
    Output('gauge_diagram_EUR', 'figure'),
    Output('gauge_diagram_JAP', 'figure'),
    Output('gauge_diagram_OTH', 'figure'),
    Output('wrong_time_alert', 'children')
     ],
    [Input('check_choice', 'value'),
    Input('dd_platform', 'value'),
    Input('dd_genre', 'value'),
    Input('dd_console', 'value'),
    Input('dd_company', 'value'),
    Input('dd_publisher', 'value'),
    Input('slider_year', 'value')
     ],)

def update_charts(main_filter, platform, genre, console, company, publisher, year):
    min_year, max_year = year
    dfc = df.copy()
    dft = dfc[dfc['Year'].between(min_year, max_year)]
    dff = dft

    if platform:
        dff = dff[dff['Platform'].isin(platform)]
    if genre:
        dff = dff[dff['Genre'].isin(genre)]
    if console:
        dff = dff[dff['Console'].isin(console)]
    if company:
        dff = dff[dff['Company'].isin(company)]
    if publisher:
        dff = dff[dff['Publisher'].isin(publisher)]

    if len(dff) == 0:
        return (dff.to_dict('records'),
               stacked_bar_chart_plotly(main_filter,dff),
               line_diagram(main_filter,dff),
               calculate_global_share(main_filter, dff, dft),
               gauge_chart(main_filter, dff, 'North America', dft),
               gauge_chart(main_filter, dff, 'Europe', dft),
               gauge_chart(main_filter, dff, 'Japan', dft),
               gauge_chart(main_filter, dff, 'Others', dft),
                alert)
    else:
        return (dff.to_dict('records'),
               stacked_bar_chart_plotly(main_filter,dff),
               line_diagram(main_filter,dff),
               calculate_global_share(main_filter, dff, dft),
               gauge_chart(main_filter, dff, 'North America', dft),
               gauge_chart(main_filter, dff, 'Europe', dft),
               gauge_chart(main_filter, dff, 'Japan', dft),
               gauge_chart(main_filter, dff, 'Others', dft),
               dash.no_update)


# RUN THE APP
#--------------------------------------------------------------------
if __name__=='__main__':
    app.run_server(debug=True, port=8000)

