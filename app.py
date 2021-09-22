# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 17:35:03 2021

@author: Anja
"""

import pandas as pd
from load_data import get_CovidData
from help_timer_functions import *
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px

template = 'plotly_dark'

data, bezirksgrenzen, df = get_CovidData()

bezirks = ['Mitte', 'Friedrichshain-Kreuzberg', 'Pankow',
           'Charlottenburg-Wilmersdorf', 'Spandau', 'Steglitz-Zehlendorf',
           'Tempelhof-Schöneberg', 'Neukölln', 'Treptow-Köpenick',
           'Marzahn-Hellersdorf', 'Lichtenberg', 'Reinickendorf']


max_z = data[['Mitte_7dI', 'Friedrichshain-Kreuzberg_7dI', 'Pankow_7dI',
              'Charlottenburg-Wilmersdorf_7dI', 'Spandau_7dI',
              'Steglitz-Zehlendorf_7dI', 'Tempelhof-Schöneberg_7dI',
              'Neukölln_7dI',
              'Treptow-Köpenick_7dI', 'Marzahn-Hellersdorf_7dI',
              'Lichtenberg_7dI',
              'Reinickendorf_7dI']].max().max()

# The initial figure
time = data.Datum.max()
data_datum_x = data[data.Datum == time]
df = pd.DataFrame({'Bezirk': bezirks,
                   '7dI': [float(data_datum_x[bez + '_7dI']) for bez in bezirks]})
fig = px.choropleth(
    df, geojson=bezirksgrenzen, color='7dI',
    color_continuous_scale="Viridis",
    locations="Bezirk",
    range_color=(0, max_z),
    labels={'7dI': '7 day \nincidence'})
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    template=template)

fig_total_In = px.line(data, x='Datum',
                       y='All_berlin_7dI',
                       # title='Total 7-day incidence of Berlin',
                       labels={'All_berlin_7dI': 'Total 7-day incidence in Berlin',
                               'Datum': 'Date'})
fig_total_In.update_layout(shapes=[
        dict(
          type='line',
          yref='paper', y0=0, y1=1,
          xref='x', x0=time, x1=time
        )
    ], template=template)





app = dash.Dash(__name__,
                title='Covid-incidence-Berlin')
server = app.server

app.layout = html.Div([
    html.Div([
        html.H1("Covid 7-day incidence in Berlin - timeline",
                style={'textAlign': 'center', 'width': "80%", 
                       "display": "inline-block"}),
        html.Label(["Created by ",
                    html.A("Anja", href='https://github.com/AnjaTRPES/Covid7dI_Berlin_app'),
                    " using ",
                    html.A("Dash and Plotly", href='https://plotly.com/dash/')
                    ],
               style={"width": "18%","display": "inline-block"})
    ]),
    html.Div([
        html.Div([
            dcc.Graph(id="choropleth", figure=fig)],
            style={"width": "80%", "display": "inline-block",
                   "height": "100%"}),
        html.Div([
            html.Div([
                dcc.Input(id="z_max",
                          type="number",
                          placeholder="Max 7day incidence",
                          value=int(max_z),
                          style={"width": "18%",
                                 "display": "inline-block"}),
                html.Div(['Max 7day incidence'],
                         style={"width": "50%",
                                "display": "inline-block",
                                "margin-left": "2px"})
                ],
                style={"position": "absolute",
                       "top": "10px"}),
            html.Div([
                dcc.Input(id="z_min",
                          type="number",
                          placeholder="max 7day incidence",
                          value=int(0),
                          style={"width": "18%",
                                 "display": "inline-block"}),
                html.Div(['Min 7day incidence'],
                         style={"width": "50%",
                                "display": "inline-block",
                                "margin-left": "2px"})],
                style={"position":"absolute",
                       "bottom": "1px"}
                )],
                 style={"width":"19%","display": "inline-block",
                        "height": "100%",
                        "position":"absolute",
                        "top":"0px"})
        ],
        style ={"position":"relative",
                "top": "0px"}),
    html.Div([
        dcc.Slider(id='timeline',
                   min=unixTimeMillis(data.Datum.min()),
                   max=unixTimeMillis(data.Datum.max()),
                   value=unixTimeMillis(data.Datum.max()),
                   marks=getMarks(data.Datum.min(),
                               data.Datum.max(),10),
                   included=False)],
        style={"margin-left":"3.5%",
               "margin-right": "3.5%"}
               
    ),
    dcc.Graph(id='total_7dIn', figure=fig_total_In)
    
], style={'height': "99%"})




@app.callback(
    [Output("choropleth", "figure"),
     Output('total_7dIn', 'figure')],
    [Input("timeline", "value"),
     Input("z_min", "value"),
     Input("z_max", "value")],
    [State('choropleth', 'relayoutData'),
     State('choropleth', 'figure'),
     State('total_7dIn', 'figure')]
)
def display_choropleth(time, z_min, z_max, relayoutData, figure, figure7dI):
    print('triggered the callback', flush=True)
    # determine which input was triggerd
    ctx = dash.callback_context
    print(ctx)
    if not ctx.triggered:
        print('wasnt triggered')
        #pass
    else:
        print('apparantly was triggered!')
        print(ctx.triggered)
        if ctx.triggered[0]['prop_id'] == 'timeline.value':
            time = unixToDatetime(time)
            data_datum_x = data[data.Datum == time]
            z_new = [float(data_datum_x[bez+'_7dI']) for bez in bezirks]
            figure['data'][0]['z'] = z_new
            figure7dI['layout']['shapes'] = [
                dict(
                  type='line',
                  yref='paper', y0=0, y1=1,
                  xref='x', x0=time, x1=time
                )
            ]
        else:
            figure['layout']['coloraxis']['cmin'] = z_min
            figure['layout']['coloraxis']['cmax'] = z_max
    '''
    time = unixToDatetime(time)
    data_datum_x = data[data.Datum == time]
    z_new = [float(data_datum_x[bez+'_7dI']) for bez in bezirks]
    figure['data'][0]['z'] = z_new
    figure7dI['layout']['shapes'] = [
        dict(
          type='line',
          yref='paper', y0=0, y1=1,
          xref='x', x0=time, x1=time
        )
    ]
    figure['layout']['coloraxis']['cmin'] = z_min
    figure['layout']['coloraxis']['cmax'] = z_max
    '''
    return figure, figure7dI



    


if __name__ == '__main__':
    app.run_server(debug=False)


































