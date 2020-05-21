# DataGeneration.py

# Import Libraries 
import requests
import json
import geopandas
import pandas as pd
import unicodedata
from iteround import saferound

class DataGeneration():

    def __init__(self,args):

        self.args = args
        self.url = pd.read_csv(f'data/{self.args.url}.csv',header = None).values[0][0]
        self.zones = geopandas.GeoDataFrame.from_features(requests.get(self.url).json()['features'])
        self.zones['NAME'] = self.zones['NAME'].apply(lambda i: self.strip_accents(i.upper()))
        self.zones['centroid'] = self.zones.apply(self.get_centroid(), axis=1)
        self.data = (pd.read_csv(f'data/{self.args.data}.csv'))
        self.data.index = self.data.NAME

    def strip_accents(self,s):
        return ''.join(c for c in unicodedata.normalize('NFD', s)
            if unicodedata.category(c) != 'Mn')
    
    def get_centroid(self):
        centroid = lambda row: (row['geometry'].centroid.y, row['geometry'].centroid.x)
        return centroid

    def get_examined_zones(self):
        idx = []
        zones_bool = (self.zones['NAME'].isin(self.data['NAME']))
        for index,boolean in zones_bool.iteritems():
            if boolean:
                idx.append(index)          

        zones_athens = geopandas.GeoDataFrame(self.zones,index=idx)
        zones_athens['KWD_YPES'] = zones_athens['KWD_YPES'].astype(int)

        # fix for duplicate cities in geojson
        zones_athens = zones_athens.drop(zones_athens[zones_athens.KWD_YPES > 9250].index)
        zones_athens = zones_athens.reset_index(drop=True)
        return zones_athens

    def get_trip_generation(self):
        self.data['Attraction'] = (self.data['Employment'] * self.data.sum()['Production'] / self.data.sum()['Employment'])
        df = pd.DataFrame(columns = ['Production','Attraction'])
        df['Production'] = self.data['Production']
        round_attraction = (saferound(self.data['Attraction'], places=0))
        mod_attraction = ([int(x) for x in round_attraction])
        df['Attraction']= mod_attraction
        return df
    