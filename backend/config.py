"""Configuration and event multipliers for SimCity"""

# Event multipliers for disaster scenarios
SCENARIOS = {
    "flood": {
        "traffic_speed": 0.2,
        "traffic_congestion": 2.5,
        "hospital_surge": 3.0,
        "inventory_drain": 2.0,
        "delivery_delay": 1.8
    },
    "earthquake": {
        "traffic_speed": 0.15,
        "traffic_congestion": 3.5,
        "hospital_surge": 4.0,
        "inventory_drain": 1.5,
        "delivery_delay": 2.5
    },
    "fire": {
        "traffic_speed": 0.25,
        "traffic_congestion": 2.0,
        "hospital_surge": 2.5,
        "inventory_drain": 2.5,
        "delivery_delay": 1.6
    }
}

# Default multipliers (normal conditions)
DEFAULT_MULTIPLIERS = {
    "traffic_speed": 1.0,
    "traffic_congestion": 1.0,
    "hospital_surge": 1.0,
    "inventory_drain": 1.0,
    "delivery_delay": 1.0
}

# Threshold values for alerts
THRESHOLDS = {
    "hospital_occupancy": 90,  # %
    "traffic_congestion": 0.85,  # 0-1 scale
    "supply_inventory": 20,  # %
    "er_wait_time": 120  # minutes
}

# Zones and facilities
TRAFFIC_ZONES = ["downtown", "suburban", "highway"]
HOSPITAL_FACILITIES = ["HOSPITAL_001", "HOSPITAL_002", "HOSPITAL_003"]
WAREHOUSES = ["WH_NORTH", "WH_SOUTH", "WH_CENTRAL"]

# Data generation ranges
TRAFFIC_SPEED_RANGE = (30, 80)  # km/h
HOSPITAL_OCCUPANCY_RANGE = (50, 85)  # %
ER_WAIT_RANGE = (15, 120)  # minutes
INVENTORY_RANGE = (60, 95)  # %
DELIVERY_ETA_RANGE = (4, 24)  # hours

# Simulation timing
TICK_INTERVAL = 7  # seconds
SIMULATOR_URL = "http://localhost:8000/ingest"