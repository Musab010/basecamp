import csv
import os
import sys
from vessel import Vessel
from port import Port
from shipment import Shipment
from datetime import date
import sqlite3

DATABASE_PATH = "shipments.db"

class Reporter:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.cursor = self.conn.cursor()

    # How many vessels are there? -> int
    def total_amount_of_vessels(self) -> int:
        """
        Retourneer het totale aantal schepen in de database.
        """
        self.cursor.execute("SELECT COUNT(*) FROM vessels")
        result = self.cursor.fetchone()
        return result[0] if result else 0

    # What is the longest shipment distance? -> Shipment
    def longest_shipment(self) -> Shipment:
        """
        Retourneer de zending met de langste afstand.
        """
        self.cursor.execute("SELECT * FROM shipments ORDER BY distance_naut DESC LIMIT 1")
        shipment_data = self.cursor.fetchone()
        return Shipment(*shipment_data) if shipment_data else None

    # What is the longest and shortest vessel? -> tuple[Vessel, Vessel]
    def longest_and_shortest_vessels(self) -> "tuple[Vessel, Vessel]":
        """
        Retourneer het langste en het kortste schip.
        """
        self.cursor.execute("SELECT * FROM vessels ORDER BY length DESC LIMIT 1")
        longest_vessel_data = self.cursor.fetchone()
        
        self.cursor.execute("SELECT * FROM vessels ORDER BY length ASC LIMIT 1")
        shortest_vessel_data = self.cursor.fetchone()
        
        longest_vessel = Vessel(*longest_vessel_data) if longest_vessel_data else None
        shortest_vessel = Vessel(*shortest_vessel_data) if shortest_vessel_data else None

        return (longest_vessel, shortest_vessel)

    # What is the widest and smallest vessel? -> tuple[Vessel, Vessel]
    def widest_and_smallest_vessels(self) -> "tuple[Vessel, Vessel]":
        """
        Retourneer het breedste en het kleinste (qua breedte) schip.
        """
        self.cursor.execute("SELECT * FROM vessels ORDER BY beam DESC LIMIT 1")
        widest_vessel_data = self.cursor.fetchone()
        
        self.cursor.execute("SELECT * FROM vessels ORDER BY beam ASC LIMIT 1")
        smallest_vessel_data = self.cursor.fetchone()
        
        widest_vessel = Vessel(*widest_vessel_data) if widest_vessel_data else None
        smallest_vessel = Vessel(*smallest_vessel_data) if smallest_vessel_data else None

        return (widest_vessel, smallest_vessel)

    # Which vessels have the most shipments -> tuple[Vessel, ...]
    def vessels_with_the_most_shipments(self) -> "tuple[Vessel, ...]":
        """
        Retourneer de schepen met de meeste zendingen.
        """
        self.cursor.execute("""
            SELECT vessel, COUNT(*) as shipment_count
            FROM shipments
            GROUP BY vessel
            ORDER BY shipment_count DESC
        """)
        vessel_data = self.cursor.fetchall()

        if not vessel_data:
            return tuple()

        max_shipments = vessel_data[0][1]
        vessels = [Vessel(*self.fetch_vessel_by_imo(data[0])) for data in vessel_data if data[1] == max_shipments]
        
        return tuple(vessels)

    # Which ports have the most shipments -> tuple[Port, ...]
    def ports_with_most_shipments(self) -> "tuple[Port, ...]":
        """
        Retourneer de havens met de meeste zendingen.
        """
        self.cursor.execute("""
            SELECT origin, COUNT(*) as shipment_count
            FROM shipments
            GROUP BY origin
            ORDER BY shipment_count DESC, origin ASC
        """)
        port_data = self.cursor.fetchall()

        if not port_data:
            return tuple()

        max_shipments = port_data[0][1]
        ports = [Port(*self.fetch_port_by_id(data[0])) for data in port_data if data[1] == max_shipments]
        
        return tuple(ports)

    # Which ports (origin) had the first shipment? -> tuple[Port, ...]:
    # Which ports (origin) had the first shipment of a specific vessel type?  -> tuple[Port, ...]:
    def ports_with_first_shipment(self, vessel_type: str = None) -> "tuple[Port, ...]":
        """
        Retourneer de havens met de eerste zending. Optioneel filteren op scheepstype.
        """
        if vessel_type:
            self.cursor.execute("""
                SELECT origin, MIN(date)
                FROM shipments
                JOIN vessels ON shipments.vessel = vessels.imo
                WHERE vessels.type = ?
                GROUP BY origin
                ORDER BY date ASC
            """, (vessel_type,))
        else:
            self.cursor.execute("""
                SELECT origin, MIN(date)
                FROM shipments
                GROUP BY origin
                ORDER BY date ASC
            """)
        
        port_data = self.cursor.fetchall()

        if not port_data:
            return tuple()

        earliest_date = port_data[0][1]
        ports = [Port(*self.fetch_port_by_id(data[0])) for data in port_data if data[1] == earliest_date]
        
        return tuple(ports)

    # Which ports (origin) had the latest shipment? -> tuple[Port, ...]:
    # Which ports (origin) had the latetst shipment of a specific vessel type? -> tuple[Port, ...]:
    def ports_with_latest_shipment(self, vessel_type: str = None) -> "tuple[Port, ...]":
        """
        Retourneer de havens met de laatste zending. Optioneel filteren op scheepstype.
        """
        if vessel_type:
            self.cursor.execute("""
                SELECT origin, MAX(date)
                FROM shipments
                JOIN vessels ON shipments.vessel = vessels.imo
                WHERE vessels.type = ?
                GROUP BY origin
                ORDER BY date DESC
            """, (vessel_type,))
        else:
            self.cursor.execute("""
                SELECT origin, MAX(date)
                FROM shipments
                GROUP BY origin
                ORDER BY date DESC
            """)

        port_data = self.cursor.fetchall()

        if not port_data:
            return tuple()

        latest_date = port_data[0][1]
        ports = [Port(*self.fetch_port_by_id(data[0])) for data in port_data if data[1] == latest_date]
        
        # Reverse the order to match the expected output order
        ports.reverse()

        return tuple(ports)

    # Which vessels have docked port Z between period X and Y? -> tuple[Vessel, ...]
    # Based on given parameter `to_csv = True` should generate CSV file as  `Vessels docking Port Z between X and Y.csv`
    # example: `Vessels docking Port MZPOL between 2023-03-01 and 2023-06-01.csv`
    # date input always in format: YYYY-MM-DD
    # otherwise it should just return the value as tuple(Vessels, ...)
    # CSV example (this are also the headers):
    #   imo, mmsi, name, country, type, build, gross, netto, length, beam
    def vessels_that_docked_port_between(self, port: Port, start: date, end: date, to_csv: bool = False) -> "tuple[Vessel, ...]":
        """
        Retourneer de schepen die tussen de gegeven data in een specifieke haven hebben aangemeerd. Optioneel een CSV-bestand genereren.
        """
        start_date = start.strftime("%Y-%m-%d")
        end_date = end.strftime("%Y-%m-%d")

        self.cursor.execute("""
            SELECT DISTINCT vessels.*
            FROM shipments
            JOIN vessels ON shipments.vessel = vessels.imo
            WHERE (origin = ? OR destination = ?)
            AND date BETWEEN ? AND ?
            ORDER BY vessels.imo  -- Ensure ordering by IMO number
        """, (port.id, port.id, start_date, end_date))
        
        vessels_data = self.cursor.fetchall()

        if to_csv:
            csv_filename = f"Vessels docking Port {port.id} between {start_date} and {end_date}.csv"
            with open(csv_filename, 'w', newline='') as csvfile:
                fieldnames = ["imo", "mmsi", "name", "country", "type", "build", "gross", "netto", "length", "beam"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for vessel in vessels_data:
                    writer.writerow(dict(zip(fieldnames, vessel)))
            return tuple()

        return tuple(Vessel(*vessel) for vessel in vessels_data)

    # Which ports are located in country X? ->tuple[Port, ...]
    # Based on given parameter `to_csv = True` should generate CSV file as  `Ports in country X.csv`
    # example: `Ports in country Norway.csv`
    # otherwise it should just return the value as tuple(Port, ...)
    # CSV example (this are also the headers):
    #   id, code, name, city, province, country
    def ports_in_country(self, country: str, to_csv: bool = False) -> "tuple[Port, ...]":
        """
        Retourneer de havens die zich in een specifiek land bevinden. Optioneel een CSV-bestand genereren.
        """
        self.cursor.execute("SELECT * FROM ports WHERE country = ? ORDER BY id", (country,))
        ports_data = self.cursor.fetchall()

        if to_csv:
            csv_filename = f"Ports in country {country}.csv"
            with open(csv_filename, 'w', newline='') as csvfile:
                fieldnames = ["id", "code", "name", "city", "province", "country"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for port in ports_data:
                    writer.writerow(dict(zip(fieldnames, port)))
            return tuple()

        return tuple(Port(*port) for port in ports_data)

    # Which vessels are from country X? -> tuple[Vessel, ...]
    # Based on given parameter `to_csv = True` should generate CSV file as  `Vessels from country X.csv`
    # example: `Vessels from country GER.csv`
    # otherwise it should just return the value as tuple(Vessel, ...)
    # CSV example (this are also the headers):
    #   imo, mmsi, name, country, type, build, gross, netto, length, beam
    def vessels_from_country(self, country: str, to_csv: bool = False) -> "tuple[Vessel, ...]":
        """
        Retourneer de schepen die afkomstig zijn uit een specifiek land. Optioneel een CSV-bestand genereren.
        """
        self.cursor.execute("SELECT * FROM vessels WHERE country = ?", (country,))
        vessels_data = self.cursor.fetchall()

        if to_csv:
            csv_filename = f"Vessels from country {country}.csv"
            with open(csv_filename, 'w', newline='') as csvfile:
                fieldnames = ["imo", "mmsi", "name", "country", "type", "build", "gross", "netto", "length", "beam"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for vessel in vessels_data:
                    writer.writerow(dict(zip(fieldnames, vessel)))
            return tuple()

        return tuple(Vessel(*vessel) for vessel in vessels_data)
    
    def fetch_vessel_by_imo(self, imo: int):
        """
        Haal een schip op aan de hand van het IMO-nummer.
        """
        self.cursor.execute("SELECT * FROM vessels WHERE imo = ?", (imo,))
        return self.cursor.fetchone()

    def fetch_port_by_id(self, port_id: str):
        """
        Haal een haven op aan de hand van de ID.
        """
        self.cursor.execute("SELECT * FROM ports WHERE id = ?", (port_id,))
        return self.cursor.fetchone()

    def __del__(self):
        """
        Sluit de databaseverbinding wanneer de Reporter-instantie wordt verwijderd.
        """
        self.conn.close()
