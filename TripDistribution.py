# trip distribution

import requests
import json
import numpy as np
import pandas as pd
import os
from ipfn import ipfn

class TripDistribution():
    
    def __init__(self,examined_zones):

        self.examined_zones = examined_zones
        
        # you have to use an api key from graphhopper and store it as csv on /data directory for cost matrix
        self.api = (pd.read_csv('data/graph_api.csv',header=None).values)[0][0]

    def cost_matrix(self):

        api_key = self.api
        df = self.examined_zones['centroid'].values
        lat = []
        long = []
        for i in df:
            lat.append(i[0])
            long.append(i[1])

        dict_tot = {'lat':lat,'long':long}
        df = pd.DataFrame(dict_tot)

        # Transforming data to string request
        points_str = df.apply(lambda row: f"point={row['lat']},{row['long']}&", axis=1).sum()

        # Making the request for distance and time matrix
        request = f"https://graphhopper.com/api/1/matrix?{points_str}type=json&vehicle=car&debug=true&out_array=weights&out_array=times&out_array=distances&key={api_key}"
        response = requests.get(request).json()
        
        # Creating numpy arrays to store matrixes
        distance_matrix = np.round(np.array(response['distances'])/1000, decimals=2)
        time_matrix = np.round(np.array(response['times'])/60, decimals=1)

        # Returning Dictionaries with matrices            
        response = {"time": time_matrix,"distance":distance_matrix}
        dir = f"data/tables/"
        if not os.path.exists(dir):
            os.makedirs(dir)
        np.savetxt(fname = f'{dir}/DistanceTableAthens.csv', X = distance_matrix, fmt='%1.1f', delimiter=',')
        np.savetxt(fname = f'{dir}/TimeTableAthens.csv', X = time_matrix, fmt='%1.1f', delimiter=',')
        return response
    
    def gravity_model(self,trip_generation, cost_matrix):
        cost_matrix['ozone'] = cost_matrix.columns
        cost_matrix = cost_matrix.melt(id_vars=['ozone'])
        cost_matrix.columns = ['ozone', 'dzone', 'total']
        production = trip_generation['Production']
        production.index.name = 'ozone'
        attraction = trip_generation['Attraction']
        attraction.index.name = 'dzone'
        aggregates = [production, attraction]
        dimensions = [['ozone'], ['dzone']]
        IPF = ipfn.ipfn(cost_matrix, aggregates, dimensions)
        trips = IPF.iteration()
        return(trips.pivot(index='ozone', columns='dzone', values='total'))
