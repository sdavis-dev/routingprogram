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
            if row and len(row) > 2 and row[2].strip() != "":
                cleaned_row = []
            
                for value in row[2:]:
                    cleaned_row.append(value.strip())

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
    
def get_distance(distances, i, j):
        d = distances[i][j + 1]

        if d == '' or d is None:
            d = distances[j][i + 1]
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
            d = get_distance(distances, current, pkg_index)
            if d < shortest:
                shortest = d
                closest_pkg = pkg

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

print("Total addresses loaded:", len(addresses)) # loads 27 addresses
print(addresses[:5])

"""print("Distance rows:", len(distances)) # come back, rows supposed to match number of addresses
print("Distance columns in row 0:", len(distances[0]))"""

"""pkg = package_table.lookup("2") # checks for address mapping
index = address_index(addresses, pkg.address)

print("package address:", pkg.address)
print("Mapped index:", index)
print("Address at that index:", addresses[index] if index is not None else "Not found")"""

print("Address couont:", len(addresses))
print("Distance rows:", len(distances))
print("Distance columns in row 0:", len(distances[0]))

"""truck1 = Truck("truck1")
nearest_neighbor(truck1, distances, addresses)

for pkg in [package_table.lookup("1"), package_table.lookup("13")]:
    print(pkg.id, pkg.status, pkg.delivery_time)

print("Truck miles:", truck1.miles)
print("Truck time:", convert_time(truck1.time)) """

