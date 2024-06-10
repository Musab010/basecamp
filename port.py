import sqlite3

database_path = 'shipments.db'

class Port:
    def __init__(self, id: str, code: int, name: str, city: str, province: str, country: str):
        # Initialize the attributes of the port
        self.id = id
        self.code = code
        self.name = name
        self.city = city
        self.province = province
        self.country = country

    def get_shipments(self) -> tuple:
        # Connect to the database
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Execute a SQL query to find shipments where this port is the origin or destination
        query = """
            SELECT id FROM shipments WHERE origin = ? OR destination = ?
        """
        cursor.execute(query, (self.id, self.id))
        
        # Fetch all results and close the database connection
        shipments = cursor.fetchall()
        conn.close()

        # Convert the results to a tuple of shipment IDs
        shipment_ids = tuple(shipment[0] for shipment in shipments)
        return shipment_ids
    
    def __repr__(self) -> str:
        # Return a string representation of the Port object for readable output
        attributes = ", ".join([f"{key}={value!s}" for key, value in self.__dict__.items()])
        return f"{type(self).__name__}({attributes})"