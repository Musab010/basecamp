import unittest
from shipment import Shipment
from vessel import Vessel
from port import Port

class TestShipment(unittest.TestCase):

    def setUp(self):
        self.shipment = Shipment(
            id="SHIP-TR001",
            date="2023-05-15",
            cargo_weight=25000,
            distance_naut=8500,
            duration_hours=170,
            average_speed=16,
            origin="TRIST",
            destination="TRIZM",
            vessel=1234567
        )
        self.vessel = Vessel(
            imo=1234567,
            mmsi=271000123,
            name="ISTANBUL PRIDE",
            country="Turkey",
            type="Container Ship",
            build=2019,
            gross=50000,
            netto=30000,
            length=250,
            beam=40
        )

    def test_convert_duration(self):
        """Test duration conversion for various formats."""
        self.assertEqual(self.shipment.convert_duration("%D:%H"), "7 days : 2 hours")
        self.assertEqual(self.shipment.convert_duration("%H"), "170 hours")
        self.assertEqual(self.shipment.convert_duration("%M"), "10200 minutes")

        with self.assertRaises(ValueError):
            self.shipment.convert_duration("invalid")

    def test_convert_distance(self):
        """Test distance conversion for various units."""
        self.assertAlmostEqual(self.shipment.convert_distance("NM"), 8500, places=6)
        self.assertAlmostEqual(self.shipment.convert_distance("M"), 8500 * 1852, places=6)
        self.assertAlmostEqual(self.shipment.convert_distance("KM"), 8500 * 1.852, places=6)
        self.assertAlmostEqual(self.shipment.convert_distance("MI"), 8500 * 1.15078, places=6)
        self.assertAlmostEqual(self.shipment.convert_distance("YD"), 8500 * 2025.3718, places=6)

        with self.assertRaises(ValueError):
            self.shipment.convert_distance("invalid")

    def test_convert_speed(self):
        """Test speed conversion for various formats."""
        self.assertAlmostEqual(self.shipment.convert_speed("Knts"), 16, places=6)
        self.assertAlmostEqual(self.shipment.convert_speed("Mph"), 16 * 1.15078, places=6)
        self.assertAlmostEqual(self.shipment.convert_speed("Kmph"), 16 * 1.852, places=6)

        with self.assertRaises(ValueError):
            self.shipment.convert_speed("invalid")

    def test_get_fuel_consumption(self):
        """Test fuel consumption calculation based on distance."""
        distance = 8500 
        expected_consumption = 0.3 * (50000 / 30000) * distance  # Efficiency for "Container Ship" is 0.3
        self.assertAlmostEqual(self.vessel.get_fuel_consumption(distance), expected_consumption, places=5)

    def test_calculate_fuel_costs(self):
        """Test calculation of fuel costs based on price per liter."""
        price_per_liter = 2.5
        fuel_consumption = self.vessel.get_fuel_consumption(self.shipment.distance_naut)
        expected_costs = self.shipment.duration_hours * fuel_consumption * price_per_liter
        self.assertAlmostEqual(self.shipment.calculate_fuel_costs(price_per_liter, self.vessel), round(expected_costs, 3), places=3)

    def test_get_ports(self):
        """Test retrieval of origin and destination ports."""
        ports = self.shipment.get_ports()

        self.assertEqual(len(ports), 2)
        self.assertIn("origin", ports)
        self.assertIn("destination", ports)
        self.assertEqual(ports["origin"].id, "TRIST")
        self.assertEqual(ports["destination"].id, "TRIZM")

class TestPort(unittest.TestCase):

    def test_get_shipments(self):
        """Test retrieval of shipments for a specific port."""
        port = Port("TRIST", 34000, "Istanbul", "Istanbul", "Marmara", "Turkey")
        shipments = port.get_shipments()

        # We assume get_shipments returns the IDs of shipments
        self.assertNotIn("SHIP-TR001", shipments, "Expected 'SHIP-TR001' not to be in shipments since this ID is not in the db")

if __name__ == '__main__':
    # Run all tests
    unittest.main()

