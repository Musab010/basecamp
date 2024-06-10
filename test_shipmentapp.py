import unittest
from shipment import Shipment
from vessel import Vessel
from port import Port

# Test to check if duration is converted correctly based on the given arguments
def test_convert_duration():
    shipment = Shipment(
        id="SHIP-456",
        date="2023-05-15",
        cargo_weight=20000,
        distance_naut=7500,
        duration_hours=150,
        average_speed=15,
        origin="MYTPP",
        destination="TRGEM",
        vessel=9913547
    )

    # %D:%H
    duration_dh = shipment.convert_duration("%D:%H")
    assert duration_dh == "6 days : 6 hours", f"Expected '6 days : 6 hours', got {duration_dh}"

    # %H
    duration_h = shipment.convert_duration("%H")
    assert duration_h == "150 hours", f"Expected '150 hours', got {duration_h}"

    # %M
    duration_m = shipment.convert_duration("%M")
    assert duration_m == "9000 minutes", f"Expected '9000 minutes', got {duration_m}"

    # Invalid format should raise ValueError
    try:
        shipment.convert_duration("invalid")
        assert False, "Expected ValueError for invalid format"
    except ValueError:
        pass

# Test to check if distance is converted correctly based on the given arguments
def test_convert_distance():
    shipment = Shipment(
        id="SHIP-456",
        date="2023-05-15",
        cargo_weight=20000,
        distance_naut=7500,
        duration_hours=150,
        average_speed=15,
        origin="MYTPP",
        destination="TRGEM",
        vessel=9913547
    )

    # NM = Nautical Miles
    distance_nm = shipment.convert_distance("NM")
    assert abs(distance_nm - 7500) < 1e-6, f"Expected 7500, got {distance_nm}"

    # M = Meters
    distance_m = shipment.convert_distance("M")
    assert abs(distance_m - (7500 * 1852)) < 1e-6, f"Expected {7500 * 1852}, got {distance_m}"

    # KM = Kilometers
    distance_km = shipment.convert_distance("KM")
    assert abs(distance_km - (7500 * 1.852)) < 1e-6, f"Expected {7500 * 1.852}, got {distance_km}"

    # MI = Miles
    distance_mi = shipment.convert_distance("MI")
    assert abs(distance_mi - (7500 * 1.15078)) < 1e-6, f"Expected {7500 * 1.15078}, got {distance_mi}"

    # YD = Yards
    distance_yd = shipment.convert_distance("YD")
    assert abs(distance_yd - (7500 * 2025.3718)) < 1e-6, f"Expected {7500 * 2025.3718}, got {distance_yd}"

    # ValueError check
    try:
        shipment.convert_distance("invalid")
        assert False, "Expected ValueError for invalid format"
    except ValueError:
        pass

# Test to check if speed is converted correctly based on the given arguments
def test_convert_speed():
    shipment = Shipment(
        id="SHIP-456",
        date="2023-05-15",
        cargo_weight=20000,
        distance_naut=7500,
        duration_hours=150,
        average_speed=15,
        origin="MYTPP",
        destination="TRGEM",
        vessel=9913547
    )

    # Knts = Knots
    speed_knts = shipment.convert_speed("Knts")
    assert abs(speed_knts - 15) < 1e-6, f"Expected 15, got {speed_knts}"

    # Mph = Miles per hour
    speed_mph = shipment.convert_speed("Mph")
    assert abs(speed_mph - (15 * 1.15078)) < 1e-6, f"Expected {15 * 1.15078}, got {speed_mph}"

    # Kmph = Kilometers per hour
    speed_kmph = shipment.convert_speed("Kmph")
    assert abs(speed_kmph - (15 * 1.852)) < 1e-6, f"Expected {15 * 1.852}, got {speed_kmph}"

    # ValueError check
    try:
        shipment.convert_speed("invalid")
        assert False, "Expected ValueError for invalid format"
    except ValueError:
        pass

# Test to check if the fuel consumption is calculated correctly based on the distance
def test_get_fuel_consumption():
    vessel = Vessel(
        imo=9913547,
        mmsi=477736400,
        name="TIGER LONGKOU",
        country="Hong Kong",
        type="Deck Cargo Ship",
        build=2022,
        gross=23040,
        netto=26200,
        length=192,
        beam=37
    )

    distance = 7500  # Sample distance
    fuel_consumption = vessel.get_fuel_consumption(distance)
    expected_consumption = 0.4 * (23040 / 26200) * 7500  # Efficiency for "Deck Cargo Ship" is 0.4
    assert abs(fuel_consumption - expected_consumption) < 1e-5, f"Expected {expected_consumption}, got {fuel_consumption}"

# Test to check if the fuel costs are calculated correctly based on the price per liter
def test_calculate_fuel_costs():
    vessel = Vessel(
        imo=9913547,
        mmsi=477736400,
        name="TIGER LONGKOU",
        country="Hong Kong",
        type="Deck Cargo Ship",
        build=2022,
        gross=23040,
        netto=26200,
        length=192,
        beam=37
    )

    shipment = Shipment(
        id="SHIP-456",
        date="2023-05-15",
        cargo_weight=20000,
        distance_naut=7500,
        duration_hours=150,
        average_speed=15,
        origin="MYTPP",
        destination="TRGEM",
        vessel=vessel.imo
    )

    price_per_liter = 2.0  # Assume $2.0 per liter
    fuel_costs = shipment.calculate_fuel_costs(price_per_liter, vessel)
    fuel_consumption = vessel.get_fuel_consumption(shipment.distance_naut)
    expected_costs = shipment.duration_hours * fuel_consumption * price_per_liter
    assert abs(fuel_costs - round(expected_costs, 3)) < 1e-3, f"Expected {round(expected_costs, 3)}, got {fuel_costs}"

# Test to check if the returned ports are correct
def test_get_ports():
    shipment = Shipment(
        id="SHIP-456",
        date="2023-05-15",
        cargo_weight=20000,
        distance_naut=7500,
        duration_hours=150,
        average_speed=15,
        origin="MYTPP",
        destination="TRGEM",
        vessel=9913547
    )

    ports = shipment.get_ports()

    # Amount check
    assert len(ports) == 2, f"Expected 2 ports, got {len(ports)}"

    # Keys check
    assert "origin" in ports, "Expected 'origin' key in ports"
    assert "destination" in ports, "Expected 'destination' key in ports"

    # Values check
    assert ports["origin"].id == "MYTPP", f"Expected 'MYTPP', got {ports['origin'].id}"
    assert ports["destination"].id == "TRGEM", f"Expected 'TRGEM', got {ports['destination'].id}"

# Test if the returned shipments contain the required shipment(s)
def test_get_shipments():
    port = Port("MYTPP", 55750, "Tanjung Pelepas", "Tanjung Pelepas", "Johor", "Malaysia")
    shipments = port.get_shipments()

    # We assume get_shipments returns the IDs of shipments
    assert "SHIP-456" not in shipments, f"Expected 'SHIP-456' not to be in shipments, got {shipments}"  # since this ID is not in the db

if __name__ == '__main__':
    # Call each test function individually
    test_convert_duration()
    test_convert_distance()
    test_convert_speed()
    test_get_fuel_consumption()
    test_calculate_fuel_costs()
    test_get_ports()
    test_get_shipments()

    print("All tests passed!")
