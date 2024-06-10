import sqlite3

database_path = 'shipments.db' 

class Port:
    def __init__(self, id: str, code: int, name: str, city: str, province: str, country: str):
        self.id = id
        self.code = code
        self.name = name
        self.city = city
        self.province = province
        self.country = country

    def __repr__(self) -> str:
        return "{}({})".format(
            type(self).__name__,
            ", ".join([f"{key}={value!s}" for key, value in self.__dict__.items()])
        )

    def get_shipments(self) -> tuple:
        """
        Haalt alle zendingen op waar deze haven ofwel de oorsprong ofwel de bestemming is.
        Retourneert een tuple van zending-ID's.
        """
        conn = sqlite3.connect(database_path)  # Verbinding maken met de database
        cursor = conn.cursor()  # Een cursor-object aanmaken om SQL-query's uit te voeren
        
        cursor.execute("""
            SELECT id FROM shipments WHERE origin = ? OR destination = ?
        """, (self.id, self.id))  # Query uitvoeren om zending-ID's op te halen waar deze haven de oorsprong of bestemming is
        
        shipments = cursor.fetchall()  # Alle resultaten ophalen
        conn.close()  # De databaseverbinding sluiten
        
        return tuple([shipment[0] for shipment in shipments])  # De zending-ID's omzetten naar een tuple en retourneren
