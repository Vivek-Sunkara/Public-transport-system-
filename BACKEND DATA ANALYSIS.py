import pandas as pd

# Load data from the uploaded Excel file
data = pd.read_excel('/mnt/data/bus route.xlsx')

# Define a function to parse stops from the data
def parse_stops(route_data):
    stops = route_data.split(',')
    return [stop.strip() for stop in stops]

# Create a structured data format for bus routes and stops
bus_routes = {}
for index, row in data.iterrows():
    bus_routes[row['BUS ROUTE NO']] = {
        'distance': row['DISTANCES'],
        'total_stops': row['TOTAL STOPS'],
        'key_stops': parse_stops(row['KEY STOPS']),
        'start_time': row['START TIME'],
        'end_time': row['END TIME'],
        'frequency': row['FREQUENCY FOR EVERY STOP']
    }

# Function to find routes between two stops
def find_direct_route(current_location, destination, bus_routes):
    """
    Finds a direct bus route from the current location to the destination.
    
    Args:
        current_location (str): The starting bus stop.
        destination (str): The ending bus stop.
        bus_routes (dict): Dictionary containing bus route data.
    
    Returns:
        dict or None: Details of the direct route if found, otherwise None.
    """
    for route_no, details in bus_routes.items():
        stops = details['key_stops']
        if current_location in stops and destination in stops:
            if stops.index(current_location) < stops.index(destination):
                return {
                    'route_no': route_no,
                    'stops': stops,
                    'details': details
                }
    return None
def find_indirect_route(current_location, destination, bus_routes):
    """
    Finds an indirect bus route from the current location to the destination with necessary transfers.
    
    Args:
        current_location (str): The starting bus stop.
        destination (str): The ending bus stop.
        bus_routes (dict): Dictionary containing bus route data.
    
    Returns:
        list: A list of route segments, each segment being a dictionary with start, transfer, and end details.
    """
    # Step 1: Find potential transfer points
    start_routes = {route_no: details for route_no, details in bus_routes.items() if current_location in details['key_stops']}
    end_routes = {route_no: details for route_no, details in bus_routes.items() if destination in details['key_stops']}
    
    transfer_options = []
    for start_route_no, start_details in start_routes.items():
        for end_route_no, end_details in end_routes.items():
            common_stops = set(start_details['key_stops']) & set(end_details['key_stops'])
            for transfer_stop in common_stops:
                # Ensure valid direction for both segments
                if (start_details['key_stops'].index(current_location) < start_details['key_stops'].index(transfer_stop) and
                    end_details['key_stops'].index(transfer_stop) < end_details['key_stops'].index(destination)):
                    transfer_options.append({
                        'start_route_no': start_route_no,
                        'start_to_transfer': {
                            'start': current_location,
                            'transfer': transfer_stop,
                            'route_no': start_route_no
                        },
                        'transfer_stop': transfer_stop,
                        'transfer_to_end': {
                            'transfer': transfer_stop,
                            'end': destination,
                            'route_no': end_route_no
                        },
                        'end_route_no': end_route_no
                    })
    
    return transfer_options

# Example usage:
bus_routes = {
    'Route 1': {'key_stops': ['A', 'B', 'C', 'D'], 'other_info': '...'},
    'Route 2': {'key_stops': ['C', 'D', 'E', 'F'], 'other_info': '...'},
    'Route 3': {'key_stops': ['E', 'F', 'G', 'H'], 'other_info': '...'}
}

current_location = 'A'
destination = 'H'

direct_route = find_direct_route(current_location, destination, bus_routes)
if direct_route:
    print("Direct route found:", direct_route)
else:
    indirect_routes = find_indirect_route(current_location, destination, bus_routes)
    if indirect_routes:
        for route in indirect_routes:
            print(f"Transfer at {route['transfer_stop']} from {route['start_route_no']} to {route['end_route_no']}")
            print(f"  - Start with {route['start_to_transfer']['route_no']} from {route['start_to_transfer']['start']} to {route['start_to_transfer']['transfer']}")
            print(f"  - Then take {route['transfer_to_end']['route_no']} from {route['transfer_to_end']['transfer']} to {route['transfer_to_end']['end']}")
    else:
        print("No route found.")

# Mock functions for fare estimates
def get_uber_fare(start, end, vehicle_type):
    # Mock calculation or API call based on vehicle type
    fares = {
        'uberX': 300,
        'uberGo': 250,
        'uberAuto': 100
    }
    return fares.get(vehicle_type, 'Not available')

def get_ola_fare(start, end, vehicle_type):
    fares = {
        'Ola Mini': 200,
        'Ola Prime Sedan': 350,
        'Ola Auto': 100
    }
    return fares.get(vehicle_type, 'Not available')

def get_rapido_fare(start, end, vehicle_type):
    fares = {
        'Rapido Bike': 150
    }
    return fares.get(vehicle_type, 'Not available')

# Updated function to include vehicle types
def get_transportation_options(current_location, destination):
    routes = find_routes(current_location, destination)
    transportation_options = []
    
    for route_no, details in routes:
        transportation_options.append({
            'mode': 'Bus',
            'route_no': route_no,
            'details': details
        })
    
    # Fetching fares for different vehicle types
    vehicle_types = ['uberX', 'uberGo', 'uberAuto', 'Ola Mini', 'Ola Prime Sedan', 'Ola Auto', 'Rapido Bike']
    for vehicle_type in vehicle_types:
        if 'Uber' in vehicle_type:
            fare = get_uber_fare(current_location, destination, vehicle_type)
            transportation_options.append({'mode': 'Uber', 'vehicle_type': vehicle_type, 'fare': fare})
        elif 'Ola' in vehicle_type:
            fare = get_ola_fare(current_location, destination, vehicle_type)
            transportation_options.append({'mode': 'Ola', 'vehicle_type': vehicle_type, 'fare': fare})
        elif 'Rapido' in vehicle_type:
            fare = get_rapido_fare(current_location, destination, vehicle_type)
            transportation_options.append({'mode': 'Rapido', 'vehicle_type': vehicle_type, 'fare': fare})
    
    return transportation_options
def get_transportation_options(current_location, destination):
    routes = find_routes(current_location, destination)
    transportation_options = []
    
    for route_no, details in routes:
        transportation_options.append({
            'mode': 'Bus',
            'route_no': route_no,
            'details': details
        })
    
    # Fetching fares
    uber_fare = get_uber_fare(current_location, destination)
    ola_fare = get_ola_fare(current_location, destination)
    rapido_fare = get_rapido_fare(current_location, destination)
    
    transportation_options.append({'mode': 'Uber', 'fare': uber_fare})
    transportation_options.append({'mode': 'Ola', 'fare': ola_fare})
    transportation_options.append({'mode': 'Rapido', 'fare': rapido_fare})
    
    return transportation_options
