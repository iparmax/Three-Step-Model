import networkx 
import pandas as pd
from matplotlib import pyplot
from matplotlib import patheffects
import geopandas

class Assignment():
    
    def __init__(self,examined_zones,trip_distribution,cost_matrix):
        self.examined_zones = examined_zones
        self.trip_distribution = trip_distribution
        self.cost_matrix = cost_matrix

    def route_assignement(self):
        G = networkx.Graph()
        for index, row in self.examined_zones.iterrows():
            zone1,cent1,name1 = row['geometry'],row['centroid'],row['NAME']
            for index, row in self.examined_zones.iterrows():
                zone2,cent2,name2 = row['geometry'],row['centroid'],row['NAME']
                if zone2.intersects(zone1):
                    G.add_edge(name1, name2, distance = self.cost_matrix.at[name1,name2],volume=0.0)

        for origin in self.trip_distribution:
            for destination in self.trip_distribution:
                path = networkx.shortest_path(G, origin, destination,weight='distance')
                for i in range(len(path) - 1):
                    G[path[i]][path[i + 1]]['volume'] = G[path[i]][path[i + 1]]['volume'] + self.trip_distribution[path[i]][path[i+1]]
        return G

    def visualize(self,G):
        fig = pyplot.figure(1, figsize=(10, 10), dpi=90)
        ax = fig.add_subplot(111)
        examined_zonesT = self.examined_zones
        examined_zonesT.plot(ax = ax)
        for i, row in self.examined_zones.iterrows():
            text = pyplot.annotate(s=row['NAME'], xy=((row['centroid'][1], row['centroid'][0])), horizontalalignment='center', fontsize=6)
            text.set_path_effects([patheffects.Stroke(linewidth=3, foreground='white'), patheffects.Normal()])
        
        for zone in G.edges:
            volume = G[zone[0]][zone[1]]['volume']
            p1 = ((self.examined_zones.loc[self.examined_zones['NAME'] == zone[0],'centroid']).values)[0]
            p2 = ((self.examined_zones.loc[self.examined_zones['NAME'] == zone[1],'centroid']).values)[0]
            x = p1[1], p2[1]
            y = p1[0], p2[0]
            ax.plot(x, y, color='#D61F1F', linewidth=volume/50000, solid_capstyle='round', zorder=1)
            
        pyplot.show()