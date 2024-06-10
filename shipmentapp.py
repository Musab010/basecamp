import os
import sqlite3
import json
from vessel import Vessel
from port import Port
from shipment import Shipment

DATABASE_PATH = "shipments.db"  # Pad naar de database
JSON_FILE_PATH = "shipments.json"  # Pad naar het JSON-bestand

def initialize_database():
    """
    Initialiseer de database en vul deze met gegevens uit het JSON-bestand als de tabellen leeg zijn.
    """
    conn = sqlite3.connect(DATABASE_PATH)  # Verbinding maken met de database
    cursor = conn.cursor()  # Een cursor-object aanmaken om SQL-query's uit te voeren

    def is_table_empty(table_name):
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        return count == 0

    # Controleer of de tabellen leeg zijn
    tables = ["vessels", "ports", "shipments"]
    empty_tables = {table: is_table_empty(table) for table in tables}

    if any(empty_tables.values()):
        print("De database vullen met JSON-gegevens...")
        populate_database(cursor)
    else:
        print("De database is al gevuld.")

    conn.commit()  # Wijzigingen bevestigen
    conn.close()  # De databaseverbinding sluiten

def populate_database(cursor):
    """
    Vul de database met gegevens uit het JSON-bestand.
    """
    with open(JSON_FILE_PATH, 'r') as file:
        json_data = json.load(file)  # Lees de JSON-gegevens

    for entry in json_data:
        origin = entry["origin"]
        destination = entry["destination"]
        
        # Voeg de gegevens van de oorsprongshaven toe
        cursor.execute("""
            INSERT OR IGNORE INTO ports (id, code, name, city, province, country)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (origin["id"], origin["code"], origin["name"], origin["city"], origin["province"], origin["country"]))

        # Voeg de gegevens van de bestemmingshaven toe
        cursor.execute("""
            INSERT OR IGNORE INTO ports (id, code, name, city, province, country)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (destination["id"], destination["code"], destination["name"], destination["city"], destination["province"], destination["country"]))

        vessel = entry["vessel"]
        length, beam = map(int, vessel["size"].split(" / "))  # Converteer de grootte naar lengte en breedte
        
        # Voeg de gegevens van het schip toe
        cursor.execute("""
            INSERT OR IGNORE INTO vessels (imo, mmsi, name, country, type, build, gross, netto, length, beam)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (vessel["imo"], vessel["mmsi"], vessel["name"], vessel["country"], vessel["type"], vessel["build"], vessel["gross"], vessel["netto"], length, beam))

        # Voeg de zendinggegevens toe
        cursor.execute("""
            INSERT INTO shipments (id, date, cargo_weight, distance_naut, duration_hours, average_speed, origin, destination, vessel)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (entry["tracking_number"], entry["date"], entry["cargo_weight"], entry["distance_naut"], entry["duration_hours"], entry["average_speed"], origin["id"], destination["id"], vessel["imo"]))

def fetch_all_ports():
    """
    Haal alle havens op uit de database.
    """
    conn = sqlite3.connect(DATABASE_PATH)  # Verbinding maken met de database
    cursor = conn.cursor()  # Een cursor-object aanmaken om SQL-query's uit te voeren

    cursor.execute("SELECT * FROM ports")
    ports = cursor.fetchall()  # Alle havens ophalen
    conn.close()  # De databaseverbinding sluiten

    return [Port(*port) for port in ports]  # Retourneer een lijst van Port-instanties

def fetch_all_vessels():
    """
    Haal alle schepen op uit de database.
    """
    conn = sqlite3.connect(DATABASE_PATH)  # Verbinding maken met de database
    cursor = conn.cursor()  # Een cursor-object aanmaken om SQL-query's uit te voeren

    cursor.execute("SELECT * FROM vessels")
    vessels = cursor.fetchall()  # Alle schepen ophalen
    conn.close()  # De databaseverbinding sluiten

    return [Vessel(*vessel) for vessel in vessels]  # Retourneer een lijst van Vessel-instanties

def fetch_all_shipments():
    """
    Haal alle zendingen op uit de database.
    """
    conn = sqlite3.connect(DATABASE_PATH)  # Verbinding maken met de database
    cursor = conn.cursor()  # Een cursor-object aanmaken om SQL-query's uit te voeren

    cursor.execute("SELECT * FROM shipments")
    shipments = cursor.fetchall()  # Alle zendingen ophalen
    conn.close()  # De databaseverbinding sluiten

    return [Shipment(*shipment) for shipment in shipments]  # Retourneer een lijst van Shipment-instanties

def fetch_port_details(port_id):
    """
    Haal de details op van een specifieke haven op basis van ID.
    """
    conn = sqlite3.connect(DATABASE_PATH)  # Verbinding maken met de database
    cursor = conn.cursor()  # Een cursor-object aanmaken om SQL-query's uit te voeren

    cursor.execute("SELECT * FROM ports WHERE id = ?", (port_id,))
    port_data = cursor.fetchone()  # Haal de gegevens van de haven op
    conn.close()  # De databaseverbinding sluiten

    if port_data:
        return Port(*port_data)  # Retourneer een Port-instantie
    else:
        print(f"Haven met ID {port_id} niet gevonden.")
        return None

def fetch_vessel_details(imo):
    """
    Haal de details op van een specifiek schip op basis van IMO.
    """
    conn = sqlite3.connect(DATABASE_PATH)  # Verbinding maken met de database
    cursor = conn.cursor()  # Een cursor-object aanmaken om SQL-query's uit te voeren

    cursor.execute("SELECT * FROM vessels WHERE imo = ?", (imo,))
    vessel_data = cursor.fetchone()  # Haal de gegevens van het schip op
    conn.close()  # De databaseverbinding sluiten

    if vessel_data:
        return Vessel(*vessel_data)  # Retourneer een Vessel-instantie
    else:
        print(f"Schip met IMO {imo} niet gevonden.")
        return None

def fetch_shipment_details(shipment_id):
    """
    Haal de details op van een specifieke zending op basis van ID.
    """
    conn = sqlite3.connect(DATABASE_PATH)  # Verbinding maken met de database
    cursor = conn.cursor()  # Een cursor-object aanmaken om SQL-query's uit te voeren

    cursor.execute("SELECT * FROM shipments WHERE id = ?", (shipment_id,))
    shipment_data = cursor.fetchone()  # Haal de gegevens van de zending op
    conn.close()  # De databaseverbinding sluiten

    if shipment_data:
        return Shipment(*shipment_data)  # Retourneer een Shipment-instantie
    else:
        print(f"Zending met ID {shipment_id} niet gevonden.")
        return None

def main():
    # Initialiseer de database
    initialize_database()

if __name__ == "__main__":
    main()
