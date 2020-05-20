# Import libraries

import requests
import json
import geopandas
from matplotlib import pyplot
from matplotlib import patheffects
import pandas as pd
import unicodedata
from cost_matrix import graphhopper_matrix
from ipfn import ipfn
import networkx
from haversine import haversine

# to remove greek accents 
def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

# assert that cities of table are equal to indices of geojson
df = (pd.read_csv('data/workers.csv'))
column = df['NAME'].values

new_col =[]
for i in column:
    new_col.append(strip_accents(i))

# load map from api 

url = 'https://geodata.gov.gr/geoserver/wfs/?service=WFS&version=1.0.0&request=GetFeature&typeName=geodata.gov.gr:c7b5978b-aca9-4d74-b8a5-d3a48d02f6d0&outputFormat=application/json&srsName=epsg:4326'
r = requests.get(url)
zones = geopandas.GeoDataFrame.from_features(r.json()['features'])
centroidFunction = lambda row: (row['geometry'].centroid.y, row['geometry'].centroid.x)
zones['centroid'] = zones.apply(centroidFunction, axis=1)

# keep the municipalities that are of interest
count = 0
idx = []
for i,j in zip(zones['NAME'],zones['KWD_YPES']):
    string = strip_accents(i.upper())
    if string in new_col and int(j) <= 9250:
        idx.append(count)
    count+=1

# plot map 
zones_athens = geopandas.GeoDataFrame(zones,index=idx)
zones_athens.plot()
pyplot.show()
name = []
print(len(zones_athens['NAME']))
for index, row in zones_athens.iterrows():
    zone1 = row['geometry']
    name1 = row['NAME']
    for index, row in zones_athens.iterrows():
        zone2 = row['geometry']
        name2 = row['NAME']
        if zone2.intersects(zone1) or zone2.contains(zone1):
            if name1 not in name:
                name.append(name1)
            if name2 not in name:
                name.append(name2)
            print(name1,name2)

print(len(name))
print(name)