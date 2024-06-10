import os
import sqlite3
import json
from vessel import Vessel
from port import Port
from shipment import Shipment

# Constants for database and JSON file paths
DATABASE_PATH = "shipments.db"
JSON_FILE_PATH = "shipments.json"

def initialize_database():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        # Create tables if they don't exist
        create_tables(cursor)

        # Check if tables are empty
        tables = ["vessels", "ports", "shipments"]
        empty_tables = {table: is_table_empty(cursor, table) for table in tables}

        if any(empty_tables.values()):
            print("Populating the database with JSON data...")
            populate_database(cursor)
        else:
            print("Database is already populated.")

        conn.commit()  # Commit changes

def create_tables(cursor):
    """
    Create the necessary tables if they do not exist.
    """
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ports (
            id TEXT PRIMARY KEY,
            code INTEGER,
            name TEXT,
            city TEXT,
            province TEXT,
            country TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vessels (
            imo INTEGER PRIMARY KEY,
            mmsi INTEGER,
            name TEXT,
            country TEXT,
            type TEXT,
            build INTEGER,
            gross INTEGER,
            netto INTEGER,
            length INTEGER,
            beam INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shipments (
            id TEXT PRIMARY KEY,
            date TEXT,
            cargo_weight INTEGER,
            distance_naut REAL,
            duration_hours REAL,
            average_speed REAL,
            origin TEXT,
            destination TEXT,
            vessel INTEGER,
            FOREIGN KEY (origin) REFERENCES ports(id),
            FOREIGN KEY (destination) REFERENCES ports(id),
            FOREIGN KEY (vessel) REFERENCES vessels(imo)
        )
    ''')

def is_table_empty(cursor, table_name):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    return count == 0

def populate_database(cursor):
    with open(JSON_FILE_PATH, 'r') as file:
        json_data = json.load(file)

    for entry in json_data:
        origin = entry["origin"]
        destination = entry["destination"]

        # Insert origin port data
        cursor.execute("""
            INSERT OR IGNORE INTO ports (id, code, name, city, province, country)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (origin["id"], origin["code"], origin["name"], origin["city"], origin["province"], origin["country"]))

        # Insert destination port data
        cursor.execute("""
            INSERT OR IGNORE INTO ports (id, code, name, city, province, country)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (destination["id"], destination["code"], destination["name"], destination["city"], destination["province"], destination["country"]))

        vessel = entry["vessel"]
        length, beam = map(int, vessel["size"].split(" / "))

        # Insert vessel data
        cursor.execute("""
            INSERT OR IGNORE INTO vessels (imo, mmsi, name, country, type, build, gross, netto, length, beam)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (vessel["imo"], vessel["mmsi"], vessel["name"], vessel["country"], vessel["type"], vessel["build"], vessel["gross"], vessel["netto"], length, beam))

        # Insert shipment data
        cursor.execute("""
            INSERT INTO shipments (id, date, cargo_weight, distance_naut, duration_hours, average_speed, origin, destination, vessel)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (entry["tracking_number"], entry["date"], entry["cargo_weight"], entry["distance_naut"], entry["duration_hours"], entry["average_speed"], origin["id"], destination["id"], vessel["imo"]))

def fetch_all_ports():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ports")
        ports = cursor.fetchall()

    return [Port(*port) for port in ports]

def fetch_all_vessels():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vessels")
        vessels = cursor.fetchall()

    return [Vessel(*vessel) for vessel in vessels]

def fetch_all_shipments():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shipments")
        shipments = cursor.fetchall()

    return [Shipment(*shipment) for shipment in shipments]

def fetch_port_details(port_id):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ports WHERE id = ?", (port_id,))
        port_data = cursor.fetchone()

    if port_data:
        return Port(*port_data)
    else:
        print(f"Port with ID {port_id} not found.")
        return None

def fetch_vessel_details(imo):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vessels WHERE imo = ?", (imo,))
        vessel_data = cursor.fetchone()

    if vessel_data:
        return Vessel(*vessel_data)
    else:
        print(f"Vessel with IMO {imo} not found.")
        return None

def fetch_shipment_details(shipment_id):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shipments WHERE id = ?", (shipment_id,))
        shipment_data = cursor.fetchone()

    if shipment_data:
        return Shipment(*shipment_data)
    else:
        print(f"Shipment with ID {shipment_id} not found.")
        return None

def main():
    # Initialize the database
    initialize_database()

if __name__ == "__main__":
    main()
