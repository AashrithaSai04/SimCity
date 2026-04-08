"""Data generation simulator for SimCity"""

import time
import random
import requests
import logging
import argparse
from datetime import datetime
from config import (
    SCENARIOS, DEFAULT_MULTIPLIERS, TRAFFIC_ZONES, HOSPITAL_FACILITIES,
    WAREHOUSES, TRAFFIC_SPEED_RANGE, HOSPITAL_OCCUPANCY_RANGE, 
    ER_WAIT_RANGE, INVENTORY_RANGE, DELIVERY_ETA_RANGE, TICK_INTERVAL,
    SIMULATOR_URL
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Simulator:
    def __init__(self, scenario: str = None):
        self.scenario = scenario
        self.multipliers = SCENARIOS.get(scenario, DEFAULT_MULTIPLIERS) if scenario else DEFAULT_MULTIPLIERS
        self.tick_count = 0
        self.backend_url = SIMULATOR_URL
    
    def generate_traffic(self):
        """Generate traffic snapshot"""
        base_speed = random.uniform(*TRAFFIC_SPEED_RANGE)
        base_congestion = random.uniform(0.2, 0.9)
        
        speed = base_speed * self.multipliers.get("traffic_speed", 1.0)
        congestion = min(1.0, base_congestion * self.multipliers.get("traffic_congestion", 1.0))
        
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metadata": {
                "domain": "traffic",
                "zone": random.choice(TRAFFIC_ZONES)
            },
            "data": {
                "speed": round(speed, 2),
                "congestion_score": round(congestion, 2),
                "incident_flag": congestion > 0.8
            }
        }
    
    def generate_hospital(self):
        """Generate hospital snapshot"""
        base_occupancy = random.uniform(*HOSPITAL_OCCUPANCY_RANGE)
        base_er_wait = random.uniform(*ER_WAIT_RANGE)
        
        occupancy = min(100, base_occupancy * self.multipliers.get("hospital_surge", 1.0))
        er_wait = base_er_wait * self.multipliers.get("hospital_surge", 1.0)
        
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metadata": {
                "domain": "hospital",
                "facility_id": random.choice(HOSPITAL_FACILITIES)
            },
            "data": {
                "bed_occupancy": round(occupancy, 2),
                "er_wait_time_minutes": int(er_wait),
                "critical_status": occupancy > 90
            }
        }
    
    def generate_supply(self):
        """Generate supply chain snapshot"""
        base_inventory = random.uniform(*INVENTORY_RANGE)
        base_eta = random.uniform(*DELIVERY_ETA_RANGE)
        
        inventory = max(0, base_inventory - (100 - base_inventory) * self.multipliers.get("inventory_drain", 1.0))
        eta = base_eta * self.multipliers.get("delivery_delay", 1.0)
        
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metadata": {
                "domain": "supply_chain",
                "warehouse": random.choice(WAREHOUSES)
            },
            "data": {
                "inventory_level": round(inventory, 2),
                "delivery_eta_hours": round(eta, 1),
                "stock_critical": inventory < 20
            }
        }
    
    def send_data(self, traffic: dict, hospital: dict, supply: dict):
        """Send data to backend"""
        try:
            response = requests.post(
                f"{self.backend_url}/ingest",
                json=[traffic, hospital, supply],
                timeout=5
            )
            if response.status_code == 200:
                return True
            else:
                logger.warning(f"⚠️  Backend returned {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Cannot connect to backend at {self.backend_url}")
            return False
        except Exception as e:
            logger.error(f"❌ Error sending data: {e}")
            return False
    
    def run(self, duration: int = None):
        """Run simulation loop"""
        logger.info(f"🚀 Starting simulator (Scenario: {self.scenario or 'NORMAL'})")
        logger.info(f"📊 Event Multipliers: {self.multipliers}")
        
        start_time = time.time()
        
        try:
            while True:
                if duration and (time.time() - start_time) > duration:
                    logger.info(f"✅ Simulation completed after {self.tick_count} ticks")
                    break
                
                self.tick_count += 1
                
                # Generate data
                traffic = self.generate_traffic()
                hospital = self.generate_hospital()
                supply = self.generate_supply()
                
                # Send to backend
                success = self.send_data(traffic, hospital, supply)
                
                if success:
                    logger.info(
                        f"✅ Tick {self.tick_count} | "
                        f"Traffic: {traffic['data']['speed']:.1f} km/h, "
                        f"Hospital: {hospital['data']['bed_occupancy']:.1f}%, "
                        f"Supply: {supply['data']['inventory_level']:.1f}%"
                    )
                else:
                    logger.warning(f"⚠️  Tick {self.tick_count} - Failed to send data")
                
                # Sleep 5-10 seconds
                sleep_time = random.uniform(5, TICK_INTERVAL)
                time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            logger.info(f"🛑 Simulator stopped by user after {self.tick_count} ticks")
        except Exception as e:
            logger.error(f"❌ Simulator error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SimCity Data Simulator")
    parser.add_argument(
        "--scenario",
        type=str,
        choices=["flood", "earthquake", "fire", "normal"],
        default="normal",
        help="Disaster scenario to simulate"
    )
    parser.add_argument(
        "--duration",
        type=int,
        help="Simulation duration in seconds"
    )
    args = parser.parse_args()
    
    sim = Simulator(scenario=None if args.scenario == "normal" else args.scenario)
    sim.run(duration=args.duration)