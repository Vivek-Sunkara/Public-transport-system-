from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth import get_user_model
import pandas as pd
import random
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Load data from the uploaded Excel file
try:
    data = pd.read_excel('bus route.xlsx')

    # Strip whitespace from column names
    data.columns = data.columns.str.strip()

    # Function to parse stops from the data
    def parse_stops(route_data):
        stops = route_data.split(',')
        return [stop.strip() for stop in stops]

    # Create a structured data format for bus routes and stops
    bus_routes = {}
    for index, row in data.iterrows():
        bus_routes[row['BUS ROUTE NO']] = {
            'distance': row.get('DISTANCES', 'N/A'),  # Default value if the key is not found
            'total_stops': row.get('TOTAL STOPS', 0),  # Default value if the key is not found
            'key_stops': parse_stops(row.get('KEY STOPS', '')),
            'start_time': row.get('START TIME', '00:00'),  # Default value if the key is not found
            'end_time': row.get('END TIME', '00:00'),  # Default value if the key is not found
            'frequency': row.get('FREQUENCY FOR EVERY STOP', 'N/A')  # Default value if the key is not found
        }
except Exception as e:
    print(f"Error loading Excel file: {str(e)}")
    bus_routes = {}  # Initialize as empty to prevent further errors

# Home page view
def pakka_local_view(request):
    return render(request, 'pakka_local.html')

# Registration view
def register(request):
    User = get_user_model()  # Get the custom user model if any
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            try:
                user = User.objects.create_user(username=username, password=password)
                user.save()
                messages.success(request, 'Account created successfully! You can now log in.')
                return redirect('login')  # Change 'login' to the name of your login URL
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            messages.error(request, 'Passwords do not match.')

    return render(request, 'register.html')  # Ensure this path matches your registration template path

# Login view
def loginPage(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('page1')  # Redirect to page1 upon successful login
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Logout view
def logoutPage(request):
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')  # Redirect to the login page after logout

# Page1 (Home) view
from django.shortcuts import render
import random  # Ensure you have this import at the top

def page1_view(request):
    direct_route = None
    indirect_routes = None
    costs = None

    if request.method == "POST":
        current_location = request.POST.get("current_location")
        destination = request.POST.get("destination")

        # Simulated route and transport costs
        direct_route = {
            'route_no': 'Bus 42',
            'stops': ['Stop A', 'Stop B', 'Stop C'],
            'details': {
                'distance': '10 km',
                'total_stops': '3',
                'start_time': '10:00 AM',
                'end_time': '10:30 AM',
            }
        }

        # Generate random costs
        bus_cost = f"Bus: ₹ 0 - {random.randint(0, 100)}"  # Random cost between 0 to 100
        bike_cost = f"Bike: ₹ {random.randint(60, 100)}"
        auto_cost = f"Auto: ₹ {random.randint(90, 150)}"
        car_cost = f"Car: ₹ {random.randint(100, 200)}"

        costs = {
            'bus_cost': bus_cost,
            'rapido': {
                'bike': bike_cost,
                'auto': auto_cost,
                'car': car_cost,
            },
            'ola': {
                'bike': bike_cost,
                'auto': auto_cost,
                'car': car_cost,
            },
            'uber': {
                'bike': bike_cost,
                'auto': auto_cost,
                'car': car_cost,
            },
        }

        # Find routes (existing functionality)
        direct_route = find_direct_route(current_location, destination, bus_routes)
        indirect_routes = find_indirect_route(current_location, destination, bus_routes)

        # Pass both costs and route information to the template
        context = {
            'direct_route': direct_route,
            'indirect_routes': indirect_routes,
            'costs': costs,
        }
        return render(request, 'page1.html', context)

    return render(request, 'page1.html')  # In case of GET request

# Reports view
def reports_view(request):
    # Load data from the Excel file for the reports
    try:
        report_data = pd.read_excel('bus route.xlsx')
        report_data.columns = report_data.columns.str.strip()  # Clean column names
        html_table = report_data.to_html(classes='dataframe', index=False)  # Convert to HTML
    except Exception as e:
        print(f"Error loading report data: {str(e)}")
        html_table = None  # Set to None if there was an error

    return render(request, 'reports.html', {'table': html_table})

# Users view

@login_required
def users_view(request):
    return render(request, 'users.html', {'user': request.user})

@login_required
def update_profile(request):
    user = request.user
    if request.method == 'POST':
        user.username = request.POST['username']
        user.age = request.POST.get('age')
        user.gender = request.POST.get('gender')
        user.email = request.POST['email']
        user.mobile_number = request.POST.get('mobile_number')
        user.address = request.POST.get('address')
        
        if 'profile_pic' in request.FILES:
            user.profile_pic = request.FILES['profile_pic']
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('users')
    
    return render(request, 'settings.html', {'user': user})

# Function to find direct route
def find_direct_route(current_location, destination, bus_routes):
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

# Function to find indirect route
def find_indirect_route(current_location, destination, bus_routes):
    start_routes = {route_no: details for route_no, details in bus_routes.items() if current_location in details['key_stops']}
    end_routes = {route_no: details for route_no, details in bus_routes.items() if destination in details['key_stops']}
    
    transfer_options = []
    for start_route_no, start_details in start_routes.items():
        for end_route_no, end_details in end_routes.items():
            common_stops = set(start_details['key_stops']) & set(end_details['key_stops'])
            for transfer_stop in common_stops:
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
# Reports view
def reports_view(request):
    # Load data from the Excel file for the reports
    try:
        report_data = pd.read_excel('bus route.xlsx')
        report_data.columns = report_data.columns.str.strip()  # Clean column names
        html_table = report_data.to_html(classes='dataframe', index=False)  # Convert to HTML
    except Exception as e:
        print(f"Error loading report data: {str(e)}")
        html_table = None  # Set to None if there was an error

    return render(request, 'reports.html', {'table': html_table})

# Users view
def users_view(request):
    return render(request, 'users.html')

# Settings view
def settings_view(request):
    return render(request, 'settings.html')