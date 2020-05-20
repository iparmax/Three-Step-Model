import pandas as pd
import requests
import numpy as np
import os

def graphhopper_matrix(zones_athens):

    # Graphhopper API key at index 0
    api_key = (pd.read_csv('data/graph_api.csv',header=None).values)[0][0]

    # Transforming the addresses/coordinates matrix to a string
    df = zones_athens['centroid'].values
    list1 = []
    list2 = []
    for i in df:
        list1.append(i[0])
        list2.append(i[1])

    dict_tot = {'lat':list1,'long':list2}
    df = pd.DataFrame(dict_tot)

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