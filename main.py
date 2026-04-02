# Student ID: 010256107 - (Task C1)

# import statements for csv file imports
import csv

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
        self.truck = None

# Hashtable class for the package (Task A)
class HashTable:
    def __init__(self, size = 40):
        self.table = [[] for _ in range(size)]
    
    def _hash(self, key):
        return int(str(key).strip()) % len(self.table)
    
    def insert(self, package):
        index = self._hash(package.id)
        self.table[index].append(package)
    
    def lookup(self, id): # lookup function that return components of the package with the given id (B)
        index = self._hash(id)
        for package in self.table[index]:
            if package.id == id:
                return package
        return None
    
def load_packages(filename, table): # CSV loader function for the package file
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

def load_distances(filename): # CSV loader function for the distance table
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

def load_addresses(filename): # loads addresses from distance table
    addresses = []
    address_dict = {}
    
    with open(filename, "r", encoding = 'utf-8-sig') as file:
        reader = csv.reader(file)

        for row in reader:
            if row and len(row) > 1:
                address = row[1].strip()
            
                if address != "" and "HUB" not in address:
                    address = address.split("\n")[0]
                    address_dict[address] = len(addresses)
                    addresses.append(address)
    return addresses, address_dict
class Truck: # Truck class 
    def __init__(self, name, start_time = 8.0):
        self.name = name
        self.packages = []
        self.miles = 0
        self.time = start_time
        self.current_location = 0 # The hub index

def convert_time(t): # Converts time to HH:MM
        hours = int(t)
        minutes = int((t - hours) * 60)
        return f"{hours:02d}:{minutes:02d}"

def time_to_float(time_str): # Converts HH:MM to decimal time, updated for AM/PM
    if time_str == "EOD":
        return 24.0
    
    time_str = time_str.strip()

    if "AM" in time_str or "PM" in time_str:
        time_part, period = time_str.split(" ")
        hours, minutes = map(int, time_part.split(":")) # splits time

        if period == "PM" and hours != 12: # 24 hr format conversion
            hours += 12
        if period == "AM" and hours == 12:
            hours = 0
    else:
        hours, minutes = map(int, time_str.split(":"))

    return hours + minutes / 60



def get_distance(distances, i, j): # 
    d = distances[i][j]

    if d == '' or d is None:
        d = distances[j][i]

    d = str(d).strip()

    if d == '':
        return 0.0
    
    return float(d)

def address_index(addresses, address): #
    for i in range(len(addresses)):
        if address in addresses[i]:
            return i
    return None

delayed_packages = {"6", "25", "28", "32"}

def get_package_status(pkg, query_time, address_dict): # updated version of get_package_status()
    if pkg.id in delayed_packages:
        if query_time < time_to_float("9:05"):
            return "delayed on flight" # need a fix for pkg 6, unrealistic delivery time

    if pkg.departure_time is None or query_time < pkg.departure_time:
        return "at the hub"
    
    if pkg.delivery_time is None:
        return "en route"
    
    deliver_time = time_to_float(pkg.delivery_time)

    if query_time < deliver_time:
        return "en route"
    
    return f"Delivered at {pkg.delivery_time}"
def get_display_address(pkg, query_time):
    if pkg.id == "9" and query_time >= time_to_float("10:20"):
        return "410 S State St", "Salt Lake City", "84111"
    return pkg.address, pkg.city, pkg.zip_code

def print_all_status(package_table, query_time, address_dict):
    for bucket in package_table.table:
        for pkg in bucket:
            status = get_package_status(pkg, query_time, address_dict)
            address, city, zip_code = get_display_address(pkg, query_time)

            print(
                "Package:", pkg.id,
                "| Truck:", pkg.truck,
                "| Address:", address,
                "| Deadline:", pkg.deadline,
                "| City:", city,
                "| Weight:", pkg.weight,
                "| Status:", status
            )

def lookup_single_package(package_table, package_id, query_time, address_dict):
    pkg = package_table.lookup(package_id)

    if pkg is None:
        print("Package not found.")
        return
    
    status = get_package_status(pkg, query_time, address_dict)
    address, city, zip_code = get_display_address(pkg, query_time)

    print(
        "Package:", pkg.id,
        "| Truck:", pkg.truck,
        "| Address:", address,
        "| Deadline:", pkg.deadline,
        "| City:", city,
        "| Zip:", zip_code,
        "| Weight:", pkg.weight,
        "| Status:", status
    )

def deadline_to_float(deadline):
    return time_to_float(deadline)

def nearest_neighbor(truck, distances, addresses):
    current = 0 # Start at the hub

    while truck.packages:
        closest_pkg = None
        shortest = float("inf")
        best_score = float("inf")
        
        for pkg in truck.packages:
            if pkg.id in delayed_packages and truck.time < 9.05: # delayed packages to be skipped until 9:05
                continue

            pkg_index = address_index(addresses, pkg.address)
            if pkg_index is None or pkg_index == current:
                continue

            d = get_distance(distances, current, pkg_index)
            deadline = deadline_to_float(pkg.deadline)
            time_remaining = deadline - truck.time

            # urgency for scoring - the lower, the more urgent. add if missed
            eta = truck.time + d / 18.0 
            late_penalty = 1000.0 if eta > deadline else 0.0
            urgency = 1.0 / max(deadline - truck.time, 0.01)

            if pkg.id in delayed_packages and truck.time >= 9.05:
                priority_boost = -200
            else:
                priority_boost = 0

            score = d / 18.0 + urgency * 0.3 + late_penalty + priority_boost

            if score < best_score:
                best_score = score
                closest_pkg = pkg
                shortest = d

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

def main():

    package_table = HashTable()
    load_packages("WGUPS Package File.csv", package_table)
    addresses, address_dict = load_addresses("WGUPS Distance Table.csv")
    distances = load_distances("WGUPS Distance Table.csv")

    distances = load_distances("WGUPS Distance Table.csv")
    addresses, address_dict = load_addresses("WGUPS Distance Table.csv")

    # Create trucks
    truck1 = Truck("1", 8.0)
    truck2 = Truck("2", 9.05)
    truck3 = Truck("3", 10.20)
    
    # manual truck loading to meet deadlines better
    truck1_ids = [
        "15",                           
        "1", "13", "14", "16", "19", "20", "29", "30", "31", "34", "37", "40",
    ]

    truck2_ids = [
        "3", "6", "18", "25", "26", "28", "32", "33", "35", "36", "38", "39"
    ]

    truck3_ids = [
        "2", "4", "5", "7", "8", "9", "10", "11", "12", "17", "21",
        "22", "23", "24", "27"
    ]

    for pid in truck1_ids:
        pkg = package_table.lookup(pid)
        if pkg:
            pkg.truck = truck1.name
            pkg.departure_time = truck1.time
            truck1.packages.append(pkg)
    
    for pid in truck2_ids:
        pkg = package_table.lookup(pid)
        if pkg:
            pkg.truck = truck2.name
            pkg.departure_time = truck2.time
            truck2.packages.append(pkg)
    
    for pid in truck3_ids:
        pkg = package_table.lookup(pid)
        if pkg:
            pkg.truck = truck3.name
            pkg.departure_time = truck3.time
            truck3.packages.append(pkg)

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

    while True: # UI menu

        print("\nWGUPS Routing System")
        print("1 - View All Package Status")
        print("2 - Lookup Package by ID")
        print("3 - Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            user_time = input("Enter time (HH:MM): ")
            query_time = time_to_float(user_time)

            print("\nPackage Status at", user_time)

            print_all_status(package_table, query_time, address_dict)

        elif choice == "2":
            user_time = input("Enter time (HH:MM): ")
            query_time = time_to_float(user_time)

            package_id = input("Enter package ID: ")

            lookup_single_package(package_table, package_id, query_time)

        elif choice == "3":
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()


