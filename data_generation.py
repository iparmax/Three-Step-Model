# Import libraries

import requests
import json
import geopandas
from matplotlib import pyplot
from matplotlib import patheffects
import pandas as pd
import unicodedata
from test import graphhopper_matrix
from ipfn import ipfn

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

df['Attraction'] = (df['Attraction'] * df.sum()['Production'] / df.sum()['Attraction'])
df.index = df.NAME
df.sort_index(inplace=True)

pd.set_option('display.float_format', lambda x: '%.0f' % x)
trip_generation = df[['Production', 'Attraction']]

cost_matrix = pd.read_csv('data/tables/DistanceTableAthens.csv',header=None)
cost_matrix.index=df.index
cost_matrix.columns=df.index

def tripDistribution(tripGeneration, costMatrix):
    costMatrix['ozone'] = costMatrix.columns
    costMatrix = costMatrix.melt(id_vars=['ozone'])
    costMatrix.columns = ['ozone', 'dzone', 'total']
    production = tripGeneration['Production']
    production.index.name = 'ozone'
    attraction = tripGeneration['Attraction']
    attraction.index.name = 'dzone'
    aggregates = [production, attraction]
    dimensions = [['ozone'], ['dzone']]
    IPF = ipfn.ipfn(costMatrix, aggregates, dimensions)
    trips = IPF.iteration()
    return(trips.pivot(index='ozone', columns='dzone', values='total'))

trips = tripDistribution(trip_generation, cost_matrix)
print(trips)
print(trip_generation)

#print(trips)