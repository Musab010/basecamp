import sqlite3
from port import Port
from vessel import Vessel

database_path = 'shipments.db'

class Shipment:
    def __init__(self, id, date, cargo_weight, distance_naut, duration_hours, average_speed, origin, destination, vessel):
        self.id = id
        self.date = date
        self.cargo_weight = cargo_weight
        self.distance_naut = distance_naut
        self.duration_hours = duration_hours
        self.average_speed = average_speed
        self.origin = origin
        self.destination = destination
        self.vessel = vessel

    def get_ports(self):
        with sqlite3.connect(database_path) as conn:
            cursor = conn.cursor()
            
            # Fetch origin port details
            cursor.execute("SELECT * FROM ports WHERE id = ?", (self.origin,))
            origin_port_data = cursor.fetchone()
            if not origin_port_data:
                raise ValueError(f"No port found with ID {self.origin}")
            origin_port = Port(*origin_port_data)
            
            # Fetch destination port details
            cursor.execute("SELECT * FROM ports WHERE id = ?", (self.destination,))
            dest_port_data = cursor.fetchone()
            if not dest_port_data:
                raise ValueError(f"No port found with ID {self.destination}")
            dest_port = Port(*dest_port_data)

        return {"origin": origin_port, "destination": dest_port}

    def get_vessel(self):
        with sqlite3.connect(database_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM vessels WHERE imo = ?", (self.vessel,))
            vessel_data = cursor.fetchone()
            if not vessel_data:
                raise ValueError(f"No vessel found with IMO {self.vessel}")
            return Vessel(*vessel_data)

    def calculate_fuel_costs(self, price_per_liter, vessel):
        fuel_consumption = vessel.get_fuel_consumption(self.distance_naut)
        total_cost = self.duration_hours * fuel_consumption * price_per_liter
        return round(total_cost, 3)

    def convert_speed(self, to_format):
        conversions = {"Knts": 1.0, "Mph": 1.15078, "Kmph": 1.852}
        if to_format not in conversions:
            raise ValueError("Unsupported speed format")

        return round(self.average_speed * conversions[to_format], 6)

    def convert_distance(self, to_format):
        conversions = {"NM": 1.0, "M": 1852, "KM": 1.852, "MI": 1.15078, "YD": 2025.3718}
        if to_format not in conversions:
            raise ValueError("Unsupported distance format")

        return round(self.distance_naut * conversions[to_format], 6)

    def convert_duration(self, to_format):
        if to_format == "%D:%H":
            days = int(self.duration_hours // 24)
            hours = int(self.duration_hours % 24)
            return f"{days} days : {hours} hours"
        elif to_format == "%H":
            return f"{int(self.duration_hours)} hours"
        elif to_format == "%M":
            minutes = int(self.duration_hours * 60)
            return f"{minutes} minutes"
        else:
            raise ValueError("Unsupported duration format")

    def __repr__(self):
        attrs = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{type(self).__name__}({attrs})"