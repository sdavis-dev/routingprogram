# Student ID: 010256107

# import statements for csv file imports and GUI implementation
import csv
import tkinter as tk
from tkinter import ttk

# Package class for each package's details and status
class Package:
    def __init__(self, id, address, deadline, city, zip_code, weight):
        self.id = id
        self.address = address
        self.deadline = deadline
        self.city = city
        self.zip_code = zip_code
        self.weight = weight
        self.status = "at the hub"
        self.delivery_time = None
        self.address_index = None
        self.departure_time = None

# Hashtable class for the package 
class HashTable:
    def __init__(self, size = 40):
        self.table = [[] for _ in range(size)]
    
    def _hash(self, key):
        return int(str(key).strip()) % len(self.table)
    
    def insert(self, package):
        index = self._hash(package.id)
        self.table[index].append(package)
    
    def lookup(self, id): # lookup function that return components of the package with the given id
        index = self._hash(id)
        for package in self.table[index]:
            if package.id == id:
                return package
        return None
    
def load_packages(filename, table):
    with open(filename, 'r', encoding = 'utf-8-sig') as file:
        reader = csv.reader(file)
        
        for row in reader:

            if not row:
                continue

            try:
                int(row[0].strip())
            except ValueError:
                continue

            if row[0].strip() == '':
                continue
            package = Package(
                row[0].strip(), # id
                row[1].strip(), # address
                row[5].strip(), # deadline
                row[2].strip(), # city
                row[4].strip(), # zip code
                row[6].strip()  # weight
                )
            table.insert(package)

def load_distances(filename):
    distances = []
    start_reading = False

    with open(filename, "r", encoding = 'utf-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            if row and "DISTANCE BETWEEN HUBS IN MILES" in row[0]: # this fixes the reading issue by the actual header now
                start_reading = True
                continue
            
            if start_reading:
                if not row or row[0].strip() == "": # skip blanks
                    continue
            
            numeric_found = False
            for cell in row:
                try:
                    float(cell)
                    numeric_found = True
                    break
                except:
                    continue

            if numeric_found:
                cleaned_row = [value.strip() for value in row[2:]]
                distances.append(cleaned_row)

    return distances

class Truck:
    def __init__(self, name, start_time = 8.0):
        self.name = name
        self.packages = []
        self.miles = 0
        self.time = start_time
        self.current_location = 0 # The hub index

def convert_time(t):
        hours = int(t)
        minutes = int((t - hours) * 60)
        return f"{hours:02d}:{minutes:02d}"

def time_to_float(time_str):
    hours, minutes = map(int, time_str.split(":"))
    return hours + minutes / 60

def get_distance(distances, i, j):
        d = distances[i][j]

        if d == '' or d is None:
            d = distances[j][i]
        d = str(d).strip()
        if d == '':
            return 0.0
        return float(d)

def load_addresses(filename):
    addresses = []
    start_reading = False
    
    with open(filename, "r", encoding = 'utf-8-sig') as file:
        reader = csv.reader(file)

        for row in reader:
            if row and len(row) > 1:
                address = row[1].strip()
            
            if address != "" and "HUB" not in address:
                address = address.split("\n")[0]
                addresses.append(address)
    return addresses

def address_index(addresses, address):
    for i in range(len(addresses)):
        if address in addresses[i]:
            return i
    return None

def nearest_neighbor(truck, distances, addresses):
    current = 0 # Start at the hub

    while truck.packages:
        closest_pkg = None
        shortest = float("inf")

        for pkg in truck.packages:
            pkg_index = address_index(addresses, pkg.address)

            if pkg_index is None:
                continue # this allows a skip if address is not found
            
            if pkg_index == current:
                continue

            d = get_distance(distances, current, pkg_index)

            if d < shortest:
                shortest = d
                closest_pkg = pkg

        if closest_pkg is None:
            break

        travel_time = shortest / 18.0 # Assuming average speed of 18 mph
        truck.time += travel_time
        truck.miles += shortest

        closest_pkg.status = "delivered"
        closest_pkg.delivery_time = convert_time(truck.time)

        truck.current_location = address_index(addresses, closest_pkg.address)
        current = truck.current_location
        truck.packages.remove(closest_pkg)

        """print(f"Truck {truck.name} delivering package {closest_pkg.id}")
        print(f"Distance traveled: {shortest}")
        print(f"Arrival time: {convert_time(truck.time)}")
        print("-" * 30) """

package_table = HashTable()
load_packages("WGUPS Package File.csv", package_table)
addresses = load_addresses("WGUPS Distance Table.csv")
distances = load_distances("WGUPS Distance Table.csv")

"""for i in range(1, 41): # testing for all 40 packages printing
    pkg = package_table.lookup(str(i))
    if pkg:
        print(pkg.id, pkg.address, pkg.status)
    else:
        print("Missing package:", i)"""

"""print("Total addresses loaded:", len(addresses)) # loads 27 addresses
print(addresses[:5]) """

"""print("Distance rows:", len(distances)) # come back, rows supposed to match number of addresses
print("Distance columns in row 0:", len(distances[0]))"""

"""pkg = package_table.lookup("2") # checks for address mapping
index = address_index(addresses, pkg.address)

print("package address:", pkg.address)
print("Mapped index:", index)
print("Address at that index:", addresses[index] if index is not None else "Not found")"""

"""print("Address couont:", len(addresses))
print("Distance rows:", len(distances))
print("Distance columns in row 0:", len(distances[0]))"""

"""truck1 = Truck("truck1")
nearest_neighbor(truck1, distances, addresses)

for pkg in [package_table.lookup("1"), package_table.lookup("13")]:
    print(pkg.id, pkg.status, pkg.delivery_time)

print("Truck miles:", truck1.miles)
print("Truck time:", convert_time(truck1.time)) """

"""print("Hub:", addresses[0])
print("First location:", addresses[1])

print("Distance HUB to location 1:", get_distance(distances, 0, 1))

print(len(distances))
print(len(distances[0]))
print(distances[0][:10])
print(distances[1][:10])

nearest_neighbor(truck1, distances, addresses)
print("Truck miles:", truck1.miles)"""

# Create trucks
truck1 = Truck("1", 8.0)
truck2 = Truck("2", 9.05)
truck3 = Truck("3", 10.20)

# Load packages onto trucks (temporary example)
for i in range(1, 15):
    pkg = package_table.lookup(str(i))
    if pkg:
        truck1.packages.append(pkg)

for i in range(15, 30):
    pkg = package_table.lookup(str(i))
    if pkg:
        truck2.packages.append(pkg)

for i in range(30, 41):
    pkg = package_table.lookup(str(i))
    if pkg:
        truck3.packages.append(pkg)

for pkg in truck1.packages:
    pkg.departure_time = truck1.time

for pkg in truck2.packages:
    pkg.departure_time = truck2.time

for pkg in truck3.packages:
    pkg.departure_time = truck3.time

# Run routing algorithm
nearest_neighbor(truck1, distances, addresses)
nearest_neighbor(truck2, distances, addresses)
nearest_neighbor(truck3, distances, addresses)

# Print mileage results
print("Truck 1 miles:", truck1.miles)
print("Truck 2 miles:", truck2.miles)
print("Truck 3 miles:", truck3.miles)

total_miles = truck1.miles + truck2.miles + truck3.miles
print("Total miles:", total_miles)

