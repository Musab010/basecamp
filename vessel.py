import sqlite3

database_path = 'shipments.db'

class Vessel:
    def __init__(self, imo: int, mmsi: int, name: str, country: str, type: str, build: int, gross: int, netto: int, length: int, beam: int):
        self.imo = imo
        self.mmsi = mmsi
        self.name = name
        self.country = country
        self.type = type
        self.build = build
        self.gross = gross
        self.netto = netto
        self.length = length
        self.beam = beam

    def get_shipments(self) -> list:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Query to find all shipments for this vessel
        cursor.execute("SELECT id FROM shipments WHERE vessel = ?", (self.imo,))
        shipments = cursor.fetchall()

        conn.close()  # Close the database connection

        # Extract the shipment IDs from the query results
        return [shipment_id for (shipment_id,) in shipments]

    def get_fuel_consumption(self, distance: float) -> float:
        # Define efficiency values for different vessel types
        efficiency_values = {
            "Aggregates Carrier": 0.4,
            "Bulk Carrier": 0.35,
            "Bulk/Oil Carrier": 0.35,
            "Cement Carrier": 0.4,
            "Container Ship": 0.3,
            "Deck Cargo Ship": 0.4,
            "General Cargo Ship": 0.4,
            "Heavy Load Carrier": 0.4,
            "Landing Craft": 0.4,
            "Nuclear Fuel Carrier": 0.35,
            "Palletised Cargo Ship": 0.4,
            "Passenger/Container Ship": 0.3,
            "Ro-Ro Cargo Ship": 0.4,
            "Self Discharging Bulk Carrier": 0.35,
            "Vehicles Carrier": 0.35,
            "Wood Chips Carrier": 0.4
        }

        # Fetch the efficiency value for this vessel's type, default to 0.4 if not found
        efficiency = efficiency_values.get(self.type, 0.4)

        # Calculate fuel consumption based on efficiency, gross tonnage, and net tonnage
        fuel_consumption = efficiency * (self.gross / self.netto) * distance

        return round(fuel_consumption, 5)
    
    def __repr__(self) -> str:
        return f"{type(self).__name__}({', '.join(f'{key}={value!s}' for key, value in self.__dict__.items())})"