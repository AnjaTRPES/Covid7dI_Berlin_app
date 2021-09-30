# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 17:55:33 2021

@author: Anja
"""

import pandas as pd
from shapely.geometry import polygon
from shapely.geometry import MultiPolygon
import geopandas as gpd
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def get_CovidData():
    url_berlin = 'https://www.berlin.de/lageso/gesundheit/infektionskrankheiten/corona/tabelle-bezirke-gesamtuebersicht/'

    data = pd.read_html(url_berlin)[0]
    # Data treatment
    data.Datum = pd.to_datetime(data.Datum, format="%d.%m.%Y")
    data = data[::-1]
    bezirks = ['Mitte', 'Friedrichshain-Kreuzberg', 'Pankow',
               'Charlottenburg-Wilmersdorf', 'Spandau', 'Steglitz-Zehlendorf',
               'Tempelhof-Schöneberg', 'Neukölln', 'Treptow-Köpenick',
               'Marzahn-Hellersdorf', 'Lichtenberg', 'Reinickendorf']
    # rename each bezirk to its full name
    data = data.rename(columns={'MI': 'Mitte',
                                'FK': 'Friedrichshain-Kreuzberg',
                                'PA': 'Pankow',
                                'CW': 'Charlottenburg-Wilmersdorf',
                                'SP': 'Spandau',
                                'SZ': 'Steglitz-Zehlendorf',
                                'TS': 'Tempelhof-Schöneberg',
                                'NK': 'Neukölln',
                                'TK': 'Treptow-Köpenick',
                                'MH': 'Marzahn-Hellersdorf',
                                'LI': 'Lichtenberg', 'RD': 'Reinickendorf'})
    # add a column for the total cases:
    data['All_berlin'] = data[bezirks].mean(axis=1, skipna=True)
    # transform it for each bezirk into the 7day inzidenz
    for bezirk in bezirks:
        data[bezirk+'_7dI'] = data[bezirk].rolling(window=7,
                                                   min_periods=1).mean()
    data['All_berlin_7dI'] = data['All_berlin'].rolling(window=7,
                                                        min_periods=1).mean()

    # Loading the geoapandas bezirksgrenzen
    bezirksgrenzen_url = 'https://tsb-opendata.s3.eu-central-1.amazonaws.com/bezirksgrenzen/bezirksgrenzen.geojson'

    bezirksgrenzen_f = gpd.read_file(bezirksgrenzen_url)

    bezirksgrenzen = bezirksgrenzen_f[["Gemeinde_name",
                                       "geometry"]].set_index("Gemeinde_name")
    bezirks_to_reverse = ['Spandau', 'Steglitz-Zehlendorf', 'Treptow-Köpenick',
                          'Reinickendorf', 'Pankow']

    for bez in bezirks_to_reverse:
        ex = bezirksgrenzen.loc[bez][0]
        ex = MultiPolygon([polygon.orient(ex[i], -1) for i in range(len(ex))])
        bezirksgrenzen.loc[bez] = ex

    bezirks = ['Mitte', 'Friedrichshain-Kreuzberg', 'Pankow',
               'Charlottenburg-Wilmersdorf', 'Spandau', 'Steglitz-Zehlendorf',
               'Tempelhof-Schöneberg', 'Neukölln', 'Treptow-Köpenick',
               'Marzahn-Hellersdorf', 'Lichtenberg', 'Reinickendorf']

    df = pd.DataFrame({'Bezirk': [bezirks[0]]*(len(data.Datum)-1),
                       'Datum': data.Datum[1:],
                       '7dI': data[bezirks[0]+'_7dI'][1:]})
    for bezirk in bezirks[1:]:
        df2 = pd.DataFrame({'Bezirk': [bezirk]*(len(data.Datum)-1),
                            'Datum': data.Datum[1:],
                            '7dI': data[bezirk+'_7dI'][1:]})
        df = pd.concat([df, df2], ignore_index=True)

    # print(df.head(10))
    df.Datum = df.Datum.apply(lambda x: x.strftime('%Y-%m-%d'))

    return data, bezirksgrenzen, df
