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

    def __repr__(self) -> str:
        return "{}({})".format(
            type(self).__name__,
            ", ".join([f"{key}={value!s}" for key, value in self.__dict__.items()])
        )

    def get_shipments(self) -> list:
        """
        Haalt alle zendingen op die aan dit schip zijn gekoppeld.
        Retourneert een lijst met zending-ID's.
        """
        conn = sqlite3.connect(database_path)  # Verbind met de database
        cursor = conn.cursor()  # Maak een cursor-object aan om SQL-query's uit te voeren
        
        cursor.execute("""
            SELECT id FROM shipments WHERE vessel = ?
        """, (self.imo,))  # Voer een query uit om alle zending-ID's op te halen voor dit schip
        
        shipments = cursor.fetchall()  # Haal alle resultaten op
        conn.close()  # Sluit de databaseverbinding
        
        return [shipment[0] for shipment in shipments]  # Converteer de zending-ID's naar een lijst en retourneer deze

    def get_fuel_consumption(self, distance: float) -> float:
        """
        Berekent het brandstofverbruik op basis van de afstand en de efficiëntie van het schip.
        Retourneert het berekende brandstofverbruik afgerond op 5 decimalen.
        """
        # Efficiëntiewaarden op basis van het type schip
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

        efficiency = efficiency_values.get(self.type, 0.4)  # Haal de efficiëntiewaarde op voor dit scheepstype
        fuel_consumption = efficiency * (self.gross / self.netto) * distance  # Bereken het brandstofverbruik
        
        return round(fuel_consumption, 5)  # Rond het brandstofverbruik af naar 5 decimalen en retourneer het