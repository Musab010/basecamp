import sqlite3
from port import Port
from vessel import Vessel

database_path = 'shipments.db'

class Shipment:
    def __init__(self, id: str, date: str, cargo_weight: int, distance_naut: float, duration_hours: float, average_speed: float, origin: str, destination: str, vessel: int):
        self.id = id
        self.date = date
        self.cargo_weight = cargo_weight
        self.distance_naut = distance_naut
        self.duration_hours = duration_hours
        self.average_speed = average_speed
        self.origin = origin
        self.destination = destination
        self.vessel = vessel

    def __repr__(self) -> str:
        return "{}({})".format(
            type(self).__name__,
            ", ".join([f"{key}={value!s}" for key, value in self.__dict__.items()])
        )

    def get_ports(self) -> dict:
        """
        Haalt de oorsprong- en bestemmingshavens op voor deze zending.
        Retourneert een woordenboek met 'origin' en 'destination' als sleutels die wijzen naar Port-instanties.
        """
        conn = sqlite3.connect(database_path)  # Verbind met de database
        cursor = conn.cursor()  # Maak een cursor-object aan om SQL-query's uit te voeren
        
        cursor.execute("SELECT * FROM ports WHERE id = ?", (self.origin,))
        origin_port_data = cursor.fetchone()  # Haal de gegevens van de oorsprongshaven op
        if origin_port_data is None:
            raise ValueError(f"Geen haven gevonden met ID {self.origin}")
        origin_port = Port(*origin_port_data)
        
        cursor.execute("SELECT * FROM ports WHERE id = ?", (self.destination,))
        destination_port_data = cursor.fetchone()  # Haal de gegevens van de bestemmingshaven op
        if destination_port_data is None:
            raise ValueError(f"Geen haven gevonden met ID {self.destination}")
        destination_port = Port(*destination_port_data)
        
        conn.close()  # Sluit de databaseverbinding
        
        return {"origin": origin_port, "destination": destination_port}

    def get_vessel(self) -> Vessel:
        """
        Haalt het schip op voor deze zending.
        Retourneert een Vessel-instantie.
        """
        conn = sqlite3.connect(database_path)  # Verbind met de database
        cursor = conn.cursor()  # Maak een cursor-object aan om SQL-query's uit te voeren
        
        cursor.execute("SELECT * FROM vessels WHERE imo = ?", (self.vessel,))
        vessel_data = cursor.fetchone()  # Haal de gegevens van het schip op
        if vessel_data is None:
            raise ValueError(f"Geen schip gevonden met IMO {self.vessel}")
        vessel = Vessel(*vessel_data)
        
        conn.close()  # Sluit de databaseverbinding
        
        return vessel

    def calculate_fuel_costs(self, price_per_liter: float, vessel: Vessel) -> float:
        """
        Berekent de totale brandstofkosten voor deze zending.
        Retourneert de totale kosten afgerond naar 3 decimalen.
        """
        fuel_consumption = vessel.get_fuel_consumption(self.distance_naut)  # Haal het brandstofverbruik op
        total_cost = self.duration_hours * fuel_consumption * price_per_liter  # Bereken de totale brandstofkosten
        
        return round(total_cost, 3)  # Rond de kosten af naar 3 decimalen

    def convert_speed(self, to_format: str) -> float:
        """
        Converteert de gemiddelde snelheid van deze zending naar het gespecificeerde formaat.
        Ondersteunde formaten: 'Knts' (knopen), 'Mph' (mijl per uur), 'Kmph' (kilometer per uur).
        """
        conversion_factors = {
            "Knts": 1.0,
            "Mph": 1.15078,
            "Kmph": 1.852
        }

        if to_format not in conversion_factors:
            raise ValueError("Niet-ondersteund formaat voor snelheidsconversie")

        converted_speed = self.average_speed * conversion_factors[to_format]  # Converteer de snelheid
        return round(converted_speed, 6)  # Rond de geconverteerde snelheid af naar 6 decimalen

    def convert_distance(self, to_format: str) -> float:
        """
        Converteert de afstand van deze zending naar het gespecificeerde formaat.
        Ondersteunde formaten: 'NM' (zeemijlen), 'M' (meters), 'KM' (kilometers), 'MI' (mijlen), 'YD' (yards).
        """
        conversion_factors = {
            "NM": 1.0, 
            "M": 1852,
            "KM": 1.852,
            "MI": 1.15078,
            "YD": 2025.3718
        }

        if to_format not in conversion_factors:
            raise ValueError("Niet-ondersteund formaat voor afstandsconversie")

        converted_distance = self.distance_naut * conversion_factors[to_format]  # Converteer de afstand
        return round(converted_distance, 6)  # Rond de geconverteerde afstand af naar 6 decimalen

    def convert_duration(self, to_format: str) -> str:
        """
        Converteert de duur van deze zending naar het gespecificeerde formaat.
        Ondersteunde formaten: '%D:%H' voor dagen en uren, '%H' voor uren, '%M' voor minuten.
        """
        if to_format == "%D:%H":
            days = int(self.duration_hours // 24)
            hours = int(self.duration_hours % 24)
            return f"{days} dagen : {hours} uren"
        elif to_format == "%H":
            return f"{int(self.duration_hours)} uren"
        elif to_format == "%M":
            minutes = int(self.duration_hours * 60)
            return f"{minutes} minuten"
        else:
            raise ValueError("Niet-ondersteund formaat voor tijdsduurconversie")
            