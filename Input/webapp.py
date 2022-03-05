import math
import networkx as nx
import pandas as pd
import collections
import dash
from dash import dash_table
from dash import dcc
from dash import html
import plotly.graph_objs as go
import plotly.express as px
from textwrap import dedent as d

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "CZ4071 Project 1"
df = pd.read_csv("ProcessedNetworkDataFrame.csv")

def get_author_name(author_pid):
    return str(df.loc[df['author_pid']==author_pid].iloc[0]['author_name'])

def generate_graph(year_range, option):
    if option == "Random":
        return nx.fast_gnp_random_graph(n=989, p=0.03, seed=4071)
    else:
        df_filtered = df.loc[(year_range[0]<=df['year']) & (df['year']<=year_range[1])].reset_index(drop=True)
        # if author_pid != None:
        #     df_filtered = df_filtered.loc[df['author_pid']==author_pid]

        author_pid = df_filtered["author_pid"].to_list()
        coauthor_pid = df_filtered["coauthor_pid"].to_list()
        collaborations = list(zip(author_pid, coauthor_pid))

        G = nx.Graph()
        G.add_edges_from(collaborations)
        return G

def network_graph(year_range, option):
    G = generate_graph(year_range, option)
    pos = nx.drawing.spring_layout(G)
    for node in G.nodes:
        G.nodes[node]['pos'] = list(pos[node])
    
    traceRecode = []

    # edges
    index = 0
    for edge in G.edges:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        trace = go.Scatter(
            x=tuple([x0, x1, None]), 
            y=tuple([y0, y1, None]),
            mode='lines',
            marker=dict(color='blue'),
            line_shape='spline',
            opacity=1
        )
        traceRecode.append(trace)
        index = index + 1

    # nodes
    node_trace = go.Scatter(
        x=[], y=[], 
        hovertext=[], 
        text=[], 
        mode='markers+text', 
        textposition="bottom center",
        hoverinfo="text", 
        marker={
            'size': 10, 
            'color': 'LightSkyBlue'}
    )

    index = 0
    for node in G.nodes:
        x, y = G.nodes[node]['pos']
        hovertext = "AuthorPID: " + str(node)
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['hovertext'] += tuple([hovertext])
        index = index + 1

    traceRecode.append(node_trace)

    # hover over edge
    middle_hover_trace = go.Scatter(
        x=[], y=[], hovertext=[], 
        mode='markers', 
        hoverinfo="text",
        marker={
            'size': 20, 
            'color': 'LightSkyBlue'},
        opacity=0
    )

    index = 0
    for edge in G.edges:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        middle_hover_trace['x'] += tuple([(x0 + x1) / 2])
        middle_hover_trace['y'] += tuple([(y0 + y1) / 2])
        index = index + 1

    traceRecode.append(middle_hover_trace)

    # layout
    figure = {
        "data": traceRecode,
        "layout": go.Layout(
            title='Interactive Network Visualization', 
            showlegend=False, 
            hovermode='closest',
            margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
            xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
            yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
            height=600,
            clickmode='event+select',
        )
    }

    return figure

def display_degree_distribution(year_range, option):
    G = generate_graph(year_range, option)
    degree_sequence = sorted([d for n, d in G.degree()], reverse=True)
    degree_count = collections.Counter(degree_sequence)
    degree = []
    count = []
    for i in degree_count:
        count.append(math.log(degree_count[i], 10))
        if i == 0:
            degree.append(i)
        else:
            degree.append(math.log(i, 10))
    df_deg_dist = pd.DataFrame({'degree': degree, 'count': count})
    return px.scatter(df_deg_dist, x='degree', y='count', trendline='ols')

def display_network_properties(year_range, option):
    G = generate_graph(year_range, option)
    for C in (G.subgraph(c).copy() for c in sorted(nx.connected_components(G), key=len)):
        lcc = C
    properties = {
        "Number of isolates": nx.number_of_isolates(G),
        "Number of nodes": nx.number_of_nodes(G),
        "Number of edges": nx.number_of_edges(G),
        "Average degree": nx.number_of_edges(G) / nx.number_of_nodes(G),
        "Highest degree": sorted(G.degree, key=lambda x: x[1], reverse=True)[0][1],
        "Average Clustering Coefficient": nx.average_clustering(G),
        "Number of nodes in largest connected component": nx.number_of_nodes(lcc),
        "Diameter of largest connected component": nx.diameter(lcc),
        "Average shortest path of largest connected component": nx.average_shortest_path_length(lcc),
        "Node with highest degree centrality": max(nx.degree_centrality(G)),
        "Node with highest eigenvector centrality": max(nx.eigenvector_centrality(G)),
        "Node with highest betweenness centrality": max(nx.betweenness_centrality(G)),
        "Node with highest closeness centrality": max(nx.closeness_centrality(G)),
    }
    df_properties = pd.DataFrame(properties, index=[0]).transpose().reset_index()
    df_properties.columns = ["Properties", "Results"]
    return df_properties

# =================================================================================
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

tab_style = {
    "background": "#323130",
    'text-transform': 'capitalize',
    'color': 'white',
    'border': 'grey',
    'font-size': '11px',
    'font-weight': 600,
    'align-items': 'center',
    'justify-content': 'center',
    'border-radius': '4px',
    'padding': '12px'
}

tab_selected_style = {
    "background": "grey",
    'text-transform': 'capitalize',
    'color': 'white',
    'font-size': '11px',
    'font-weight': 600,
    'align-items': 'center',
    'justify-content': 'center',
    'border-radius': '4px',
    'padding': '12px'
}

app.layout = html.Div([
    html.Div(
        [
            html.H1("Collaborations Network Graph")
        ],
        className="row",
        style={'textAlign': "center"}
    ),
    
    html.Div(
        className="row",
        children=[
            html.Div(
                className="two columns",
                children=[
                    dcc.Markdown(d("""
                            **Time Range To Visualize**\n
                            Slide the bar to define year range.
                            """)),
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.RangeSlider(
                                id='my-range-slider',
                                min=1982,
                                max=2021,
                                step=1,
                                value=[1997, 2007],
                                vertical=True,
                                verticalHeight=750,
                                marks={
                                    1982: {'label': '1982'},
                                    1983: {'label': '1983'},
                                    1984: {'label': '1984'},
                                    1985: {'label': '1985'},
                                    1986: {'label': '1986'},
                                    1987: {'label': '1987'},
                                    1988: {'label': '1988'},
                                    1989: {'label': '1989'},
                                    1989: {'label': '1989'},
                                    1990: {'label': '1990'},
                                    1991: {'label': '1991'},
                                    1992: {'label': '1992'},
                                    1993: {'label': '1993'},
                                    1994: {'label': '1994'},
                                    1995: {'label': '1995'},
                                    1996: {'label': '1996'},
                                    1997: {'label': '1997'},
                                    1998: {'label': '1998'},
                                    1999: {'label': '1999'},
                                    2000: {'label': '2000'},
                                    2001: {'label': '2001'},
                                    2002: {'label': '2002'},
                                    2003: {'label': '2003'},
                                    2004: {'label': '2004'},
                                    2005: {'label': '2005'},
                                    2006: {'label': '2006'},
                                    2007: {'label': '2007'},
                                    2008: {'label': '2008'},
                                    2009: {'label': '2009'},
                                    2010: {'label': '2010'},
                                    2011: {'label': '2011'},
                                    2012: {'label': '2012'},
                                    2013: {'label': '2013'},
                                    2014: {'label': '2014'},
                                    2015: {'label': '2015'},
                                    2016: {'label': '2016'},
                                    2017: {'label': '2017'},
                                    2018: {'label': '2018'},
                                    2019: {'label': '2019'},
                                    2020: {'label': '2020'},
                                    2021: {'label': '2021'},
                                }
                            ),
                            html.Br(),
                            html.Div(id='output-container-range-slider')
                        ],
                        style={'height': '300px'}
                    ),
                ],
            ),
            html.Center(
                className="eight columns",
                children=[
                    html.Div(
                        [
                            # html.Div(
                            #     className="row",
                            #     children=[
                            #         dcc.Markdown(d(
                            #             """
                            #             **Author To Search**
                            #             Input the author pid to visualize.
                            #             """)),
                            #         dcc.Input(id="input1", type="text", placeholder="author pid"),
                            #         html.Div(id="output")
                            #     ],
                            #     style={'height': '100px'}
                            # ),
                            html.Div(
                                className="row",
                                children=[
                                    dcc.Markdown(d(
                                        """
                                        **View Network**\n
                                        Select Actual or Random Network to view (default Actual)
                                        """
                                    )),
                                    dcc.Tabs(
                                        id="tabs-styled-with-inline", 
                                        value=None, 
                                        vertical=True, 
                                        children=[
                                            dcc.Tab(
                                                label='Actual Collaboration Network', 
                                                value='Actual', 
                                                style=tab_style,
                                                selected_style=tab_selected_style
                                            ),
                                            dcc.Tab(
                                                label='Random Network', 
                                                value='Random', 
                                                style=tab_style,
                                                selected_style=tab_selected_style
                                            ),
                                        ], 
                                        style={'margin-bottom': '10px', 'width': '200px'}
                                    ),
                                    html.Div(id='tabs-content-inline'),
                                ]
                            ),
                            dcc.Graph(id="my-graph", figure=network_graph([1997, 2007], 'Actual')),
                            html.H3("Click and drag to zoom in")
                        ],
                        style={'height': '1000px', 'width': '800px'}
                    ), 
                ],
            ),
        ]
    ),

    html.Div(
        className="row",
        children=[
            html.Div(
                className="twelve columns",
                children=[
                    dcc.Markdown(d(
                        """
                        **Log-Log Degree Distribution**
                        """)),
                    dcc.Graph(id="degree_dist", figure=display_degree_distribution([1997, 2007], 'Actual')),
                ], style={'height': '400px', 'width': '350px'}
            ),
            html.Div(
                className="two columns",
                children=[
                    html.Div(
                        className='twelve columns',
                        children=[
                            dcc.Markdown(d(
                                """
                                **Network Properties**
                                """)),
                            dash_table.DataTable(
                                id='network_properties',
                                columns=[{"name": i, "id": i} for i in display_network_properties([1997, 2007], 'Actual').columns],
                                data=display_network_properties([1997, 2007], 'Actual').to_dict('records'),
                            ),
                        ],
                        style={'height': '400px', 'width': '300px'}
                    ),
                ]
            )
        ]
    )

])

@app.callback(
    dash.dependencies.Output('my-graph', 'figure'),
    [
        dash.dependencies.Input('my-range-slider', 'value'), 
        # dash.dependencies.Input('input1', 'value')
        dash.dependencies.Input('tabs-styled-with-inline', 'value')
    ]
)
def update_output(year_range, option):
    return network_graph(year_range, option)
    
@app.callback(
    dash.dependencies.Output('degree_dist', 'figure'),
    [
        dash.dependencies.Input('my-range-slider', 'value'),
        dash.dependencies.Input('tabs-styled-with-inline', 'value')
    ]
)
def update_deg_dist(year_range, option):
    return display_degree_distribution(year_range, option)

@app.callback(
    [
        dash.dependencies.Output('network_properties', 'columns'),
        dash.dependencies.Output('network_properties', 'data'),
    ],
    [
        dash.dependencies.Input('my-range-slider', 'value'),
        dash.dependencies.Input('tabs-styled-with-inline', 'value')
    ]
)
def update_network_properties(year_range, option):
    return [{"name": i, "id": i} for i in display_network_properties(year_range, option).columns], display_network_properties(year_range, option).to_dict('records')
