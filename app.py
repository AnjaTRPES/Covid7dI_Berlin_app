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


data, bezirksgrenzen, df = get_CovidData()

bezirks = ['Mitte', 'Friedrichshain-Kreuzberg', 'Pankow',
           'Charlottenburg-Wilmersdorf', 'Spandau', 'Steglitz-Zehlendorf',
           'Tempelhof-Schöneberg', 'Neukölln', 'Treptow-Köpenick',
           'Marzahn-Hellersdorf', 'Lichtenberg', 'Reinickendorf']




# The initial figure
time = data.Datum.max()
data_datum_x = data[data.Datum==time]
df = pd.DataFrame({'Bezirk': bezirks,
                   '7dI': [float(data_datum_x[bez+'_7dI']) for bez in bezirks]})
fig = px.choropleth(#_mapbox(
    df, geojson=bezirksgrenzen, color='7dI',
    color_continuous_scale="Viridis",
    locations="Bezirk", #mapbox_style="carto-positron",
    #zoom=9, center = {"lat": 52.5200, "lon": 13.4050},
    #range_color=(0, 80), opacity=0.5)
    labels={'7dI':'7 day incidence rate'})
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},)

fig_total_In = px.line(data, x='Datum',
                       y='All_berlin_7dI',
                       # title='Total 7-day incidence of Berlin',
                       labels={'All_berlin_7dI': 'Total 7-day incidence in Berlin',
                               'Datum': 'Date'})

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Covid 7day incidence in Berlin - timeline",
            style={'textAlign':'center'}),
    dcc.Graph(id="choropleth", figure=fig),
    dcc.Slider(id='timeline',
               min=unixTimeMillis(data.Datum.min()),
               max=unixTimeMillis(data.Datum.max()),
               value=unixTimeMillis(data.Datum.max()),
               marks=getMarks(data.Datum.min(),
                           data.Datum.max(),10),
    ),
    dcc.Graph(id='total_7dIn', figure=fig_total_In)
    
])

@app.callback(
    [Output("choropleth", "figure"),
     Output('total_7dIn', 'figure')],
    [Input("timeline", "value")],
    [State('choropleth', 'relayoutData'),
     State('choropleth', 'figure')]
)

def display_choropleth(time, relayoutData, figure):
    
    time = unixToDatetime(time)
    data_datum_x = data[data.Datum==time]
    z_new = [float(data_datum_x[bez+'_7dI']) for bez in bezirks]
    figure['data'][0]['z'] = z_new
    fig = figure

    fig_total_In = px.line(data,
                           x='Datum',
                           y='All_berlin_7dI',
                           labels={'All_berlin_7dI': 'Total 7-day incidence in Berlin',
                                   'Datum': 'Date'})
    fig_total_In.update_layout(shapes=[
        dict(
          type='line',
          yref='paper', y0=0, y1=1,
          xref='x', x0=time, x1=time
        )
    ])
    return fig, fig_total_In


if __name__ == '__main__':
    app.run_server(debug=False)
