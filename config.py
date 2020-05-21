#config.py

# Triply Platform by Liagkouras 
# Loading configuration of optimization

# Importing Libraries
import argparse

def get_config():

    # Creating configuration file
    parser = argparse.ArgumentParser(description='Configuration file of Three Step Model.')

    # Required Input for main.py
    group = parser.add_argument_group('Required Arguments (Marked with asterisk)')
    group.add_argument('-u','--url', type=str,metavar='*', required=True, help = 'Namefile of csv containing the URL that load the GeoJson of examined city\
    to extract location data')
    group.add_argument('-d','--data', type=str,metavar='*', required=True, help = 'Namefile of csv containing Production/Employment for examined city.')

    return parser.parse_args()