import sqlite3
import csv
from datetime import date
from vessel import Vessel
from port import Port
from shipment import Shipment

DATABASE_PATH = "shipments.db"

class Reporter:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.cursor = self.conn.cursor()

    def total_amount_of_vessels(self) -> int:
        """Return the total number of vessels in the database."""
        self.cursor.execute("SELECT COUNT(*) FROM vessels")
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def longest_shipment(self) -> Shipment:
        """Find and return the shipment with the longest distance."""
        self.cursor.execute("SELECT * FROM shipments ORDER BY distance_naut DESC LIMIT 1")
        shipment_data = self.cursor.fetchone()
        return Shipment(*shipment_data) if shipment_data else None

    def longest_and_shortest_vessels(self) -> "tuple[Vessel, Vessel]":
        """Return the longest and shortest vessels by length."""
        self.cursor.execute("SELECT * FROM vessels ORDER BY length DESC LIMIT 1")
        longest_vessel_data = self.cursor.fetchone()
        
        self.cursor.execute("SELECT * FROM vessels ORDER BY length ASC LIMIT 1")
        shortest_vessel_data = self.cursor.fetchone()
        
        longest_vessel = Vessel(*longest_vessel_data) if longest_vessel_data else None
        shortest_vessel = Vessel(*shortest_vessel_data) if shortest_vessel_data else None

        return (longest_vessel, shortest_vessel)

    def widest_and_smallest_vessels(self) -> "tuple[Vessel, Vessel]":
        """Return the widest and smallest vessels by beam."""
        self.cursor.execute("SELECT * FROM vessels ORDER BY beam DESC LIMIT 1")
        widest_vessel_data = self.cursor.fetchone()
        
        self.cursor.execute("SELECT * FROM vessels ORDER BY beam ASC LIMIT 1")
        smallest_vessel_data = self.cursor.fetchone()
        
        widest_vessel = Vessel(*widest_vessel_data) if widest_vessel_data else None
        smallest_vessel = Vessel(*smallest_vessel_data) if smallest_vessel_data else None

        return (widest_vessel, smallest_vessel)

    def vessels_with_the_most_shipments(self) -> "tuple[Vessel, ...]":
        """Find and return the vessels with the most shipments."""
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

    def ports_with_most_shipments(self) -> "tuple[Port, ...]":
        """Return the ports with the most shipments."""
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

    def ports_with_first_shipment(self, vessel_type: str = None) -> "tuple[Port, ...]":
        """Return the ports with the first shipment, optionally filtered by vessel type."""
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

    def ports_with_latest_shipment(self, vessel_type: str = None) -> "tuple[Port, ...]":
        """Return the ports with the latest shipment, optionally filtered by vessel type."""
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

    def vessels_that_docked_port_between(self, port: Port, start: date, end: date, to_csv: bool = False) -> "tuple[Vessel, ...]":
        """Find vessels that docked at a specific port between two dates and optionally export to CSV."""
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
            self.export_to_csv(vessels_data, csv_filename, ["imo", "mmsi", "name", "country", "type", "build", "gross", "netto", "length", "beam"])
            return tuple()

        return tuple(Vessel(*vessel) for vessel in vessels_data)

    def ports_in_country(self, country: str, to_csv: bool = False) -> "tuple[Port, ...]":
        """Find ports located in a specific country and optionally export to CSV."""
        self.cursor.execute("SELECT * FROM ports WHERE country = ? ORDER BY id", (country,))
        ports_data = self.cursor.fetchall()

        if to_csv:
            csv_filename = f"Ports in country {country}.csv"
            self.export_to_csv(ports_data, csv_filename, ["id", "code", "name", "city", "province", "country"])
            return tuple()

        return tuple(Port(*port) for port in ports_data)

    def vessels_from_country(self, country: str, to_csv: bool = False) -> "tuple[Vessel, ...]":
        """Find vessels from a specific country and optionally export to CSV."""
        self.cursor.execute("SELECT * FROM vessels WHERE country = ?", (country,))
        vessels_data = self.cursor.fetchall()

        if to_csv:
            csv_filename = f"Vessels from country {country}.csv"
            self.export_to_csv(vessels_data, csv_filename, ["imo", "mmsi", "name", "country", "type", "build", "gross", "netto", "length", "beam"])
            return tuple()

        return tuple(Vessel(*vessel) for vessel in vessels_data)
    
    def fetch_vessel_by_imo(self, imo: int):
        """Helper method to fetch vessel details by IMO number."""
        self.cursor.execute("SELECT * FROM vessels WHERE imo = ?", (imo,))
        return self.cursor.fetchone()

    def fetch_port_by_id(self, port_id: str):
        """Helper method to fetch port details by ID."""
        self.cursor.execute("SELECT * FROM ports WHERE id = ?", (port_id,))
        return self.cursor.fetchone()

    def export_to_csv(self, data: list, filename: str, fieldnames: list):
        """Export data to a CSV file."""
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(dict(zip(fieldnames, row)))

    def __del__(self):
        """Ensure the database connection is closed."""
        self.conn.close()