# Import libraries

import requests
import json
import geopandas
from matplotlib import pyplot
from matplotlib import patheffects
import pandas as pd
import unicodedata


def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')



# get map

# assert that cities of table are equal to indices of geojson
df = (pd.read_csv('data/workers.csv',header=None))
column = df[0].values

new_col =[]
for i in column:
    new_col.append(strip_accents(i[6:]))

# 

url = 'https://geodata.gov.gr/geoserver/wfs/?service=WFS&version=1.0.0&request=GetFeature&typeName=geodata.gov.gr:c7b5978b-aca9-4d74-b8a5-d3a48d02f6d0&outputFormat=application/json&srsName=epsg:4326'

r = requests.get(url)
zones = geopandas.GeoDataFrame.from_features(r.json()['features'])
centroidFunction = lambda row: (row['geometry'].centroid.y, row['geometry'].centroid.x)
zones['centroid'] = zones.apply(centroidFunction, axis=1)

count = 0
idx = []
for i,j in zip(zones['NAME'],zones['KWD_YPES']):
    string = strip_accents(i.upper())
    if string in new_col and int(j) <= 9250:
        idx.append(count)
    count+=1

print((len(idx)))
zones_athens = geopandas.GeoDataFrame(zones,index=idx)
zones_athens.plot()
pyplot.show()