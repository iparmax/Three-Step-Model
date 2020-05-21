# main.py

# Import libraries
from DataGeneration import DataGeneration
from TripDistribution import TripDistribution
from Assignment import Assignment
from config import get_config
import pandas as pd

if __name__ == "__main__":
    
    # Loading configuration 
    pd.set_option('display.float_format', lambda x: '%.0f' % x)    
    args = get_config()

    # First Step
    first_step = DataGeneration(args)
    zones_athens = first_step.get_examined_zones()
    trip_generation = first_step.get_trip_generation()
    print(trip_generation)

    # Second Step
    second_step = TripDistribution(zones_athens)
    try:
        cost_matrix = pd.read_csv('data/tables/DistanceTableAthens.csv',header=None)
    except:
        second_step.cost_matrix()
        cost_matrix = pd.read_csv('data/tables/DistanceTableAthens.csv',header=None)

    cost_matrix.index=zones_athens.NAME
    cost_matrix.columns=zones_athens.NAME
    trips = second_step.gravity_model(trip_generation,cost_matrix)
    print(trips)

    #Third Step
    third_step = Assignment(zones_athens,trips,cost_matrix)
    G = third_step.route_assignement()
    third_step.visualize(G)