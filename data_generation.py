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
zones_athens['NAME'] = zones_athens['NAME'].apply(lambda i: strip_accents(i.upper()))
#graphhopper_matrix(zones_athens)

df['Attraction'] = (df['Employment'] * df.sum()['Production'] / df.sum()['Employment'])
df.index = df.NAME
df.sort_index(inplace=True)

pd.set_option('display.float_format', lambda x: '%.0f' % x)
trip_generation = df[['Production', 'Attraction']]
print(len(df))
print(len(zones_athens))
cost_matrix = pd.read_csv('data/tables/DistanceTableAthens.csv',header=None)
print((cost_matrix))
cost_matrix.index=df.index
cost_matrix.columns=df.index


print(trip_generation)
print(cost_matrix)
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
driving_trips = trips.values/2
driving_trips = pd.DataFrame(driving_trips)
driving_trips.index=trips.index
driving_trips.columns=trips.columns

def routeAssignment(zones, trips):
  G = networkx.Graph()
  for index, row in zones_athens.iterrows():
    zone1,cent1,name1 = row['geometry'],row['centroid'],strip_accents(row['NAME'].upper())
    for index, row in zones_athens.iterrows():
      zone2,cent2,name2 = row['geometry'],row['centroid'],strip_accents(row['NAME'].upper())
      if zone2.intersects(zone1):
        G.add_edge(name1, name2, distance = cost_matrix.at[name1,name2],volume=0.0)
  for origin in trips:
    for destination in trips:
      path = networkx.shortest_path(G, origin, destination,weight='distance')
      for i in range(len(path) - 1):
        G[path[i]][path[i + 1]]['volume'] = G[path[i]][path[i + 1]]['volume'] + trips[path[i]][path[i+1]]
  return(G)

def visualize(G, zones):
  fig = pyplot.figure(1, figsize=(10, 10), dpi=90)
  ax = fig.add_subplot(111)
  zonesT = zones
  zonesT.plot(ax = ax)
  for i, row in zones.iterrows():
    text = pyplot.annotate(s=row['NAME'], xy=((row['centroid'][1], row['centroid'][0])), horizontalalignment='center', fontsize=6)
    text.set_path_effects([patheffects.Stroke(linewidth=3, foreground='white'), patheffects.Normal()])
  for zone in G.edges:
    volume = G[zone[0]][zone[1]]['volume']
    p1 = ((zones.loc[zones['NAME'] == zone[0],'centroid']).values)[0]
    p2 = ((zones.loc[zones['NAME'] == zone[1],'centroid']).values)[0]
    x = p1[1], p2[1]
    y = p1[0], p2[0]
    ax.plot(x, y, color='#D61F1F', linewidth=volume/50000, solid_capstyle='round', zorder=1)
  pyplot.show()

G = routeAssignment(zones_athens,driving_trips)
visualize(G, zones_athens)